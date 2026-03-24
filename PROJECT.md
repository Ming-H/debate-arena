# DebateArena 项目文档

## 项目概述

DebateArena 是一个基于 Claude 的多智能体辩论系统，通过让多个 AI 辩手就争议性话题进行多轮辩论，帮助用户深入理解复杂问题的不同视角。

**核心目标：**
1. 多立场辩论 - 创建支持不同立场的 AI 辩手
2. 结构化流程 - 主持人引导的有序辩论流程
3. 智能评判 - 基于论点质量的客观评价系统
4. 可扩展性 - 易于添加新话题和新辩手人设

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      Arena (竞技场)                      │
│  - 协调整个辩论流程                                      │
│  - 管理辩论状态                                          │
│  - 生成最终报告                                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────────────────────────┐  │
│  │  Moderator   │  │         Debaters (辩手)          │  │
│  │  (主持人)    │  │  ┌─────────┐ ┌─────────┐         │  │
│  │              │  │  │   Pro   │ │   Con   │         │  │
│  │ - 引导流程   │  │  │ (正方)  │ │ (反方)  │         │  │
│  │ - 控制轮次   │  │  └─────────┘ └─────────┘         │  │
│  │ - 维持秩序   │  │  - 生成论点                      │  │
│  │ - 总结阶段   │  │  - 反驳对手                      │  │
│  └──────────────┘  │  - 结辩陈词                      │  │
│                    └─────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Judge (评判系统)                    │   │
│  │  - 论点质量评估 (1-10分)                         │   │
│  │  - 逻辑一致性检查                                │   │
│  │  - 证据充分性分析                                │   │
│  │  - 最终结论生成                                  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Debater (辩手)

**位置：** `debate_arena/core/debater.py`

**职责：**
- 根据立场生成论点
- 回应对方论点（反驳）
- 生成结辩陈词

**数据类：**

```python
@dataclass
class Persona:
    """辩手人设配置"""
    name: str                # 姓名
    description: str         # 角色描述
    background: str          # 背景经历
    argument_style: str      # 论辩风格

@dataclass
class Argument:
    """单个论点"""
    content: str             # 论点内容
    stance: Stance           # 立场 (PRO/CON/NEUTRAL)
    debater_name: str        # 辩手姓名
    round_num: int           # 轮次编号
    is_rebuttal: bool        # 是否为反驳
    target_stance: Optional[Stance]  # 针对的立场
```

**主要方法：**
- `generate_opening_statement(topic: str) -> Argument` - 生成开篇陈词
- `generate_rebuttal(topic, opponent_arguments, round_num) -> Argument` - 生成反驳
- `generate_closing_statement(topic, my_arguments, opponent_arguments) -> Argument` - 生成结辩

### 2. Moderator (主持人)

**位置：** `debate_arena/core/moderator.py`

**职责：**
- 宣布辩题和规则
- 控制发言顺序
- 总结每轮要点
- 宣布辩论结束

**主要方法：**
- `open_debate(topic: str, debaters: list) -> str` - 开场致辞
- `summarize_round(topic, round_num, arguments) -> str` - 轮次总结
- `close_debate(topic, all_arguments) -> str` - 结束致辞

### 3. Judge (评判系统)

**位置：** `debate_arena/core/judge.py`

**职责：**
- 评估论点质量
- 分析逻辑一致性
- 检查证据质量
- 生成最终结论

**数据类：**

```python
@dataclass
class ArgumentScore:
    """论点评分"""
    content: str              # 论点内容
    argument_strength: int    # 论点强度 (1-10)
    evidence_quality: int     # 证据质量 (1-10)
    logical_consistency: int  # 逻辑一致性 (1-10)
    clarity: int              # 表达清晰度 (1-10)
    total_score: int          # 总分 (1-10)
    reasoning: str            # 评分理由

@dataclass
class DebateVerdict:
    """辩论裁决"""
    topic: str
    winner: Optional[str]     # "pro", "con", 或 None (平局)
    summary: str
    pro_scores: list[ArgumentScore]
    con_scores: list[ArgumentScore]
    best_argument: Optional[ArgumentScore]
    final_analysis: str
```

**评估维度：**
| 维度 | 描述 | 评分标准 |
|------|------|----------|
| Argument Strength | 核心观点的说服力 | 1-10分 |
| Evidence Quality | 事实、数据的引用 | 1-10分 |
| Logical Consistency | 推理严密性 | 1-10分 |
| Clarity | 表达清晰度 | 1-10分 |

**主要方法：**
- `evaluate_argument(argument: Argument) -> ArgumentScore` - 评估单个论点
- `render_verdict(topic, pro_arguments, con_arguments) -> DebateVerdict` - 生成最终裁决

### 4. Arena (竞技场)

**位置：** `debate_arena/core/arena.py`

**职责：**
- 初始化辩论配置
- 协调各组件交互
- 记录辩论过程
- 输出最终报告

**数据类：**

```python
@dataclass
class DebateResult:
    """辩论结果"""
    topic: str
    rounds: int
    transcript: list[str]      # 完整记录
    verdict: Optional[DebateVerdict]
    timestamp: str

    @property
    def report(self) -> str     # 格式化报告
```

**主要方法：**
- `run() -> DebateResult` - 运行完整辩论

## 辩论流程

```
1. 初始化阶段
   ├── 定义辩题
   ├── 创建辩手（PRO 和 CON）
   └── 设置轮次限制

2. 开场阶段
   ├── 主持人宣布辩题
   ├── 介绍辩手
   └── 各方阐述立论

3. 辩论阶段 (N 轮)
   ├── PRO 发言
   ├── CON 发言
   └── 主持人总结本轮

4. 结辩阶段
   ├── PRO 结辩
   └── CON 结辩

5. 评判阶段
   ├── 评估所有论点
   ├── 计算平均分
   └── 生成分析报告
```

## API 文档

### 基础使用

```python
from debate_arena import Arena

# 创建竞技场
arena = Arena(
    topic="人工智能是否应该受到监管？",
    rounds=3,              # 辩论轮次
    api_key="your_key",    # Anthropic API Key
    model="claude-3-7-sonnet-20250219",  # 可选模型
)

# 运行辩论
result = arena.run()

# 获取报告
print(result.report)
```

### 进阶配置

```python
from debate_arena import Debater, Stance, Arena
from debate_arena.core.debater import Persona

# 自定义辩手人设
custom_persona = Persona(
    name="Dr. Alice Smith",
    description="AI伦理专家",
    background="斯坦福大学计算机科学博士",
    argument_style="使用案例研究和框架分析"
)

# 创建自定义辩手
pro_debater = Debater(
    stance=Stance.PRO,
    persona=custom_persona,
    api_key="your_key"
)
```

### 使用预设人设

```python
from debate_arena.personas import PERSONAS, get_persona

# 查看可用人设
print(PERSONAS.keys())
# dict_keys(['pro_default', 'con_default', 'economist_pro',
#            'economist_con', 'scientist_pro', 'scientist_con'])

# 获取特定人设
economist = get_persona("economist_pro")
```

## 使用示例

### 示例 1：气候变化辩论

```bash
# 设置 API Key
export ANTHROPIC_API_KEY="your_key_here"

# 运行示例
python examples/climate_debate.py
```

### 示例 2：验证结构（无需 API）

```bash
python examples/verify_structure.py
```

## 开发状态

### 已完成
- [x] 核心组件实现 (Debater, Moderator, Judge, Arena)
- [x] 基础测试覆盖
- [x] 预设人设系统
- [x] 完整辩论流程

### 待改进
- [ ] 扩展测试覆盖率
- [ ] 添加更多预设人设
- [ ] 支持三方辩论
- [ ] 添加辩论历史保存功能
- [ ] 实现辩论回放功能
- [ ] 添加 Web UI

## 项目结构

```
debate-arena/
├── debate_arena/
│   ├── __init__.py           # 主入口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── debater.py        # 辩手实现
│   │   ├── moderator.py      # 主持人实现
│   │   ├── judge.py          # 评判系统实现
│   │   └── arena.py          # 竞技场实现
│   └── personas/
│       ├── __init__.py
│       └── presets.py        # 预设人设
├── tests/
│   └── test_arena.py         # 测试文件
├── examples/
│   ├── climate_debate.py     # 气候变化辩论示例
│   └── verify_structure.py   # 结构验证脚本
├── pyproject.toml            # 项目配置
├── README.md                 # 项目说明
└── PROJECT.md                # 本文档
```

## 技术栈

- **语言**: Python 3.11+
- **AI 模型**: Claude (Anthropic API)
- **依赖管理**: pip / pyproject.toml
- **测试框架**: pytest
- **代码风格**: black, ruff

## 环境配置

### 安装依赖

```bash
# 开发环境
pip install -e ".[dev]"

# 生产环境
pip install -e .
```

### 配置 API Key

```bash
# 方式1: 环境变量
export ANTHROPIC_API_KEY="your_key_here"

# 方式2: .env 文件
echo 'ANTHROPIC_API_KEY=your_key_here' > .env
```

## 开发指南

### 添加新预设人设

编辑 `debate_arena/personas/presets.py`:

```python
PERSONAS: Dict[str, Persona] = {
    # ... 现有人设 ...
    "my_persona": Persona(
        name="Your Persona Name",
        description="Brief description",
        background="Background info",
        argument_style="Argumentation style"
    ),
}
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_arena.py::test_arena_initialization -v
```

### 代码风格检查

```bash
# 格式化代码
black debate_arena/

# 代码检查
ruff check debate_arena/
```

## 常见问题

**Q: 如何更换 Claude 模型？**
```python
arena = Arena(
    topic="Your topic",
    model="claude-3-opus-20240229"  # 使用其他模型
)
```

**Q: 如何增加辩论轮次？**
```python
arena = Arena(topic="Your topic", rounds=5)  # 5轮辩论
```

**Q: 如何获取原始辩论记录？**
```python
result = arena.run()
raw_transcript = result.transcript  # list[str]
```

## 许可证

MIT License
