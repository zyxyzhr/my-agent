"""
第 5 课单元测试：
    python test_lesson5.py
全部 PASS = 第 5 课验收通过。

（本测试在第 4 课完成前运行必然 FAIL，这是正常的——它是第 5 课的验收工具。）
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import agent  # noqa: E402

FAILED = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    extra = f"  <- {detail}" if (detail and not cond) else ""
    print(f"[{status}] {name}{extra}")
    if not cond:
        FAILED.append(name)


# ── 1. 普通截断（无 tool 消息）──────────────────────────────
msgs = [{"role": "system", "content": "S"}]
for n in range(1, 8):
    msgs += [{"role": "user", "content": f"u{n}"}, {"role": "assistant", "content": f"a{n}"}]
orig_len = len(msgs)
out = agent.trim_history(msgs, keep_last=6)
roles = [m["role"] for m in out]
check("保留 system 在首位", roles and roles[0] == "system", str(roles))
check("截断生效（结果长度 <= keep_last+1）", len(out) <= 7, f"len={len(out)}")
check("保留的是最近的尾部", bool(out) and out[-1]["content"] == "a7", str(roles))
check("原列表未被修改", len(msgs) == orig_len, f"len={len(msgs)}")

# ── 2. 孤儿 tool 保护 ──────────────────────────────────────
tc = {"id": "call_x", "type": "function", "function": {"name": "calculator", "arguments": "{}"}}
msgs2 = [
    {"role": "system", "content": "S"},
    {"role": "user", "content": "u1"},
    {"role": "assistant", "content": "a1"},
    {"role": "user", "content": "u2"},
    {"role": "assistant", "content": None, "tool_calls": [tc]},
    {"role": "tool", "tool_call_id": "call_x", "content": "42"},
    {"role": "tool", "tool_call_id": "call_x", "content": "21"},
]
out2 = agent.trim_history(msgs2, keep_last=3)
roles2 = [m["role"] for m in out2]
check("截断生效（比原列表短）", len(out2) < len(msgs2), f"len={len(out2)}")
check("无孤儿 tool（截断后第一条非system消息不是tool）",
      bool(out2) and len(out2) > 1 and out2[1]["role"] != "tool", str(roles2))

# ── 3. 持久化 round-trip ───────────────────────────────────
p = pathlib.Path(__file__).parent / "_test_hist.json"
try:
    hist = [{"role": "user", "content": "你好，世界"}]
    agent.save_history(hist, path=str(p))
    loaded = agent.load_history(path=str(p))
    check("存盘→读回 一致", loaded == hist, str(loaded))
    raw = p.read_text(encoding="utf-8")
    check("中文原文写入（ensure_ascii=False）", "你好，世界" in raw)
finally:
    p.unlink(missing_ok=True)

# ── 4. 损坏文件不能崩 ──────────────────────────────────────
p2 = pathlib.Path(__file__).parent / "_test_bad.json"
p2.write_text("{损坏的JSON", encoding="utf-8")
try:
    try:
        r = agent.load_history(path=str(p2))
        check("损坏文件返回 []（不崩溃）", r == [], str(r))
    except Exception as e:
        check("损坏文件返回 []（不崩溃）", False, f"崩溃了: {type(e).__name__}")
finally:
    p2.unlink(missing_ok=True)

print()
if FAILED:
    print(f"共 {len(FAILED)} 项未通过: {FAILED}")
    sys.exit(1)
print("全部 PASS")
