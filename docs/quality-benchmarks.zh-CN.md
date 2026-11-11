# 质量对标与落实情况

审阅日期：2026-11-10；当前版本：0.3.3-alpha；本表来源对标在0.1.1-alpha完成。选择标准是功能相关性与可核验的维护实践，star 仅帮助发现项目。以下数字属于整个仓库，不是单个 skill 的星数，也不证明效果。

这轮使用本机提供的 skill-creator 编写与验证技能；另把 Anthropic 的公开 skill-creator 作为固定版本的研究对象。两者不是同一份技能，也没有把第三方指令或工具整包搬入我们的发布包。

| 对标来源 | 仓库 star 快照 | 审阅重点 | 在本套件的落实 |
|---|---:|---|---|
| [planning-with-files](https://github.com/othmanadi/planning-with-files/tree/2362ca385ad74f061aa0e7b73f56543a4b7e6df2) | 27,978 | 文件恢复、完成门、eval 说明与 CI 配置 | 保留文件状态与恢复的基础模式；新增可重复的公开包检查与 CI 配置。已有恢复方案不是我们的新发明 |
| [Superpowers](https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7) | 315,305 | writing-skills、testing 文档：区分非模型测试与真实会话行为评测 | `tests/` 检查脚本与打包；`evals/` 保存行为规格。静态检查通过不写成 agent 通过率 |
| [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin/tree/dd9b7921c9c80498eba84994ff1b8e1e81dbc1db) | 26,006 | 真实调用方形态、越界评分、盲测新旧指令、减少过度设计 | 区分直接请求与定时唤醒；加入小修改、任务错选、设计而非执行等案例；要求观察实际动作与无关改动 |
| [Anthropic skills / skill-creator](https://github.com/anthropics/skills/tree/2c5958ecac7cee2b583967a2c4981d0f4a75c579/skills/skill-creator) | 191,456 | 渐进加载、真实任务、基线、输出审阅、时间/token、触发评测 | 入口保持聚焦、细节按需读取；输入和评分分开；记录结果身份与未知值；另设正负触发案例 |

来源对应的 commit、文件、字节数与 SHA-256 见 [sources.json](../research/sources.json)。这是列明文件的定向审阅，没有审计这些仓库的所有代码或复现其公布的成绩。项目的自报评测仅作为方法参考，不当作我们已获得的结果。

## 可复核的质量要求

| 要求 | 产物或检查 | 当前证据边界 |
|---|---|---|
| 技能可发现、安装后引用完整 | [核心 skill](../skills/agent-workflow/SKILL.md)、独立目录引用与 skill-creator 验证 | 格式/引用检查；发现准确率待测 |
| 规则不替用户扩大任务 | 设计与接续分流、授权来源、小任务按需简化 | 已写入；真实 agent 是否遵守待测 |
| 结果可核验，不靠措辞评分 | [22行为与7触发案例](../evals/prompts.json)、[独立评分标准](../evals/rubric.json) | 评测规格已备；不是29次测试通过 |
| 修改是否有效要有对照 | [评测方法](../evals/README.md)、[结果模板](../evals/result-template.json) | 新旧/无 skill 对照尚未运行 |
| 发布不混入用户材料 | [公开包检查器](../scripts/release.py)、显式文件清单、私有词外置、打包哈希 | 自动检查与逐文件审阅；无法证明任意敏感语义绝对不存在 |
| 维护者可复现基本检查 | [贡献指南](../CONTRIBUTING.md)、[离线测试](../tests/test_release.py)、CI 配置 | 本机结果见[验证记录](../evals/validation.md)；托管 CI 尚未执行 |

采用的是与当前产品相关、能检查的做法。尚无依据宣称“达到这些项目全部质量标准”或“新指令让任务成功率提高”。0.2版已验证合成本地崩溃恢复、并发claim和LangGraph接续；真实调度器、分布式锁、通知交付及agent行为仍待验证。

## 隐私与来源边界

公开 skill、模板、案例和测试使用通用描述或合成数据；不需要用户的私有代码、业务数据、机器路径、真实运行记录或内部成绩。调研源文件留在本地排除目录，只发布来源元数据与原创分析，不分发其源文件。新增源码用于通用发布检查与参考运行层，没有读取、改写或嵌入私有项目实现。

后续打磨以示例任务的实测失败为依据。先做最小配对评测，再按发现修正；不为追求文档厚度而增加规则、平台或常驻服务。

## 0.3版删减审查

本次补查Cursor第一性原理设计skill与ce-simplify-code的实际源码、参数与适用边界，详情见[必要性审查](necessity-audit.zh-CN.md)。没有把代码简化器当作文案评审，也没有照搬多agent评审队列。统一补齐[参数类型、默认值、调整与不支持项](../skills/agent-workflow/references/parameters.md)，并把机械接续从模型回调中移除。高星项目功能清单不能代替本项目用户需求；仍不声称已达到它们全部质量标准。
