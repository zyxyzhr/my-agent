# 第 6 课：工程化加固（最后一课）

> 预计 60 分钟｜动手文件：`llm_client.py` + `agent.py` + `test_lesson6.py`｜前置：第 5 课

## 一、目标
给 Agent 加上生产级三件套：重试、流式、日志。完成后你能讲清楚手写 Agent 与 LangChain 这类框架的本质关系。

## 二、理论（10 分钟读完）

**1. 重试 —— 分清错误类别**
- 瞬时（值得重试）：429 限流、5xx 服务故障、网络错误/超时
- 永久（重试无用）：其他 4xx（请求错/认证失败）——同样的请求，服务端判定永远一样
- **重试的本质 = 赌"两次请求之间世界的状态会改变"**
- 退避用指数（1s→2s→4s）而非固定：固定间隔下 1000 个客户端的重试会同一时刻砸回来，
  服务器再次倒地，无限塌方循环（重试风暴）。指数退避让重试时刻"去同步"，真实系统还会加随机抖动。
- 最后的异常必须抛出，不能吞掉。

**2. 流式（SSE）—— 让第一个字几秒内出来**
- 非流式：模型全部想完你才看到第一个字；流式：第一个 chunk 几秒内到达，边生成边显示
- HTTP 响应体是无边界的字节流，SSE 用文本约定做"事件分帧"：每行 `data: {json}`，以 `data: [DONE]` 结束
- 两个坑：① 有的 chunk 的 `choices` 是空列表，取之前判空；② 思考模型先流 `reasoning_content` 再流 `content`
  （AI 产品的"正在思考…"动画就是显示 reasoning 流）
- 代价：content 被切成碎片，调用方要拼接；总时长基本不变，降的是"首字延迟"
- 流式 tool_calls 需要跨 chunk 拼 delta——进阶话题，知道存在即可

**3. 日志 —— print 给用户，logging 给运维**
- print = 界面输出；logging = 带时间戳/级别，可落文件、可按级别过滤
- 过程性 print（轮次/token 数/工具调用）→ logging.info；最终回答 → print

**4. 大总结 —— 框架的真相**

    LangChain 组件            你手写里的对应物
    ─────────────────────────────────────────
    ChatModel 封装             llm_client.py（chat/retry/stream）
    @tool 装饰器 + 注册表       TOOLS + FUNCTIONS
    AgentExecutor              run_agent 的 while 循环
    ConversationBufferMemory   history + trim_history + 持久化
    callbacks/logging          第 6 课的 logging

**没有本质区别**——框架只是"循环 + 工具注册 + 上下文管理"更完整、更通用的版本。
从零写一遍的价值：读得懂任何框架源码 / 抽风时知道 debug 哪层 / 任何环境 30 分钟手搓最小 Agent。

## 三、任务
- **TODO-10** `llm_client.py` 的 `chat_with_retry`（注释里有提示结构）
- **TODO-11** `llm_client.py` 的 `stream_chat`（生成器函数，body 里含 yield）
- **TODO-12** agent.py 的过程性 print 换 logging.info（文件顶部 basicConfig）
- **TODO-12b** run_agent 里 chat 调用换成 chat_with_retry
- **TODO-13** main() 加 `stream ` 前缀入口：流式逐字打印回答（注意 `flush=True`）

## 四、验收
- [ ] `python test_lesson6.py` 全部 4 项 PASS（流式拼接 + 重试退避）
- [ ] 手工体验：运行 agent.py，输入 `stream 用三个短句介绍你自己`，对比流式 vs 非流式的体感差异
- [ ] 日志行带时间戳（形如 `2026-01-01 10:00:00 [INFO] ...`）

## 五、理解题
1. 哪些 HTTP 状态码该重试、哪些不该？401 为什么重试一百次也没用？
2. 退避为什么是指数而不是固定间隔？（站在"1000 个客户端同时收到 429"的角度想）
3. SSE 为什么长成 "data: " 行 + [DONE] 的样子？（想：HTTP 字节流有天然的消息边界吗？）
4. 思考模型的流里 reasoning_content 和 content 谁先？这对"流式体验"意味着什么？
5. 终极问题：你手写的 Agent 和 LangChain，**本质区别是什么**？

## 六、常见坑
- `except` 后吞掉异常（最后假装成功）——最后的异常必须 raise
- 流式打印不加 `flush=True`，输出被重定向/录制时逐字效果消失
- 别把最终回答打进日志、也别用 print 打运维状态——两者分工明确
