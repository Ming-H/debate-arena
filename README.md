# DebateArena

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

### AI-Powered Multi-Agent Debate Simulation Framework

DebateArena is a sophisticated framework that simulates structured debates between AI agents. It enables deep exploration of complex topics through multi-round debates with different perspectives, guided by a moderator and evaluated by an intelligent judge.

### Features

- **Multi-Stance Debates**: Create AI debaters supporting PRO, CON, or NEUTRAL positions
- **Structured Flow**: Moderator-guided debate process with opening, rounds, and closing
- **Intelligent Judging**: Objective evaluation based on argument quality, evidence, and logic
- **Persona System**: Customizable debater personalities and argumentation styles
- **Full Transcript**: Complete debate history with scores and analysis

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Arena (Coordinator)                     │
│  - Coordinates entire debate process                         │
│  - Manages debate state                                      │
│  - Generates final report                                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────────────────────────┐      │
│  │  Moderator   │  │         Debaters                │      │
│  │  (Host)      │  │  ┌─────────┐ ┌─────────┐        │      │
│  │              │  │  │   PRO   │ │   CON   │        │      │
│  │ - Guide flow │  │  │ (For)   │ │(Against)│        │      │
│  │ - Control    │  │  └─────────┘ └─────────┘        │      │
│  │ - Summarize  │  │  - Generate arguments           │      │
│  └──────────────┘  │  - Rebut opponents              │      │
│                    │  - Closing statements           │      │
│                    └─────────────────────────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Judge (Evaluation System)               │   │
│  │  - Argument quality assessment (1-10 scale)          │   │
│  │  - Logical consistency check                         │   │
│  │  - Evidence sufficiency analysis                     │   │
│  │  - Final verdict generation                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Installation

```bash
pip install -e .
```

### Quick Start

```python
from debate_arena import Arena

# Create arena with a topic
arena = Arena(
    topic="Should AI development be regulated?",
    rounds=3,
    api_key="your-anthropic-api-key"
)

# Run the debate
result = arena.run()

# Get the report
print(result.report)

# Access detailed results
print(f"Winner: {result.verdict.winner}")
print(f"Summary: {result.verdict.summary}")
```

### Advanced Usage

#### Custom Debater Personas

```python
from debate_arena import Debater, Stance, Arena
from debate_arena.core.debater import Persona

# Create custom persona
custom_persona = Persona(
    name="Dr. Alice Smith",
    description="AI Ethics Expert",
    background="PhD in Computer Science from Stanford",
    argument_style="Uses case studies and framework analysis"
)

# Create debater with custom persona
pro_debater = Debater(
    stance=Stance.PRO,
    persona=custom_persona,
    api_key="your_key"
)

# Use in arena
arena = Arena(
    topic="AI regulation",
    pro_debater=pro_debater,
    rounds=3
)
```

#### Using Preset Personas

```python
from debate_arena.personas import PERSONAS, get_persona

# View available personas
print(PERSONAS.keys())
# dict_keys(['pro_default', 'con_default', 'neutral',
#            'economist_pro', 'economist_con',
#            'scientist_pro', 'scientist_con'])

# Get specific persona
economist = get_persona("economist_pro")
```

### Evaluation Dimensions

| Dimension | Description | Scale |
|-----------|-------------|-------|
| Argument Strength | Persuasiveness of core points | 1-10 |
| Evidence Quality | Quality of facts and data cited | 1-10 |
| Logical Consistency | Rigor of reasoning | 1-10 |
| Clarity | Expression clarity | 1-10 |

### Debate Flow

```
1. Opening Phase
   ├── Moderator announces topic
   ├── Introduces debaters
   └── Each side presents opening statement

2. Debate Phase (N rounds)
   ├── PRO speaks
   ├── CON speaks
   └── Moderator summarizes round

3. Closing Phase
   ├── PRO closing statement
   └── CON closing statement

4. Judgment Phase
   ├── Evaluate all arguments
   ├── Calculate average scores
   └── Generate analysis report
```

### Project Structure

```
debate-arena/
├── debate_arena/
│   ├── __init__.py
│   ├── core/
│   │   ├── debater.py      # Debater implementation
│   │   ├── moderator.py    # Moderator implementation
│   │   ├── judge.py        # Judge system
│   │   ├── arena.py        # Arena coordinator
│   │   └── history.py      # Debate history
│   └── personas/
│       ├── __init__.py
│       └── presets.py      # 7 preset personas
├── examples/
│   ├── climate_debate.py   # Climate debate example
│   └── verify_structure.py # Structure verification
└── tests/                  # 146 tests
```

### Development

```bash
# Run tests
pytest tests/ -v

# Run example
export ANTHROPIC_API_KEY="your_key"
python examples/climate_debate.py
```

### Test Coverage

- **146 tests** all passing
- Full type annotations with mypy validation
- Coverage of all core components

### License

MIT

---

<a name="中文"></a>
## 中文

### AI 驱动的多智能体辩论模拟框架

DebateArena 是一个复杂的框架，用于模拟 AI 智能体之间的结构化辩论。它通过多轮辩论深入探索复杂话题，支持不同观点的交锋，由主持人引导，智能评判系统进行评估。

### 功能特性

- **多立场辩论**：创建支持正方、反方或中立立场的 AI 辩手
- **结构化流程**：主持人引导的辩论流程，包含开篇、多轮辩论和结辩
- **智能评判**：基于论点质量、证据和逻辑的客观评估
- **人设系统**：可定制的辩手个性和论证风格
- **完整记录**：包含评分和分析的完整辩论历史

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Arena (竞技场)                          │
│  - 协调整个辩论流程                                          │
│  - 管理辩论状态                                              │
│  - 生成最终报告                                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌─────────────────────────────────┐      │
│  │  Moderator   │  │         Debaters (辩手)         │      │
│  │  (主持人)    │  │  ┌─────────┐ ┌─────────┐        │      │
│  │              │  │  │   PRO   │ │   CON   │        │      │
│  │ - 引导流程   │  │  │ (正方)  │ │ (反方)  │        │      │
│  │ - 控制轮次   │  │  └─────────┘ └─────────┘        │      │
│  │ - 总结阶段   │  │  - 生成论点                     │      │
│  └──────────────┘  │  - 反驳对手                     │      │
│                    │  - 结辩陈词                     │      │
│                    └─────────────────────────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Judge (评判系统)                        │   │
│  │  - 论点质量评估 (1-10分)                             │   │
│  │  - 逻辑一致性检查                                    │   │
│  │  - 证据充分性分析                                    │   │
│  │  - 最终结论生成                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 安装

```bash
pip install -e .
```

### 快速开始

```python
from debate_arena import Arena

# 创建竞技场并设置辩题
arena = Arena(
    topic="人工智能是否应该受到监管？",
    rounds=3,
    api_key="your-anthropic-api-key"
)

# 运行辩论
result = arena.run()

# 获取报告
print(result.report)

# 访问详细结果
print(f"胜者: {result.verdict.winner}")
print(f"总结: {result.verdict.summary}")
```

### 进阶使用

#### 自定义辩手人设

```python
from debate_arena import Debater, Stance, Arena
from debate_arena.core.debater import Persona

# 创建自定义人设
custom_persona = Persona(
    name="李博士",
    description="AI 伦理专家",
    background="清华大学计算机科学博士",
    argument_style="使用案例研究和框架分析"
)

# 使用自定义人设创建辩手
pro_debater = Debater(
    stance=Stance.PRO,
    persona=custom_persona,
    api_key="your_key"
)
```

#### 使用预设人设

```python
from debate_arena.personas import PERSONAS, get_persona

# 查看可用人设
print(PERSONAS.keys())
# dict_keys(['pro_default', 'con_default', 'neutral',
#            'economist_pro', 'economist_con',
#            'scientist_pro', 'scientist_con'])

# 获取特定人设
economist = get_persona("economist_pro")
```

### 评估维度

| 维度 | 描述 | 评分标准 |
|------|------|----------|
| 论点强度 | 核心观点的说服力 | 1-10分 |
| 证据质量 | 事实、数据的引用质量 | 1-10分 |
| 逻辑一致性 | 推理严密性 | 1-10分 |
| 表达清晰度 | 论述清晰程度 | 1-10分 |

### 辩论流程

```
1. 开场阶段
   ├── 主持人宣布辩题
   ├── 介绍辩手
   └── 各方阐述立论

2. 辩论阶段 (N 轮)
   ├── 正方发言
   ├── 反方发言
   └── 主持人总结本轮

3. 结辩阶段
   ├── 正方结辩
   └── 反方结辩

4. 评判阶段
   ├── 评估所有论点
   ├── 计算平均分
   └── 生成分析报告
```

### 项目结构

```
debate-arena/
├── debate_arena/
│   ├── __init__.py
│   ├── core/
│   │   ├── debater.py      # 辩手实现
│   │   ├── moderator.py    # 主持人实现
│   │   ├── judge.py        # 评判系统
│   │   ├── arena.py        # 竞技场协调
│   │   └── history.py      # 辩论历史
│   └── personas/
│       ├── __init__.py
│       └── presets.py      # 7个预设人设
├── examples/
│   ├── climate_debate.py   # 气候变化辩论示例
│   └── verify_structure.py # 结构验证脚本
└── tests/                  # 146 个测试
```

### 开发

```bash
# 运行测试
pytest tests/ -v

# 运行示例
export ANTHROPIC_API_KEY="your_key"
python examples/climate_debate.py
```

### 测试覆盖

- **146 个测试**全部通过
- 完整类型注解，通过 mypy 验证
- 覆盖所有核心组件

### 许可证

MIT
