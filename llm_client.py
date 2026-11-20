"""
协议层：所有与 LLM 服务的 HTTP 通信都经过这个文件。

两批 TODO：
    第 4 课 TODO-1：实现 chat() —— 最基本的请求函数
                    （参考 agent_v1.py 里的 chat，把逻辑搬过来即可）
    第 6 课 TODO-10 / TODO-11：实现 chat_with_retry() 和 stream_chat()

运行任何课程前需要 config.json 存在（创建方法见 README「快速开始」）。
"""
import json
import logging
import pathlib
import time
import urllib.error
import urllib.request

_CONFIG_PATH = pathlib.Path(__file__).parent / "config.json"
if not _CONFIG_PATH.exists():
    raise SystemExit(
        "未找到 config.json：请先复制 config.example.json 为 config.json，"
        "并填写 base_url / model / auth（见 README「快速开始」）。"
    )
with _CONFIG_PATH.open(encoding="utf-8") as _f:
    config = json.load(_f)


# ── 第 4 课 TODO-1：基本请求函数 ─────────────────────────────
def chat(messages, tools=None):
    """发送 messages（可选 tools），返回完整响应 JSON（dict）。

    提示结构（和 agent_v1.py 的 chat 一样）：
        body = {"model": config["model"], "messages": messages}
        if tools:
            body["tools"] = tools
        request = urllib.request.Request(
            config["base_url"] + "/chat/completions",
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + config["auth"],
            },
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    """
    # TODO-1：实现
    pass


# ── 第 6 课 TODO-10：重试包装（瞬时错误自动重试，永久错误立即抛）──
def chat_with_retry(messages, tools=None, max_retries=3):
    """chat + 自动重试。

    要重试：429（限流）、5xx（服务端故障）、网络错误/超时（URLError/TimeoutError）
    不重试：其他 4xx —— 请求本身错了/认证失败，重试一百次也一样错，立即抛
    退避：1s -> 2s（time.sleep(2 ** attempt)），最后一次失败后不睡，直接抛
    """
    # TODO-10：实现
    # 提示结构：
    #   last_exc = None
    #   for attempt in range(max_retries):
    #       try:
    #           return chat(messages, tools)
    #       except urllib.error.HTTPError as e:
    #           last_exc = e
    #           if not (e.code == 429 or e.code >= 500):
    #               raise                    # 其他 4xx：永久错误
    #       except (urllib.error.URLError, TimeoutError) as e:
    #           last_exc = e
    #       logging.warning("第%d次请求失败(%s)，%d秒后重试...",
    #                       attempt + 1, type(last_exc).__name__, 2 ** attempt)
    #       if attempt < max_retries - 1:
    #           time.sleep(2 ** attempt)
    #   raise last_exc
    pass


# ── 第 6 课 TODO-11：流式版（SSE）────────────────────────────
def stream_chat(messages, tools=None):
    """流式请求：body["stream"] = True。

    响应不再是"一大块 JSON"，而是逐行到达的文本流（SSE 协议）：
        data: {"choices": [{"delta": {"role": "assistant"}}]}
        data: {"choices": [{"delta": {"reasoning_content": "..."}}]}  ← 思考块（思考模型先吐这个）
        data: {"choices": [{"delta": {"content": "你"}}]}
        data: {"choices": [{"delta": {"content": "好"}}]}
        ...
        data: [DONE]
    本函数是【生成器】（body 里含 yield，没有 return），
    逐个 yield content 碎片，调用方一边收一边打印。

    两个坑（记牢）：
        1. 有的 chunk 的 choices 是空列表，不能直接取 [0]，先判空
        2. 思考模型先流式吐 reasoning_content 再吐 content，只取 content
    （注：带 tools 时 tool_calls 的 delta 会跨多个 chunk 需要拼接，
      属于进阶话题，现在不实现，知道存在即可）
    """
    # TODO-11：实现
    # 提示结构：
    #   body = {"model": config["model"], "messages": messages, "stream": True}
    #   （tools 非空时 body["tools"] = tools）
    #   req = urllib.request.Request(  # 和 chat 里完全一样
    #   with urllib.request.urlopen(req, timeout=120) as resp:
    #       for raw in resp:                    # 响应对象可以按行迭代
    #           line = raw.decode("utf-8").strip()
    #           if not line.startswith("data: "):
    #               continue
    #           payload = line[len("data: "):]
    #           if payload == "[DONE]":
    #               break
    #           chunk = json.loads(payload)
    #           choices = chunk.get("choices") or []
    #           if not choices:
    #               continue
    #           delta = choices[0].get("delta") or {}
    #           piece = delta.get("content")
    #           if piece:
    #               yield piece
    pass
