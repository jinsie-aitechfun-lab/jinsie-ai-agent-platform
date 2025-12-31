# Architecture Overview（通义千问增强版）

本文件描述项目的整体架构，包括多模型路由、通义千问增强层、RAG 检索链路、多 Agent 执行流、FastAPI 服务层与阿里云部署架构。

## 1. System Architecture Diagram

```mermaid
flowchart TD
    User[用户请求] --> API[FastAPI 接口层]
    API --> Router[LLM Router<br/>选择模型引擎]
    Router --> Qwen[通义 Qwen API]
    Router --> DeepSeek[DeepSeek API]
    Router --> GPT[OpenAI / Azure]
    Router --> Doubao[字节豆包]

    API --> AgentLayer[多 Agent 层]
    AgentLayer --> Planner[Planner Agent<br/>任务拆解]
    Planner --> Worker[Worker Agents<br/>工具调用]

    Worker --> RAG[RAG 检索模块]
    RAG --> Embed[Embedding（Qwen-embedding）]
    RAG --> VectorDB[向量库 Milvus / OpenSearch]
    VectorDB --> Retriever[检索器 Retriever]

    Worker --> Tools[工具集（搜索 / 计算 / API）]

    Tools --> AgentLayer
    Retriever --> Worker
    Worker --> Synthesizer[结果融合 Synthesis]

    Synthesizer --> API
    API --> User
```

## 2. Component Breakdown

### 2.1 FastAPI 服务层  
统一 HTTP 入口、参数校验、Router/Agent/RAG 调用、SSE 流式输出。

### 2.2 多模型路由  
根据任务类型自动选择 Qwen / DeepSeek / GPT / Doubao。

## 3. RRAG Pipeline（通义增强）

Qwen-Embedding → Milvus/OpenSearch → Top-k 检索 → Agent 综合总结。

## 4. Agent Architecture  
Planner → Worker → ToolCall → RAG → Synthesizer。

## 5. SSE Streaming  
支持 token-level 流式输出，前端实时渲染。

## 6. Directory Structure  
（略，与你项目结构一致）

## 7. Deployment（阿里云）
Docker → ACR → ECS/Serverless → ALB → SLS。

## 8. 通义千问增强层总结
- Qwen API 主力  
- Qwen-Embedding  
- ToolCall-native  
- RAG 与 OpenSearch 兼容  
- SSE 兼容通义  
