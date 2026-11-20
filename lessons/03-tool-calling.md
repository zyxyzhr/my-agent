# 第 3 课：第一次工具调用（全课核心）

> 预计 60 分钟｜动手文件：`agent_v1.py`｜前置：第 2 课

## 一、目标
手写工具调用的 4 步闭环。完成后你能逐条讲清楚"模型调用一个工具"的完整旅程。

## 二、理论（10 分钟读完）
**模型执行不了任何代码，它只会生成文本。**"调用工具"是一个 4 步闭环：

    ① 请求里告诉模型：你有这些工具（TOOLS：名字 + 描述 + 参数格式）
    ② 模型想用了 → 它不生成回答，生成特殊结构：
       message.tool_calls = [{"id", "function": {"name", "arguments"(JSON 字符串!)}}]
    ③ 你的代码解析 ②，【真的执行函数】，拿到结果
    ④ 结果以 role="tool" 消息发回（并带上 ② 那条消息原样）
       模型看到结果 → 生成最终回答

**模型只"申请"，代码才"执行" —— 这就是 Agent 的本质。**

三个协议细节（必背）：
1. `arguments` 是 JSON **字符串**，必须 `json.loads`
2. role=tool 消息的 `tool_call_id` 必须与对应 tool_calls 的 id **对上**——它是对账编号，模型一轮可能申请多个工具
3. 孤儿 tool 消息（对应的申请书被切掉了）→ **API 协议层直接拒收（400 错误），请求到不了模型**

**安全**：模型生成的 arguments 是"不可信输入"，绝不能直接 `eval`（模型说 `import os; ...` 就会被执行）。
本课的 `calculate` 用 AST 白名单（只允许数字 + `+ - * / **` 和括号）——读懂它为什么安全。

## 三、任务
打开 `agent_v1.py`，完成 4 个 TODO（协议流程，提示都在注释里）：

- **TODO-1** 第一轮请求：[system, user] + TOOLS，打印原始响应（你第一次看到 tool_calls）
- **TODO-2** 从 `tool_calls[0]` 取出 id / name / arguments（json.loads！），打印
- **TODO-3** 执行 `calculate`，拿到结果
- **TODO-4** 第二轮请求：[system, user, ②那条消息原样, {role:"tool", tool_call_id, content: 结果}]，打印最终回答

运行：`python agent_v1.py`

## 四、验收
- [ ] 最终答案 399（默认问题：17*23+8）
- [ ] 第一轮响应的 message 里能找到 `tool_calls`，`finish_reason` 是 `"tool_calls"`（不是 "stop"）
- [ ] 换问题 `(3+5)*2**4等于多少？`，得到 160
- [ ] 进阶观察：问 `17+*8等于多少？`，看模型怎么处理歧义输入（可能一轮并行算出两种解释）

## 五、理解题
1. 模型生成 tool_calls 的那一刻，计算器执行了吗？
2. role=tool 消息为什么要带 tool_call_id 且必须对上？（想一步：模型一轮申请两个工具呢？）
3. arguments 为什么是字符串而不是 JSON 对象？（想：模型本质上只能输出什么？）
4. 如果模型在 ① 偷懒不调工具、直接心算给了答案，怎么办？

## 六、常见坑
- 回传时直接复用响应里的 message 对象（它的 content 可能是 null，正常）
- 工具结果要 `str(result)`——tool 消息的 content 必须是字符串
- 工具声明里 description 的质量，直接决定模型会不会用、用得对不对
