# Python 运行层接入 — 0.3.3-alpha

本页从可运行示例开始，说明怎样替换为自己的模型、审查、执行和核验回调。先了解组件协作可读[架构说明](design.zh-CN.md)；需要设置周期唤醒和作业观察可读[监视接入](monitoring.zh-CN.md)。

## 从哪里开始

- agent 的入口：[核心 skill](../skills/agent-workflow/SKILL.md)。
- 各模块输入输出：[模块约定](../skills/agent-workflow/references/modular-workflow.md)。
- 运行核心：[engine.py](../workflow_runtime/engine.py)、[SQLite存储](../workflow_runtime/store.py)及[策略检查](../workflow_runtime/policy.py)。
- LangGraph编排：[langgraph_adapter.py](../workflow_runtime/langgraph_adapter.py)。
- 可运行合成回调：[demo.py](../workflow_runtime/demo.py)。

## 先运行无需模型的样例

在仓库根目录，使用 Python 3.11 或更新版本；运行目录必须放在公开仓库之外：

```bash
python scripts/demo_workflow.py --workspace ../workflow-demo-private --steps 6
python scripts/demo_workflow.py --workspace ../workflow-demo-private --steps 6
python scripts/demo_workflow.py --workspace ../workflow-demo-private --steps 6
```

三次唤醒分别完成一轮。前两轮只处理大小写，保留了错误的空格；第三轮改用“去空格并转换大小写”，核验后完成。每次重新打开同一数据库，而不是重新创建任务或重置成本。回调事先写明了这条合成轨迹，所以它证明模块衔接与接续机制，不能证明模型自主发现了更优方法。

| 第几次调用 | 返回状态 | 保留内容 |
|---|---|---|
| 第一次 | `ready`、`cycles: 1`、`spent: 1` | 首次失败结果和转向决定 |
| 第二次 | `ready`、`cycles: 2`、`spent: 2` | 第二次失败和累计尝试 |
| 第三次 | `done`、`cycles: 3`、`spent: 3` | 通过的输出与核验、任务完成决定 |

成功标签为 `["alpha", "beta", "gamma"]`。运行目录保存 `workflow.sqlite3`、每次尝试的 JSON 回执和标签文件；`spent` 是合成计费单位，每次执行计 1，不代表金额。

已知例行任务可用另一个新目录：

```bash
python scripts/demo_workflow.py --workspace ../workflow-routine-private --effort routine --steps 3
```

一次调用返回 `done`、`cycles: 1`。例行任务核验通过即结束；失败仍反思，转向后恢复研究与独立审查。两条路线不能用于相互绕过审查。

需使用真实 LangGraph 时，在独立虚拟环境中安装可选依赖：

```bash
python -m venv ../workflow-demo-env
../workflow-demo-env/bin/python -m pip install -r docs/requirements-langgraph.txt
../workflow-demo-env/bin/python scripts/demo_workflow.py --workspace ../workflow-graph-private --steps 6 --langgraph
```

重复最后一条命令可继续同一任务；Windows环境的Python路径不同。顶层LangGraph版本固定，传递依赖未完全锁定。安装依赖不会启用定时任务。回调默认不调用云端服务；启用跟踪、模型或搜索服务前，需明确其数据去向。

## 替换为自己的模块

`Workflow(directory, contract)`创建新任务；`Workflow(directory)`接续已有任务。契约包含目标、验收项ID、真实授权来源、允许动作和明确限制。`effort`默认deliberate；已知、廉价、可逆任务可由可信宿主在创建时显式选routine。字段、默认值和调整边界见[参数说明](../skills/agent-workflow/references/parameters.md)。已存在的契约不能通过再次初始化改大。

每个回调签名为 `handler(snapshot, workspace)`，返回：

```json
{"data": {"module_specific_fields": "see module references"}, "cost": 0}
```

`cost`使用任务自己定义的统一费用单位；只有确知没有该类花费时才填0，未知用null。回调实际耗时另计为seconds，两种单位不相加。同步执行回调必须等任务结束，返回匹配attempt_id的回执和保存证据，不能把“已提交远程任务”当“已执行完成”。

调用 `tick(handlers)`最多执行一个回调。LangGraph适配器只路由当前所需模块，每次唤醒有节点数上限；它使用同一SQLite状态，不另设一份可回放执行动作的图状态。定时唤醒或完成事件仍由已有宿主负责。

[agent_bridge.py](../workflow_runtime/agent_bridge.py)提供模型无关的接入桥。宿主先实现下面四个回调，再注册为引擎需要的六个模块。以下是接口示意，不是已接好模型服务的独立程序：

```python
from workflow_runtime import Workflow
from workflow_runtime.agent_bridge import make_agent_handlers

handlers = make_agent_handlers(reasoner, reviewer, execute, verify)
workflow = Workflow(task_directory)  # 打开已建立的同一任务
result = workflow.tick(handlers)    # 最多运行当前一个模块
```

| 回调 | 输入 | 必须承担什么 |
|---|---|---|
| `reasoner(request)` | 模块说明、任务约定、当前上下文、必需返回字段 | 研究、拟案与反思；按需调用只读工具；返回结构化决定及实际费用 |
| `reviewer(request)` | 同类请求，模块为 REVIEW | 独立检查确切方案，返回 merit、feasibility、acceptance、approved 与 reason |
| `execute(snapshot, workspace)` | 已通过方案和当前 attempt token | 执行真实动作，等待完成，保存输出并返回匹配身份的回执 |
| `verify(snapshot, workspace)` | 回执、方案和保存产物 | 检查每个 acceptance ID，返回 valid、improved、goal_met、checks 与 evidence |

前两个回调使用 `{data: {...}, cost: ...}` 格式，执行和核验也遵守同一外层约定。具体阶段字段见[模块约定](../skills/agent-workflow/references/modular-workflow.md)。桥接请求只载入当前说明、当前状态与最近四次尝试；它不内置模型传输、认证或 Deep Agents 连接器。模型超时与工具权限由宿主落实。

### 给规划与审查接入查证工具

`reasoner(request)` 和 `reviewer(request)` 的具体实现由宿主提供。它们可以绑定项目只读搜索、官方文档检索或论文搜索；PLAN、REVIEW、REFLECT 也能按需调用这些工具，不必等待下一轮 RESEARCH。桥接层自身不联网，也不内置这些客户端。

例如，PLAN 发现接口条件不明时，可由宿主读取相关调用方和文档，将来源、位置、观察与局限作为 `data.basis` 返回；REVIEW 再判断该依据是否支持确切方案。该字段是可选记录，不会触发自动搜索或证明科学有效性。工具调用时间包含在回调耗时中，宿主应将实际模型与检索费用汇总到同一 `cost` 单位，并为每次调用设置自己的超时。

只给研究、规划和审查所需的读取权限；不要让它们绕过 EXECUTE 实施方案。真实诊断运行或预实验是需要准入的动作。外部查询最小化，避免携带私有项目内容；工具不可用时返回具体缺口，而不是声称已经检索。

## 恢复与控制

- 创建任务默认只规划。宿主用 `set_mode("execute", source)`记录实际用户授权后，执行阶段才允许启动；`pause`、`plan_only`和`stop`同样来自可信宿主，不从日志解析。
- SQLite事务把状态快照与事件一起提交。调用模块前保存claim；第二次唤醒看到未结束claim，会要求核对，绝不自动抢占或重跑。
- 若在执行后、提交前崩溃，宿主须先确认旧worker已结束，并读取同一idempotency key的真实回执。再调用 `reconcile(token, output, elapsed_seconds)`。不能因为PID消失或时间过去就宣称没有执行。
- 回调抛错时保存错误和已观察时间；费用不猜测。完整结果尚未确认，成本只是已核部分，不能称最终总成本。回执明确cost=null时，后续动作阻止，待 `resolve_cost(cost, evidence)`核对实际费用。
- `unblock(reason)`用于已解决的非执行前置条件；`replan(reason)`重新进入研究，但保留成本、尝试与停滞历史。不能用这两个接口清除未结束claim。
- WAIT状态需要明确唤醒条件，由宿主判断条件已发生后再unblock。结束目标与结束一次尝试是两回事。

`reconcile`是受信宿主接口，不会自行证明旧进程退出；错误调用可能与旧worker冲突。本地数据库保存在用户选择的运行目录中，不是多机分布式锁。新建另一套目录仍能形成独立数据库，宿主必须把同一campaign绑定到同一真实账，不能靠换目录重置限制。

## 减少无效循环和资源浪费

| 机制 | 已实现的行为 | 仍需判断的部分 |
|---|---|---|
| 重复识别 | 按方向、实际修改、输入与评价指纹拦截重复，改显示名不绕过 | 不同文字可能描述同一变化，语义查重仍需审查 |
| 停滞窗口 | 连续无改进达到任务限制后，拒绝同方向继续变体 | 换方向并不保证更好，更不保证全局最优 |
| 研究成本 | 每轮及回调都计费，限制总轮数、同方向次数、已用费用和时间 | API调用须有自己的超时；引擎不能杀死任意Python回调 |
| 资源准入 | 启动前检查剩余费用、估计时间、磁盘可用量和运行目录大小 | 估计不是保证，真实作业还需硬限时与配额 |
| 经验沉淀 | 只保留有核验结果、复用理由和证据的可选教训，当前视图最多8条 | 教训质量与适用范围需要领域判断 |
| 上下文 | 当前快照与事件分离，不递归复制父历史；单模块返回限制32KiB | 外部文档/模型上下文需宿主按需检索 |
| 保存策略 | 不自动删除结果；空间不足停下并保留原证据 | 宿主按明确保留政策归档可重建输出 |

资源扫描有目录项数量上限，避免为了监视又递归扫描巨大树。只在启动前扫描这个参考运行目录，不在相邻推理阶段重复遍历，也不扫描用户数据盘。证据由相对路径和SHA绑定，单个直接证据文件限1MiB；大产物可用小manifest引用，但大产物本身的完整核验须由领域核验器负责。

## 本地进程适配器的实际边界

[local_executor.py](../workflow_runtime/local_executor.py)提供POSIX本地命令执行：不使用shell，独立进程组，超时或日志超量即终止进程组，保存失败回执。同一attempt key对应不同命令会拒绝；已有完整回执可重用，只有intent没有回执时拒绝重启。

它只限制运行时间和**最终保留日志**。轮询间隔内日志可能短暂超量，命令另写的文件、脱离进程组的进程、内存/GPU/网络都不受这个适配器约束。需要容器或系统配额来提供这些保证。日志被截断时会明确标记，并记录终止后观察到的字节量，不声称保存了原始完整日志。

运行目录应由受信用户独占；它不是恶意代码沙箱。暂停会阻止下一模块，但不能靠状态字段自动取消已经运行的外部任务，取消由执行适配器负责。

## 验证和开源边界

参考测试覆盖持久状态、重复唤醒、执行后崩溃、回执核对、暂停、重复方向、结果身份、费用未知和本地超时。实际范围见[验证记录](../evals/validation.md)。这些测试没有证明agent推理质量、节约比例或科研效果。

源码与借鉴来源见[来源记录](../research/sources.json)，公开包要求见[贡献指南](../CONTRIBUTING.md)。真实运行目录应保留在公开仓库之外。
