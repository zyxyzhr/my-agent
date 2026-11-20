"""
第 1 课：你的第一个 LLM 请求
════════════════════════════════
目标：不借助任何框架，亲手构造一次 HTTP 请求，把问题发给 LLM 服务，拿回回答。

开跑前先建立三个认知（本课的"理论"就这么多）：
  1) LLM 服务就是一个普通的 HTTP 服务：
       你发出去：JSON（用哪个模型 + 你想问什么）
       它返回来：JSON（它的回答 + token 用量等统计）
       它是【无状态】的：两次请求之间，服务器不记得任何东西。
  2) 请求体里最重要的字段是 messages —— 一个列表，每个元素是一句话：
       {"role": "system",    "content": "规则/人设"}   放最前面（可选）
       {"role": "user",      "content": "你说的话"}
       {"role": "assistant", "content": "模型之前说过的话"}
     "对话"本质上就是把这个列表一轮轮加长再发回去（第 2 课的主题）。
  3) 响应体里，模型的回答在 choices[0].message.content。
     先记住这句话 —— 第 3 课工具调用时，同一个 message 里会多出一个
     tool_calls 字段，那是整个 Agent 的起点。

运行（在项目目录的终端里）：
    python hello.py
"""
import json
import pathlib
import urllib.request

_config_path = pathlib.Path(__file__).parent / "config.json"
if not _config_path.exists():
    raise SystemExit(
        "未找到 config.json。先按 README「快速开始」第 2 步：\n"
        "复制 config.example.json 为 config.json，并填写你的后端配置。"
    )
config = json.loads(_config_path.read_text(encoding="utf-8"))
print("使用模型:", config["model"])

# ── 第 1 步：读配置 ────────────────────────────────────────────
# config.json 三个字段：
#   base_url  服务地址（以 /v1 结尾的 OpenAI 兼容端点）
#   model     模型名（后面课程需要支持 function calling 的模型）
#   auth      授权码（API 密钥，千万别提交到 git —— .gitignore 已配好）

# ── 第 2 步：构造对话 ──────────────────────────────────────────
# messages 是一个列表，每个元素 = 一句话 {"role": ..., "content": ...}
#
# TODO-1：填入一条 user 消息，让模型"只回复两个字：收到"
#         元素格式固定为 {"role": "user", "content": "你的话"}
messages = [
    # TODO-1：在这里填
]

# ── 第 3 步：组装 HTTP 请求 ────────────────────────────────────
# JSON 对象不能直接走网络，要先序列化成 bytes
body = json.dumps(
    {"model": config["model"], "messages": messages},
    ensure_ascii=False,
).encode("utf-8")
# 注意：ensure_ascii=False 让中文以原文发送（否则变成 \uXXXX 转义，
# 模型能看懂但 token 费得多）
#
# TODO-2：用 urllib.request.Request 构造请求对象，替换下面这行
#   - 第一个参数：完整 URL = config["base_url"] + "/chat/completions"
#   - data=body
#   - headers={...} 需要两个头：
#       "Content-Type": "application/json"
#       "Authorization": "Bearer " + config["auth"]
#     （注意 Bearer 和密钥之间有一个空格）
#   提示：Request(url, data=body, headers={...})
req = None  # TODO-2：用你的 Request(...) 替换这行

# ── 第 4 步：发送，打印原始响应 ────────────────────────────────
resp = urllib.request.urlopen(req, timeout=90)
raw = resp.read().decode("utf-8")
print("\n=== 原始响应（后面几课你会反复看这种 JSON） ===")
print(raw)

# ── 第 5 步：取出回答 ─────────────────────────────────────────
data = json.loads(raw)
# TODO-3：把模型的回答打印出来。
#   提示：回答在 data["choices"][0]["message"]["content"]
#   顺手把 data["usage"] 也打印出来，看看 token 是怎么计费的。
print("\n=== 模型的回答 ===")
# TODO-3：在这里填
