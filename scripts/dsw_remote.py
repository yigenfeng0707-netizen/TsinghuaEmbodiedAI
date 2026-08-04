"""
DSW 远程执行工具模块（基于已验证的 JupyterLab REST API + WebSocket 方案）

提供：
- ensure_chrome_with_cdp(): 确保 Chrome 以 CDP 模式运行（Junction profile）
- get_dsw_page(): 获取 DSW JupyterLab 页面（Playwright 接管）
- execute_via_jupyter_api(): 执行 Python 代码，返回输出
- run_shell(): 执行 shell 命令（subprocess.run 包装）
- run_long_task(): nohup 后台执行长任务，轮询日志
- download_file(): 通过 JupyterLab Contents API 下载文件

使用方式：
    from dsw_remote import DswRemote
    dsw = DswRemote()
    await dsw.connect()
    out = await dsw.run_shell("nvidia-smi")
    print(out)
"""
import asyncio
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Optional


# ============== 配置 ==============
DSW_URL = os.environ.get(
    "DSW_URL",
    "https://dsw-gateway-cn-hangzhou.data.aliyun.com/dsw-XXXXX/lab",
)
JUNCTION_PATH = os.environ.get(
    "CHROME_CDP_PROFILE",
    str(Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "UserData_CDP"),
)
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Windows 默认路径
CDP_PORT = 9222
TEMP_DIR = Path(os.environ.get("DSW_REMOTE_TEMP", str(Path(__file__).resolve().parents[1] / ".trae" / "temp")))
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def ensure_chrome_with_cdp() -> bool:
    """确保 Chrome 以 CDP 模式运行（Junction profile，保留真实登录态）"""
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=3)
        print("[Chrome] CDP 已就绪（复用现有实例）")
        return True
    except Exception:
        pass

    if os.environ.get("DSW_REMOTE_KILL_CHROME") == "1":
        print("[Chrome] 杀掉残留 Chrome 进程...")
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
        time.sleep(2)
    else:
        print("[Chrome] CDP 未就绪；将启动独立 CDP 窗口（不强杀现有 Chrome）")

    if not os.path.exists(JUNCTION_PATH):
        print(f"[Junction] 创建: {JUNCTION_PATH}")
        target = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        subprocess.run(
            ["powershell", "-Command",
             f'New-Item -ItemType Junction -Path "{JUNCTION_PATH}" '
             f'-Target "{target}" -Force'],
            capture_output=True
        )

    print(f"[Chrome] 启动（Junction + CDP port {CDP_PORT}）...")
    subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={JUNCTION_PATH}",
        "--no-first-run",
        "--no-default-browser-check",
        "--restore-last-session",
        "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for i in range(20):
        time.sleep(2)
        try:
            resp = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=3)
            data = json.loads(resp.read())
            print(f"[Chrome] CDP 就绪: {data.get('Browser')}")
            return True
        except Exception:
            if i % 3 == 0:
                print(f"  等待 CDP... ({i+1}/20)")
    return False


class DswRemote:
    """DSW 远程执行器：基于 JupyterLab REST API + WebSocket"""

    def __init__(self, dsw_url: str = DSW_URL):
        self.dsw_url = dsw_url
        self.browser = None
        self.context = None
        self.page = None
        self._playwright = None

    async def connect(self) -> bool:
        """连接 DSW：确保 Chrome CDP + Playwright 接管 + 找到/创建 DSW 页面 + 登录态验证"""
        from playwright.async_api import async_playwright

        if not ensure_chrome_with_cdp():
            raise RuntimeError("Chrome CDP 启动失败")

        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
        self.context = self.browser.contexts[0]

        # 找 DSW 页面
        self.page = None
        for pg in self.context.pages:
            if "dsw-gateway" in pg.url and "/lab" in pg.url:
                self.page = pg
                break

        if self.page is None:
            print("[DSW] 未找到现有 DSW 页面，新建并访问...")
            self.page = await self.context.new_page()
            try:
                await self.page.goto(self.dsw_url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"[DSW] goto 超时（可能还在加载），继续: {e}")
            await asyncio.sleep(15)

        print(f"[DSW] 当前 URL: {self.page.url[:80]}")

        # 登录态验证
        if any(k in self.page.url.lower() for k in ["login", "account.aliyun", "signin"]):
            print("[DSW] redirected to login page; manual login required")
            print("=" * 70)
            print("  ⚠️  请在 Chrome 窗口手动登录阿里云，脚本会自动检测")
            print("=" * 70)
            for i in range(300):
                await asyncio.sleep(1)
                cur = self.page.url
                if not any(k in cur.lower() for k in ["login", "account.aliyun", "signin"]):
                    print(f"[DSW] login succeeded: {cur[:80]}")
                    return True
                if i % 30 == 29:
                    print(f"  等待登录... ({i+1}s)")
            raise RuntimeError("5 分钟登录超时")

        print("[DSW] login session is valid")
        # 等 JupyterLab 完全加载
        await asyncio.sleep(5)
        return True

    async def execute_via_jupyter_api(self, code: str, timeout: int = 60) -> str:
        """
        通过 JupyterLab REST API + WebSocket 执行 Python 代码。
        返回所有 stream/execute_result/error 的合并文本。
        """
        base_url = self.page.url.split("/lab")[0]

        # 创建 kernel
        kernel_id = await self.page.evaluate("""
            async (base) => {
                const resp = await fetch(`${base}/api/kernels`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: 'python3', kind: 'kernel'})
                });
                if (!resp.ok) {
                    const text = await resp.text();
                    throw new Error(`HTTP ${resp.status}: ${text}`);
                }
                const data = await resp.json();
                return data.id;
            }
        """, base_url)

        # WebSocket 执行代码
        output = await self.page.evaluate("""
            async (params) => {
                const {base, kernelId, code, timeoutSec} = params;
                return new Promise((resolve, reject) => {
                    const wsUrl = base.replace(/^http/, 'ws') + `/api/kernels/${kernelId}/channels`;
                    let ws;
                    try { ws = new WebSocket(wsUrl); }
                    catch (e) { reject('WebSocket 创建失败: ' + e.message); return; }

                    const outputs = [];
                    const msgId = 'msg-' + Math.random().toString(36).slice(2, 12);
                    const sessionId = 'sess-' + Math.random().toString(36).slice(2, 12);
                    let idleReceived = false;

                    ws.onopen = () => {
                        ws.send(JSON.stringify({
                            header: {msg_id: msgId, username: '', session: sessionId,
                                     msg_type: 'execute_request', version: '5.4'},
                            parent_header: {}, metadata: {},
                            content: {code: code, silent: false, store_history: true,
                                      user_expressions: {}, allow_stdin: false,
                                      stop_on_error: true},
                            channel: 'shell'
                        }));
                    };

                    ws.onmessage = (event) => {
                        let msg;
                        try { msg = JSON.parse(event.data); } catch (e) { return; }
                        const parentMsgId = msg.parent_header && msg.parent_header.msg_id;
                        if (parentMsgId !== msgId) return;

                        const t = msg.msg_type;
                        if (t === 'stream') {
                            outputs.push(msg.content.text || '');
                        } else if (t === 'execute_result') {
                            const text = msg.content.data && msg.content.data['text/plain'];
                            if (text) outputs.push(text);
                        } else if (t === 'display_data') {
                            const text = msg.content.data && msg.content.data['text/plain'];
                            if (text) outputs.push('[display] ' + text);
                        } else if (t === 'error') {
                            outputs.push('ERROR: ' + (msg.content.ename || '') + ': ' + (msg.content.evalue || ''));
                            outputs.push((msg.content.traceback || []).join('\\n'));
                        } else if (t === 'status' && msg.content.execution_state === 'idle') {
                            idleReceived = true;
                            ws.close();
                            resolve(outputs.join('\\n') || '(no output, kernel idle)');
                        }
                    };

                    ws.onerror = (e) => reject('WebSocket 错误: ' + (e.message || 'unknown'));
                    setTimeout(() => {
                        if (!idleReceived) {
                            try { ws.close(); } catch (e) {}
                            resolve(outputs.join('\\n') || `(timeout after ${timeoutSec}s)`);
                        }
                    }, timeoutSec * 1000);
                });
            }
        """, {"base": base_url, "kernelId": kernel_id, "code": code, "timeoutSec": timeout})

        # 关闭 kernel
        try:
            await self.page.evaluate("""
                async (params) => {
                    await fetch(`${params.base}/api/kernels/${params.kid}`, {method: 'DELETE'});
                }
            """, {"base": base_url, "kid": kernel_id})
        except Exception:
            pass

        return output or ""

    async def run_shell(self, cmd: str, timeout: int = 60) -> str:
        """执行 shell 命令，返回 stdout + stderr"""
        # 用 shlex.quote 避免 Python 字符串转义问题
        import shlex
        code = f"""
import subprocess
r = subprocess.run({cmd!r}, capture_output=True, text=True, shell=True, timeout={timeout})
print(r.stdout, end='')
if r.stderr:
    print('---STDERR---', end='\\n')
    print(r.stderr, end='')
print('---EXIT_CODE:', r.returncode)
"""
        return await self.execute_via_jupyter_api(code, timeout=timeout + 10)

    async def run_long_task(self, cmd: str, log_file: str, wait_seconds: int = 5) -> str:
        """
        nohup 后台执行长任务，立即返回（不等待完成）。
        后续用 query_log() 轮询日志。
        """
        code = f"""
import subprocess
# 先清理可能存在的旧进程
subprocess.run("pkill -f '{cmd.split(' ')[0]}' 2>/dev/null || true", shell=True)
# nohup 启动
full_cmd = f"nohup {cmd} > {log_file} 2>&1 &"
subprocess.run(full_cmd, shell=True)
import time
time.sleep({wait_seconds})
# 读前几行日志确认启动
import os
if os.path.exists({log_file!r}):
    with open({log_file!r}) as f:
        print(f.read()[:2000])
else:
    print('LOG_FILE_NOT_CREATED')
"""
        return await self.execute_via_jupyter_api(code, timeout=wait_seconds + 15)

    async def query_log(self, log_file: str, tail_lines: int = 50) -> str:
        """查询日志文件尾部"""
        code = f"""
import os
if not os.path.exists({log_file!r}):
    print('LOG_NOT_EXISTS')
else:
    with open({log_file!r}) as f:
        lines = f.readlines()
    print(''.join(lines[-{tail_lines}:]))
"""
        return await self.execute_via_jupyter_api(code, timeout=15)

    async def is_process_running(self, process_pattern: str) -> bool:
        """检查进程是否在运行"""
        out = await self.run_shell(f"pgrep -f '{process_pattern}' | head -1")
        return bool(out.strip()) and "EXIT_CODE: 0" in out

    async def download_file(self, remote_path: str, local_path: str) -> str:
        """通过 JupyterLab Contents API 下载文件"""
        base_url = self.page.url.split("/lab")[0]
        content = await self.page.evaluate("""
            async (url) => {
                const resp = await fetch(url);
                return await resp.text();
            }
        """, f"{base_url}/api/contents/{remote_path}")

        data = json.loads(content)
        if data.get("content") and isinstance(data["content"], str) and data["content"].startswith("data:"):
            import base64
            b64 = data["content"].split(",", 1)[1]
            with open(local_path, "wb") as f:
                f.write(base64.b64decode(b64))
            return local_path
        raise RuntimeError(f"Unexpected content format: {str(data.get('content', ''))[:200]}")

    async def close(self):
        """关闭 Playwright（不关 Chrome，保留登录态）"""
        if self._playwright:
            await self._playwright.stop()


# ============== 命令行入口（用于独立测试） ==============
async def _cli():
    import sys
    dsw = DswRemote()
    await dsw.connect()
    try:
        if len(sys.argv) > 2 and sys.argv[1] == "--shell":
            out = await dsw.run_shell(sys.argv[2], timeout=int(sys.argv[3]) if len(sys.argv) > 3 else 60)
            print(out)
        elif len(sys.argv) > 2 and sys.argv[1] == "--code":
            out = await dsw.execute_via_jupyter_api(sys.argv[2], timeout=int(sys.argv[3]) if len(sys.argv) > 3 else 60)
            print(out)
        else:
            print("Usage: python dsw_remote.py --shell 'nvidia-smi' [timeout]")
            print("       python dsw_remote.py --code 'print(1+1)' [timeout]")
    finally:
        await dsw.close()


if __name__ == "__main__":
    asyncio.run(_cli())
