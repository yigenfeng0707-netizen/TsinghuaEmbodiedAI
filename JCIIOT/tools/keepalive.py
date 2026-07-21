"""DSW 实例闲置保活脚本（本地常驻）。

DSW 的"闲置自动停止"通常基于网关一段时间无活动。本脚本周期性地通过
tools/dswhub 在实例上执行一条无害命令（打印当前时间），保持网关活跃，
从而避免触发闲置停止。

用法:
    python tools/keepalive.py            # 默认每 4 分钟心跳一次，常驻
    python tools/keepalive.py --interval 300 --max 20   # 5 分钟一次，最多 20 次后退出
    Ctrl+C 退出

注意: 只能对抗"闲置停止"，无法对抗"运行时长硬上限/手动停止/配额回收"。
"""
from __future__ import annotations

import argparse
import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.dswhub as d  # noqa: E402


def heartbeat() -> str:
    # 用 contents 列表调用保活：已验证稳定可用，且不需要 kernel/ws 握手，
    # 足以让 DSW 网关认为实例处于活跃状态（对抗闲置自动停止）。
    import time
    c = d.Dswhub()
    c.contents("")
    return f"keepalive {time.time():.0f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=240, help="心跳间隔（秒），默认 240")
    ap.add_argument("--max", type=int, default=0, help="最大心跳次数，0=无限（默认）")
    args = ap.parse_args()

    print(f"[keepalive] 启动，间隔 {args.interval}s，最大 {args.max or '无限'} 次")
    print("[keepalive] Ctrl+C 退出")
    n = 0
    try:
        while True:
            n += 1
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            try:
                out = heartbeat()
                print(f"[{ts}] #{n} OK: {out.strip()[:80]}")
            except Exception as e:  # 单次失败不退出，继续下次
                print(f"[{ts}] #{n} 失败: {repr(e)[:160]}")
            if args.max and n >= args.max:
                print(f"[keepalive] 已达最大次数 {args.max}，退出")
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[keepalive] 收到 Ctrl+C，退出")


if __name__ == "__main__":
    main()
