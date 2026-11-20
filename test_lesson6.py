"""
第 6 课单元测试（含 2 次真实 API 调用）：
    python test_lesson6.py
全部 PASS = 第 6 课验收通过。

（本测试依赖 llm_client.py 的 stream_chat / chat_with_retry，
在第 6 课完成前运行必然 FAIL，这是正常的。）
"""
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import llm_client  # noqa: E402

FAILED = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    extra = f"  <- {detail}" if (detail and not cond) else ""
    print(f"[{status}] {name}{extra}")
    if not cond:
        FAILED.append(name)


# ── 1. 流式 ─────────────────────────────────────────────
pieces = list(llm_client.stream_chat([{"role": "user", "content": "只回复四个字：你好世界"}]))
text = "".join(pieces)
check("流式返回多个 chunk", len(pieces) >= 3, f"chunks={len(pieces)}")
check("流式拼回的文本包含「你好世界」", "你好世界" in text, f"text={text!r}")

# ── 2. 重试退避（指向死端口：3 次尝试 + 1s/2s 退避后抛异常）──
original_url = llm_client.config["base_url"]
llm_client.config["base_url"] = "http://127.0.0.1:9/v1"
t0 = time.time()
try:
    llm_client.chat_with_retry([{"role": "user", "content": "hi"}], max_retries=3)
    check("重试最终抛异常（不吞）", False, "意外成功了")
except Exception:
    elapsed = time.time() - t0
    check("重试最终抛异常（不吞）", True)
    check(f"退避真的执行了（耗时 >= 2.5s，实际 {elapsed:.1f}s）", elapsed >= 2.5, f"{elapsed:.1f}s")
finally:
    llm_client.config["base_url"] = original_url

print()
if FAILED:
    print(f"共 {len(FAILED)} 项未通过: {FAILED}")
    sys.exit(1)
print("全部 PASS")
