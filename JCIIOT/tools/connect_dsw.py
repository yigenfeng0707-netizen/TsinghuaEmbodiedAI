"""连接 DSW 实例，验证登录态，提取 cookie 供 dswhub.py 使用。"""
import asyncio
import json
import os
import sys

sys.path.insert(0, r"d:\APPs\TsinghuaEmbodiedAI\scripts")
from dsw_remote import DswRemote, ensure_chrome_with_cdp

DSW_URL = "https://dsw-gateway-cn-hangzhou.data.aliyun.com/dsw-2085479/lab/tree/dswQinghua"
COOKIE_OUT = os.path.join(os.path.dirname(__file__), "..", "ms_session_cookies.json")


async def main():
    if not ensure_chrome_with_cdp():
        print("[FAIL] Chrome CDP 启动失败")
        return 1

    dsw = DswRemote(dsw_url=DSW_URL)
    try:
        ok = await dsw.connect()
    except RuntimeError as e:
        print(f"[FAIL] {e}")
        return 1

    if not ok:
        print("[FAIL] 连接失败")
        return 1

    print("[OK] DSW 已连接，登录态有效")

    # 提取 cookies 并保存
    cookies = await dsw.context.cookies()
    cookie_dict = {c["name"]: c["value"] for c in cookies}

    out = {
        "domain": "https://dsw-gateway-cn-hangzhou.data.aliyun.com",
        "cookies": cookie_dict,
        "captured_at": asyncio.get_event_loop().time(),
    }
    with open(COOKIE_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    has_ticket = "login_aliyunid_ticket" in cookie_dict
    print(f"提取 {len(cookie_dict)} 个 cookies")
    print(f"login_aliyunid_ticket: {'FOUND' if has_ticket else 'MISSING'}")
    if has_ticket:
        print(f"已保存到 {COOKIE_OUT}")
        return 0
    else:
        print("可用 cookies:", sorted(cookie_dict.keys()))
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
