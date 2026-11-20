# 第 2 课：对话就是上下文

> 预计 40 分钟｜动手文件：`chat.py`｜前置：第 1 课

## 一、目标
做出一个多轮聊天 REPL，亲手造出"记忆的错觉"。

## 二、理论（5 分钟读完）
**多轮对话 = 每轮把【全部历史 + 新问题】整个发过去**：

    第1轮发: [system, user1]                             → 模型回 asst1
    第2轮发: [system, user1, asst1, user2]                → 模型回 asst2
    第3轮发: [system, user1, asst1, user2, asst2, user3]  → ...

- 模型没有记忆，是我们每轮把之前的对话原样发回去。
- 这个列表叫 **上下文（context）**，每轮 +2 条（你的话 + 模型上轮的回答）。
- system 是"规则层"，user 是"输入层"——同样的输入、不同的 system，人格就不同。
- 注意：**第 N 轮发送时刻，历史里只有 N-1 条 assistant 回答**（模型还没回答最新的 user 消息）。

## 三、任务
打开 `chat.py`，完成 3 个 TODO：

- **TODO-1** `chat(messages)` 函数（把 hello.py 的发请求代码搬进来，return content，不 print）
- **TODO-2** main() 多轮循环：history 列表，每轮 input → 追加 user → chat([system]+history) → print → 追加 assistant
- **TODO-3** 输入 "exit" 退出

运行：`python chat.py`

## 四、验收
- [ ] **记忆实验**：先告诉它你的姓名/单位，随便聊一两轮别的，再问"我叫什么？在哪工作？"——模型答对
- [ ] **长度验证**：每次调 chat 前打印 `len([system消息] + history)`，聊满 3 轮应看到 2、4、6
- [ ] 输入 "exit" 能干净退出

## 五、理解题
1. 第 3 轮请求发出去的 messages 列表里有几条？分别是什么 role？（公式：第 N 轮发 1 system + N user + (N-1) assistant = 2N 条）
2. 每多聊一轮，请求体怎么变化？对 token 费用意味着什么？
3. 模型自己说过的话如果不追加进 history，下一轮会怎样？
4. 这个"记忆"物理上存在哪里？进程关掉会怎样？

## 六、常见坑
- "一条消息的字段"（role/content）≠ "messages 列表里几条消息"——两个层次别混
- `reasoning_content` 是**响应**里才有的字段（思考模型的思考过程）；追加 assistant 历史时只取 `content`
- system 每次调用都要重新拼在最前面，不是放一次进 history 就完事
