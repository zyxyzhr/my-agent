"""
第 3 课：第一次工具调用（全课核心）
════════════════════════════════
最反直觉的事实：模型执行不了任何代码，它只会生成文本。
"调用工具"其实是一个 4 步闭环：

    ① 请求里告诉模型：你有这些工具（名字 + 描述 + 参数格式）
    ② 模型想用了 → 它不生成回答，生成特殊结构：
         message.tool_calls = [{"id": "...",
                                "function": {"name": "calculator",
                                             "arguments": "{\"expression\": \"17*23+8\""}}}]
       注意：arguments 是 JSON【字符串】，不是对象！
    ③ 你的代码解析 ②，真的执行函数，拿到结果
    ④ 结果以 role="tool" 的消息发回（并带上 ② 那条消息原样），
       模型看到结果 → 生成最终回答

    模型 ──tool_calls──▶ 你的代码执行 ──结果──▶ 模型 ──最终回答
    记住：模型只"申请"，代码才"执行"。这就是 Agent 的本质。

这一课你手写这个闭环（固定两轮请求）。
第 4 课会把它写成循环，让模型想调几次调几次。

安全点（为什么不用 eval）：
    模型生成的 arguments 是"不可信输入"。如果直接 eval(expression)，
    模型说 "import os; os.system(...)" 就真的会执行。
    下面的 calculator 用 AST 白名单：只允许数字和 + - * / ** 与括号。

运行：
    python agent_v1.py
"""
import ast
import json
import operator
import pathlib
import urllib.request

_config_path = pathlib.Path(__file__).parent / "config.json"
if not _config_path.exists():
    raise SystemExit(
        "未找到 config.json。先按 README「快速开始」第 2 步：\n"
        "复制 config.example.json 为 config.json，并填写你的后端配置。"
    )
config = json.loads(_config_path.read_text(encoding="utf-8"))

SYSTEM = "你是一个严谨的计算助手。需要计算时，必须使用 calculator 工具，严禁自己心算。"

# ── 工具本体（本课提供，你只需要读懂"为什么不是 eval"）────────
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,  # 一元负号，比如 -5
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


# ── 工具声明：我们展示给模型看的"菜单" ────────────────────────
# 模型看不到 calculate 的源码，它只看到这段 JSON 描述。
# description 写得好不好，直接决定模型会不会用、用得对不对。
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
    }
]


# ── 请求函数（chat.py 的 chat + tools 参数，本课已写好）──────
# 对照你在 chat.py 里写的版本：只多了 if tools: body["tools"] = tools 两行。
def chat(messages, tools=None):
    body = {"model": config["model"], "messages": messages}
    if tools:
        body["tools"] = tools
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        config["base_url"] + "/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + config["auth"],
        },
    )
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read().decode("utf-8"))


def main():
    question = "17*23+8等于多少？"
    # 想练手可以换别的算式，比如 "(3+5)*2**4等于多少？"

    # ── 第 A 步：第一轮请求 ─────────────────────────────────
    # TODO-1：把 [system消息, user消息(question)] 发给模型，记得带上 TOOLS
    #         把完整原始响应打印出来 —— 你应该能在 message 里看到 tool_calls
    raw_a = None  # TODO-1：这里应该是 chat(...) 的返回值
    msg_a = raw_a["choices"][0]["message"]
    print("\n=== 模型的第一次回复（应该只是「申请」，没给最终答案） ===")
    print(json.dumps(msg_a, ensure_ascii=False, indent=2))

    # ── 第 B 步：解析工具调用 ───────────────────────────────
    # TODO-2：从 msg_a["tool_calls"][0] 取出三样东西，并打印：
    #   call_id   = ...["id"]
    #   func_name = ...["function"]["name"]
    #   args      = json.loads(...["function"]["arguments"])
    #               ← 注意 arguments 是字符串，必须 json.loads！
    # TODO-3：根据 func_name 执行对应的函数（这里只有 calculator 一个），
    #         拿到结果 result 并打印。
    #         提示：calculate 的参数叫 expression，args["expression"] 取出来传进去。
    result = None  # TODO-3：这里应该是计算结果

    # ── 第 C 步：第二轮请求（把结果喂回给模型）─────────────
    # 要补发两条消息：
    #   1) msg_a 原样（模型的"申请书"，响应里的对象直接复用即可）
    #   2) 工具结果：
    #      {"role": "tool",
    #       "tool_call_id": call_id,   ← 必须和第 B 步取出的 id 对得上！
    #       "content": str(result)}
    # TODO-4：发送 [system, user, msg_a, 工具结果消息]（tools 传不传都行），
    #         打印模型的最终回答 choices[0].message.content
    pass


if __name__ == "__main__":
    main()
