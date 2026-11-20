"""
第 2 课：对话就是上下文
════════════════════════════════
第 1 课建立了认知：模型是无状态的，什么都不记得。
这一课你亲手造出"记忆的错觉"：

    多轮对话 = 每轮把【全部历史 + 新问题】整个发过去

    第1轮发: [system, user1]                              → 模型回 asst1
    第2轮发: [system, user1, asst1, user2]                 → 模型回 asst2
    第3轮发: [system, user1, asst1, user2, asst2, user3]   → ...

模型没有"记忆"，是我们每轮把之前的对话原样发回去。
这个列表就叫上下文（context），它每轮都在变长——
token 成本问题留给第 5 课。

运行：
    python chat.py
    （输入 exit 退出）

验收实验（必做）：
    1) 你说：我叫某某，在某公司，负责某某项目。记住。
    2) 随便再聊一两轮别的。
    3) 你问：我叫什么名字？在哪个公司？负责什么项目？
    模型答对了——想清楚：这个"记忆"物理上存在哪里？
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

# system 消息：每次请求都固定放在最前面，它是 Agent 的"人设/规则"
# 可以随便改，这里定义的是你这个 Agent 的灵魂
SYSTEM = "你是一个简洁、诚实的中文助手。"

# ─────────────────────────────────────────────────────────────
# TODO-1：写核心函数 chat(messages)
#   输入：完整的 messages 列表（含 system 和历史）
#   工作：组装请求并发送——把 hello.py 第 3、4 步的代码搬进来
#   返回：模型的回复文本（content 字符串）
#   注意：函数里不要 print，只 return，打印交给调用者
#   提示：
#     请求体 = {"model": config["model"], "messages": messages}
#     回复   = resp_data["choices"][0]["message"]["content"]
# ─────────────────────────────────────────────────────────────
def chat(messages):
    # TODO-1：在这里实现
    pass


def main():
    # ─────────────────────────────────────────────────────────
    # TODO-2：多轮循环
    #   1) history = []          一开始什么都没有
    #   2) while True:
    #        user_text = input("你: ")
    #        # TODO-3：如果 user_text.strip() == "exit"，break
    #        把 user 消息追加进 history（记住格式：{"role": ..., "content": ...}）
    #        reply = chat([system消息] + history)
    #        # 注意：每次调用都要把 SYSTEM 重新拼在最前面！
    #        print("助手:", reply)
    #        把 assistant 消息（模型的回复）追加进 history
    #   3) 循环结束后：print("本次对话共积累", len(history), "条历史消息")
    #
    # 加分验证（强烈建议）：在调 chat 之前加一行
    #   print("本轮发送消息数:", len([system消息] + history))
    # 聊满 3 轮，你应该看到 2、4、6 —— 这就是"对话 = 上下文"的直接证据。
    # ─────────────────────────────────────────────────────────
    pass


if __name__ == "__main__":
    main()
