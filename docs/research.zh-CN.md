# 调研：长期 agent 自动接续应该怎样包装

调研日期：2026-11-10。目标是通用长期任务，训练科研只是示例。范围是公开资料和源文件静态审阅，未安装或实际运行下列工作流，也没有进行效果排名。

## 判断

最合适的第一版是 **skill 为入口的轻量工作流工具包**，以 GitHub 仓库为发布单位，同时提供教程、任务文件模板和行为验收案例。无需先做新的 agent 平台。

这类需求包含两件事：帮助用户把模糊目标设计成工作流，以及让 agent 每次唤醒时接着正确的步骤做。首版可以在一个聚焦的 skill 中提供这两种入口，但应清楚区分“设计完成”和“真正启用自动运行”。

## 搜索与核验方式

按用户指定的 find-skills：先看 skills.sh 排行，再用 Skills CLI 检索 `planning with files`、`autonomous workflow`、`verification reflection`、`verification-before-completion`、`compound-engineering`。从高相关结果中读取固定 commit 的实际 SKILL.md/辅助文件，并通过 GitHub API 检查来源、star、许可证和 commit。

安装数来自 CLI 当时返回，不是活跃用户数或质量证明；star 来自仓库 API，不是单个 skill 的 star。数字会变化。已读文件和 commit 记录在 [sources.json](../research/sources.json)。本地原始源码快照在忽略目录 research/evidence 中，不随发布包分发。

## 值得优先研究的 skills

| 方案 | 查得安装数 / 仓库 star | 能提供什么 | 对本需求的取舍 |
|---|---|---|---|
| [planning-with-files](https://skills.sh/othmanadi/planning-with-files/planning-with-files) | 48.5K / 27,978 | 文件计划、恢复、账本，以及可选自主/有界接续模式 | 最接近的基础；不是只有三份 Markdown。适合优先试用。真实作业身份、外部副作用和本项目验收仍需接入 |
| [verification-before-completion](https://skills.sh/obra/superpowers/verification-before-completion) | 270.4K / 315,305 | 要求用实际核验支撑完成声明 | 借鉴“证据先于声明”。原指令很强调本消息重新执行核验；昂贵评价应允许读取仍有效的保存证据，避免重复计算 |
| [executing-plans](https://github.com/obra/superpowers/tree/main/skills/executing-plans) | 本轮未核单项安装数 / 同上 | 按已有计划持续执行，保存可恢复记录 | 适合开发实现阶段；本次仅核其入口文件，未审完整依赖树，不直接整包嫁接 |
| [ce-compound](https://skills.sh/everyinc/compound-engineering-plugin/ce-compound) / [lfg](https://skills.sh/everyinc/compound-engineering-plugin/lfg) | 3.8K / 3.6K；仓库 26,006 | 将有价值经验保存成最便宜的长期形式；端到端开发路由 | 借鉴经验沉淀和已有授权下持续推进。lfg 的具体产物偏代码/PR，多阶段依赖不能视作通用调度器 |
| [nemo-rl-auto-research](https://skills.sh/nvidia/skills/nemo-rl-auto-research) | CLI 1.9K / 3,917 | 假设实验、日志、停止条件、环境选择 | NVIDIA 官方领域 skill，与原科研案例接近；依赖 NeMo-RL 语境和会话记忆，不直接解决通用数据/开发任务 |

前三类来源都是社区项目，不应因为热门而称为官方标准。NVIDIA 的项目来源已核为 NVIDIA 组织。NVIDIA 的 skills.sh 详情页在本次网页工具中打开失败；安装数使用 CLI 结果，具体内容以已成功获取的固定 commit 源文件为据。

名称最像的 `autonomous-workflow` 搜索结果只有约 8–34 次安装，本轮没有做深入源码核验，因此仅视作发现线索，不作为优先推荐或成熟替代品。

如要分别试用，可使用目录提供的安装形式（本轮没有执行安装）：

```bash
npx skills add othmanadi/planning-with-files@planning-with-files
npx skills add obra/superpowers@verification-before-completion
npx skills add everyinc/compound-engineering-plugin@ce-compound
npx skills add nvidia/skills@nemo-rl-auto-research
```

建议先选一个基础方案，在隔离的低成本任务里试用；把全部 skill 同时加载容易引入不同的执行、审批和结束规则。

## 相关但不只是 skill 的方案

**[Ralph Loop](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop)**：读取了官方插件仓库中的帮助文件和 stop-hook。它用 Stop hook 请求继续，支持迭代上限/完成标记；默认无限循环配置是可能的。适合明确出口的短迭代，不等同于跨重启调度或独立结果验收。实际 hook 检查最后的模型文本标记；不能把标记本身当作外部任务已经成功的证明。仓库 star 46,680，未核该插件单独安装量。

**[Karpathy autoresearch](https://github.com/karpathy/autoresearch)**：读取 README 和 program.md；其固定短训练预算、统一评价、结果 TSV 和保留/舍弃实验很贴近科研循环。但它针对专用训练环境，原指令包含无限实验以及用 git reset 丢弃未提升改动等约定。通用用户需要自己明确范围、停止条件和工作区处理。本原型仅作概念比较，不复制其代码或指令；本次 API 的 license 字段为 null，不据此猜测可再分发许可。仓库 star 99,713。

**[LangGraph](https://docs.langchain.com/oss/python/langgraph/persistence)**：官方文档介绍 checkpointer 和 store 的持久状态，是要做服务端恢复、事件驱动与多任务编排时的运行层选择。它比一个技能包重；图的持久化也不能自动让任意外部副作用只执行一次。仓库 star 44,726。本轮只读官方持久化说明和仓库元数据，未审框架实现。

**[Codex / ChatGPT Scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app)**：官方文档把周期/事件触发与 skill 的工作指令分开；同一聊天接续适用于需要上下文的任务。本机项目运行依赖机器、应用及文件可用。它可直接承担唤醒层，无需再造计时器。产品可用能力以当前工具和计划为准。

## 对我们原有流程的优化

原流程已经有真实进程、证据、失败记录和自动接续，最需要改的是组织方式：

1. **提示变短**：稳定行为放 skill，当前事实放 state，旧结论放事件索引。定时任务只指向它们，避免数万字历史随每次唤醒重放。
2. **避免递归历史**：父记录用路径/ID加内容身份引用，不把全部祖先 runtime 再嵌进新文件。保留原账和失败，精简的是读取视图。
3. **回调和巡检分工**：执行程序负责准确限时、即时收尾；agent 在里程碑解释与选择下一步；周期检查兜底漏回调和异常。
4. **用决定衡量反思**：必须产出保留、修复、补证、执行、等待或停止中的一个。重复写未知结论不是科研推进。
5. **账目与通知分开**：真实成本更新并不都要打扰用户；通知使用事件身份去重。
6. **先验证运行层能力**：文字要求不等于锁、幂等、超时已经实现；跨崩溃恢复要单独试验。

这些是通用设计建议，尚未迁移任何既有自动化配置，也不能据此声称提升了成功率或节省了多少成本。进一步的固定版本审阅与落实情况见[质量对标](quality-benchmarks.zh-CN.md)。

## 能否有独立开源价值

有，但应定位为一个明确组合和可复用实践，而不是声称发明了反思循环或自主 agent。planning-with-files 等已经有大量重叠能力。值得验证的差异是：跨开发/研究/数据的统一任务约定、对真实执行身份的接续、昂贵证据复用、明确不确定副作用、以及把反思变成行动的示例与评测。

如果用户只想改善自己的当前流程，优先精简现有 skill 和任务状态可能更省力。若目标是社区产品，就把这套通用核心与三个示例拿出来做小规模试用，收集实际失败再决定是否建设运行引擎。
