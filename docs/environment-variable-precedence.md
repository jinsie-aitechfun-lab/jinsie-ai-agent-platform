# 环境变量优先级说明：direnv 与 python-dotenv（公开工程版｜中文版）

> 本文用于**公开工程文档**，说明在工程中为何应使用  
> `python-dotenv(load_dotenv, override=False)`，以及它如何与 `direnv` 等
> Shell 层工具安全协作。  
>  
> 本文不涉及学习过程，仅描述**工程结论与规范**。

---

## 一、核心原则（结论先行）

> **运行环境提供的环境变量永远具有最高优先级。**  
> `python-dotenv` 的设计目标是“兜底补齐”，而不是“覆盖或接管”。

换句话说：

- 环境变量的**权威来源**来自：  
  Shell / direnv / Docker / CI
- `python-dotenv` 只在**变量缺失时**才介入

---

## 二、工作机制说明

### 1️⃣ Shell 层注入（direnv）

使用 `direnv` 时，环境变量在 **Python 启动之前** 就已经被注入：

- Shell 进入项目目录
- `direnv` 自动执行 `.envrc`
- `.envrc` 中的变量被 `export`
- Python 启动时**直接继承**这些环境变量

因此，在 Python 进程中：

```python
import os
os.environ["OPENAI_API_KEY"]  # 已经存在
```

此时，这些变量已经是 Python 进程的“初始环境”。

---

### 2️⃣ Python 层兜底（python-dotenv）

当在代码中调用：

```python
load_dotenv(override=False)
```

`python-dotenv` 的行为是：

- 解析 `.env` 文件
- 对每一个变量：
  - **仅当该变量在 `os.environ` 中不存在时才写入**

也就是说：

- 已由 direnv / CI / Docker 提供的变量 → **保持不变**
- `.env` 中的变量 → **仅作为补充**

---

## 三、为什么必须使用 `override=False`

使用 `override=False` 可以确保：

- 环境变量来源层级清晰
- 本地 `.env` 不会意外覆盖 CI / 生产环境配置
- 不破坏 Docker / 云环境注入的变量
- 本地开发行为与生产环境保持一致

相反，`override=True` 会无条件覆盖已有变量，  
**在工程实践中不推荐使用**。

---

## 四、推荐的工程用法（标准模式）

```python
from dotenv import load_dotenv

# 仅在环境变量缺失时，从 .env 兜底加载
load_dotenv(override=False)
```

该模式具备以下优点：

- 环境决定“真实配置来源”
- 代码不绑定任何具体工具
- 本地 / CI / Docker 行为一致、可预期

---

## 五、总结

- `direnv`（或 Docker / CI）负责**定义运行环境**
- `python-dotenv` 负责**补齐缺失配置**
- 二者职责清晰、互不冲突

> **这是一种成熟工程中常见且稳定的环境变量管理方式。**
