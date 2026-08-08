"""从 DSW /tmp/replay_gifs 下载已生成的 GIF 到本地。

使用 Jupyter contents API 获取文件 base64 内容并保存。
"""
import base64
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dswhub import Dswhub


def main():
    d = Dswhub()
    local_dir = Path(__file__).parent.parent / "submission" / "replay_gifs"
    local_dir.mkdir(parents=True, exist_ok=True)

    # 获取 /tmp/replay_gifs 目录下的文件列表(/tmp 不在 lab 根目录,用 kernel 执行)
    print("Listing /tmp/replay_gifs...")
    list_code = (
        "import os\n"
        "out_dir = '/tmp/replay_gifs'\n"
        "if os.path.exists(out_dir):\n"
        "    files = sorted(os.listdir(out_dir))\n"
        "    for f in files:\n"
        "        size = os.path.getsize(os.path.join(out_dir, f))\n"
        "        print(f'{f}|{size}')\n"
        "else:\n"
        "    print('NO_DIR')\n"
    )
    result = d.run_python(list_code, timeout=15)
    print("Files on DSW:")
    print(result)

    files = []
    for line in result.strip().split("\n"):
        if "|" in line:
            name, size = line.rsplit("|", 1)
            files.append((name.strip(), int(size)))

    if not files:
        print("No files to download")
        return

    # 逐个下载(通过 kernel 读取 base64)
    for name, size in files:
        local_path = local_dir / name
        if local_path.exists() and local_path.stat().st_size == size:
            print(f"  [SKIP] {name} (already downloaded)")
            continue

        # 大文件(>20MB)跳过,避免 kernel 超时
        if size > 20 * 1024 * 1024:
            print(f"  [LARGE] {name} ({size//1024}KB) - will download separately")
            continue

        print(f"  [DOWN] {name} ({size//1024}KB)...", end=" ", flush=True)
        # 用 kernel 读取文件 base64
        dl_code = (
            "import base64\n"
            f"with open('/tmp/replay_gifs/{name}', 'rb') as f:\n"
            "    data = base64.b64encode(f.read()).decode()\n"
            "print(data)\n"
        )
        b64_data = d.run_python(dl_code, timeout=60)
        if b64_data.strip():
            try:
                raw = base64.b64decode(b64_data.strip())
                with open(local_path, "wb") as f:
                    f.write(raw)
                print(f"OK ({len(raw)//1024}KB)")
            except Exception as e:
                print(f"FAIL: {e}")
        else:
            print("FAIL: empty response")


if __name__ == "__main__":
    main()
