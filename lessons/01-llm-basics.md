# 第 1 课：LLM 的裸形态

> 预计 45 分钟（含动手）｜动手文件：`hello.py`｜前置：完成 README「快速开始」

## 一、目标
用裸 HTTP 发出第一个 LLM 请求，亲眼看到请求与响应的原始 JSON。
完成后你能讲清楚："LLM 服务到底是什么。"

## 二、理论（5 分钟读完）
三个认知：

1. **LLM 服务就是一个普通的 HTTP 服务**：你发 JSON（模型 + 问题），它回 JSON（回答 + token 统计）。
2. **它是无状态的**：两次请求之间，服务器什么都不记得，每次请求都是全新的一次独立计算。
   这不是缺陷，是刻意设计：任何机器都能处理任何请求（扩容容易）、机器挂了不丢状态、客户端完全控制发什么。
   **一切"记忆"都是客户端（你）构造的 —— 这是所有 Agent 设计的第一性原理。**
3. **messages**：请求体核心字段，一个列表，每个元素 `{"role", "content"}`。
   role 有三种：`system`（规则/人设，放最前，可选）、`user`（你）、`assistant`（模型之前的回答）。

## 三、任务
打开 `hello.py`，完成 3 个 TODO（提示都在注释里）：

- **TODO-1** 往 messages 列表填一条 user 消息："只回复两个字：收到"
- **TODO-2** 用 `urllib.request.Request` 构造请求（URL、data、两个 header）
- **TODO-3** 取出 `data["choices"][0]["message"]["content"]` 打印，顺手打印 `data["usage"]`

运行：`python hello.py`

## 四、验收
- [ ] 终端打印出模型回答（两个字"收到"）
- [ ] 你能在原始响应中指出：`choices[0].message.content` / `usage.prompt_tokens` / `finish_reason` 各是什么
- [ ] 选做实验：在 user 消息前加 `{"role": "system", "content": "用四川口音回答"}` 再跑一次，观察变化

## 五、理解题（通过才进下一课）
1. 你发完这次请求，紧接着再发一次，模型"记得"你刚才问的吗？为什么？
2. 看你收到的完整 JSON，message 对象除了 content 还有哪些字段？（有的字段可能是 null 但依然存在——说明什么？）
3. 一句话的提问消耗几十 prompt_tokens，两个字回答的 completion_tokens 也是几十——为什么？（提示：两点，输入有开销；输出里含思考 token）
4. 选做：加了 system 消息后 prompt_tokens 涨了多少？说明什么？

## 六、常见坑
- `Authorization` 头是 `"Bearer " + 密钥`，**中间一个空格**，漏了 → 401
- `json.dumps` 不加 `ensure_ascii=False`，中文变 `\uXXXX` 转义——模型能懂但 token 费得多
- 不要把 config.json 内容发给任何人（密钥在里面）
- 彩蛋：响应里的 `model` 字段可能暴露模型的"真身"——接口层的模型名可以是别名
