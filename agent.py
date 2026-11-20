"""
第 4 课：Agent 主循环
════════════════════════════════
第 3 课是固定的两轮请求。真实场景里模型可能连调 N 轮工具：
    - 一次问两件事 → 一轮里同时申请两个工具
    - 工具返回错误 → 模型看到错误消息，自我纠正或正确解释
    - 一个工具的答案是下一个工具的输入 → 连续调用

所以把固定两轮泛化成通用循环。本课核心只有一句：

    Agent = while 循环 + 停止条件
    循环体：发送 → 看响应
        没有 tool_calls（stop）  → 拿到最终答案，返回
        有 tool_calls            → 申请书入历史 → 逐个执行工具
                                    → 结果入历史 → 回循环顶部再发

两个安全阀：
    - max_steps：连续 N 轮还在调工具就强制停（防死循环）
    - try/except：工具报错时，把【错误消息】喂回给模型让它自我纠正
      （错误消息成了模型的下一轮输入 —— 循环的魔力所在）

运行：
    python agent.py

试一试（按顺序，每句都盯"调了几轮、调了哪些工具"）：
    17*23+8等于多少？
    现在几点？
    帮我算 5 的 3 次方，顺便告诉我现在几点     ← 一轮申请两个工具
    sqrt(16)等于多少？                          ← 模型可能自己翻译成 16**0.5
    17/0等于多少？                               ← 工具报错，观察 try/except
    17+*8等于多少？                              ← 模型可能一次算出两种解释
    17*abc+1等于多少？                           ← 模型可能不调工具直接反问

你的 TODO 清单：
    TODO-1: 在 llm_client.py 里实现 chat()（骨架已备好，参考 agent_v1.py 的 chat），
            然后在本文件顶部 import。
    TODO-2: TOOLS 里补 get_current_time 的声明（2a）+ FUNCTIONS 注册表补一项（2b）
    TODO-3: run_agent 的 while 循环主体
    TODO-4: 循环内执行单个工具调用（解析参数 → 查表 → 执行 → try/except → 结果入历史）
    TODO-5: main() 多轮 REPL（复用第 2 课的模式）
"""
import ast
import json
import operator
from datetime import datetime, timedelta, timezone

# TODO-1: from llm_client import chat

SYSTEM = (
    "你是一个严谨的助手。需要计算时，必须使用 calculator 工具；"
    "被问到时间时，必须使用 get_current_time 工具。"
    "严禁不调用工具就编造结果。"
)

# ── 工具本体（本课提供，你只需读懂白名单思路）────────────────
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("表达式包含不支持的操作（白名单之外一律拒绝）")


def calculate(expression: str):
    """安全地计算数学表达式：只允许数字 + - * / ** ( )"""
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


def get_current_time():
    """无参工具：返回当前北京时间字符串"""
    now = datetime.now(timezone(timedelta(hours=8)))
    return now.strftime("%Y-%m-%d %H:%M:%S 北京时间(UTC+8)")


# ── 工具声明（展示给模型的"菜单"）────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式的结果。支持 + - * / ** 和括号。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，如 '17*23+8'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    # TODO-2a：补 get_current_time 的声明。
    #   无参工具：properties 是空 dict，没有 "required" 字段：
    #   {
    #       "type": "function",
    #       "function": {
    #           "name": "get_current_time",
    #           "description": "获取当前北京时间(UTC+8)。用户问时间时调用。",
    #           "parameters": {"type": "object", "properties": {}},
    #       },
    #   }
]

# ── 函数注册表：工具名 → 函数的"调度表" ──────────────────────
# 统一调用方式：FUNCTIONS[name](**args)
#   calculator:        args = {"expression": "17*23+8"} → calculate(expression="17*23+8")
#   get_current_time:  args = {}                         → get_current_time()
# TODO-2b：把 get_current_time 这一项补进注册表
FUNCTIONS = {
    "calculator": calculate,
}


def run_agent(user_text, history=None, max_steps=5):
    """一轮 Agent：用户输入 →（可能多轮工具调用）→ 最终回答

    返回 (final_answer, 可复用的history)：
        可复用的 history = messages 去掉最前面的 system 消息
        （因为每轮开头都会重新拼 system，不能重复进历史）
    """
    history = history or []
    messages = [
        {"role": "system", "content": SYSTEM},
    ] + history + [
        {"role": "user", "content": user_text},
    ]

    steps = 0
    # TODO-3：while 循环主体（注释是伪代码，翻译成真实代码）
    #   while True:
    #       steps += 1
    #       if steps > max_steps:
    #           return f"(强制停止：已 {max_steps} 轮仍在请求工具)", messages[1:]
    #       resp = chat(messages, TOOLS)
    #       msg = resp["choices"][0]["message"]
    #       if not msg.get("tool_calls"):
    #           # stop：最终答案
    #           return (msg.get("content") or ""), messages[1:]
    #       messages.append(msg)            # 「申请书」必须进历史！
    #       for tc in msg["tool_calls"]:    # 模型一轮可能申请多个工具
    #           <TODO-4 在这里>
    #       # 不需要写别的，回到循环顶部再发
    pass


# ═══════════════════════════════════════════════════════════
# 第 5 课：记忆与上下文管理
# ═══════════════════════════════════════════════════════════
# TODO-6：在 run_agent 的循环里，每次拿到 resp 后打印本轮 token 数：
#   print(f"  [第{steps}轮] prompt_tokens={resp['usage']['prompt_tokens']}")
#   （先只做这一条，跑 5 轮 REPL，观察数字怎么涨）
#
# TODO-7：历史截断函数（安全边界版）——实现下面这个函数：
def trim_history(messages, keep_last=10):
    """保留 system（第 0 条）+ 最近的 keep_last 条。

    关键规则：如果截断后剩下的第一条是 role == "tool"，
    说明它对应的 assistant tool_calls 申请书被切掉了 ——
    孤儿 tool 消息会让 API 直接报错，必须继续往前多切几条，
    直到剩下的第一条不再是 tool。
    返回新列表，不要原地改。
    """
    # TODO-7：实现
    return messages


# TODO-8：持久化（"记忆"活过进程）
def save_history(history, path="history.json"):
    """把 history 写到磁盘。json.dump，记得 ensure_ascii=False"""
    # TODO-8a：实现
    pass


def load_history(path="history.json"):
    """从磁盘读回 history。文件不存在或损坏时返回 []，不要崩"""
    # TODO-8b：实现
    return []


# TODO-9：接进 main()：
#   启动时:  history = load_history()
#   每轮后:  save_history(history)
#   （存的是"去掉 system 的 history"，和 run_agent 的约定保持一致）

# ═══════════════════════════════════════════════════════════
# 第 6 课：工程化加固（agent.py 部分）
# ═══════════════════════════════════════════════════════════
# TODO-12：logging 替换 print
#   文件顶部：import logging
#   logging.basicConfig(level=logging.INFO,
#                       format="%(asctime)s [%(levelname)s] %(message)s")
#   把 run_agent 里的过程性 print 改成 logging.info：
#     - 每轮的 prompt_tokens
#     - 每次工具调用（工具名、参数、结果）
#   最终回答保持 print —— 那是"给用户的输出"，不是日志。
#   区别：print 是给人看的界面输出；logging 带时间戳和级别，
#   是给运维看的，以后可以加 FileHandler 落到文件里。
#
# TODO-12b：run_agent 里把 resp = chat(messages, TOOLS) 换成
#           resp = chat_with_retry(messages, TOOLS)
#           文件顶部的 import 同步改为：
#           from llm_client import chat, chat_with_retry, stream_chat
#
# TODO-13：main() 加流式入口
#   输入以 "stream " 开头时，走 stream_chat 逐字打印（不调工具）：
#       question = text[len("stream "):]
#       for piece in stream_chat([{"role": "user", "content": question}]):
#           print(piece, end="", flush=True)   # flush=True 强制立即输出
#       print()


def main():
    # TODO-5：多轮 REPL
    #   history = []          （第 5 课 TODO-9 改成 history = load_history()）
    #   while True:
    #       text = input("你: ")
    #       if text.strip() == "exit":
    #           break
    #       answer, history = run_agent(text, history)
    #       print("助手:", answer)
    #       （第 5 课 TODO-9 加 save_history(history)）
    print("TODO-5：实现多轮 REPL（见上方注释）")


if __name__ == "__main__":
    main()
