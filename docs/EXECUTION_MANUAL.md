# AI桌面助手统一执行手册（审阅整合版）

> 版本：v2.0  
> 用途：作为 **唯一执行基线**，直接面向 AI 编程代理与人工开发协作。  
> 状态：已对原始模块手册进行交叉审阅、冲突消解和可执行化重写。  
> 适用范围：MVP → V3 扩展（含文档库管理、修改能力预留）。

---

## 0. 本次整合的强制结论

本手册覆盖并统一以下原始文档中的内容：项目骨架、UI 层、服务层、路由器、LLM 适配器、工具层、总览与 Codex 执行文件。

### 0.1 已修复的关键冲突

| 原冲突 | 统一结论 | 原因 |
|---|---|---|
| 前端存在 `Vue / React` 两套写法 | **统一为 React 18 + TypeScript + Tauri v2** | 避免 UI 技术栈分叉 |
| Tauri 存在 v1 与 v2 混用 | **统一为 Tauri v2** | 插件接口与构建方式必须一致 |
| 健康检查端点同时出现 `/health` 与 `/api/v1/health` | **统一公开端点为 `/api/v1/health`**，可选保留 `/health` 兼容别名 | 统一 API 命名空间 |
| 服务层既被定义为单体，又被定义为 `8001/8002/8003` 多服务 | **MVP 统一为单个 Python FastAPI 进程**，Router/LLM/Tools 作为进程内模块 | 更可执行、部署更简单、调试成本更低 |
| UI 一部分通过 Tauri Commands 直连业务，一部分通过 HTTP 调 Python | **统一为：业务请求走 HTTP/SSE；Tauri Commands 只做系统能力** | 降低前后端双实现与事件同步复杂度 |
| Router 规则引擎使用 `eval` | **禁止 `eval`，改为结构化规则 DSL 或 Python 规则函数** | 安全性、可测试性、可维护性更高 |
| LLM Provider 通过 `asyncio.run()` 检查可用性 | **禁止在库代码中嵌套 `asyncio.run()`**，统一使用异步 `health_check()` | 避免事件循环冲突 |
| Tools 模块仅只读，但未给“修改能力”扩展位 | **新增 `actions/` 变更执行层**，所有写操作统一进入该层并强制确认 | 保持工具层只读原则，同时支持扩展 |
| 接口字段命名不统一（`message/query`, `mode/decision`, `history/session_history` 等） | **统一共享契约字段**，以本手册为准 | 避免 AI 编程时跨模块字段漂移 |

### 0.2 最终执行原则

1. **逻辑模块可分，物理部署先不拆。**
2. **Pydantic 契约是唯一数据源，TypeScript 类型由其生成。**
3. **外部 API 与内部 DTO 一律使用 `snake_case`。**
4. **高风险动作（写入、覆盖、删除、外发、系统操作）必须走 `actions` 层并二次确认。**
5. **本地优先、在线补强、路由集中、可解释、可覆盖。**

---

## 1. 产品定义与边界

### 1.1 一句话定义
构建一个以 **本地 Qwen3-14B（经 Ollama）** 为默认引擎、以 **在线 LLM** 为高阶补强的桌面 AI 助手。

### 1.2 目标
- 统一文本处理、文档总结、轻代码辅助与桌面上下文接入。
- 降低用户在“本地工具 / 在线 AI / 文件上下文”之间切换的成本。
- 让系统既可快速交付 MVP，也可平滑扩展到文档库管理和受控修改能力。

### 1.3 明确不做
当前阶段不实现：
- 完整自主代理式系统控制
- 未确认的文件覆盖/删除
- 浏览器级复杂自动化
- 多模型编排平台
- 多用户/云账号系统
- 复杂权限中心

---

## 2. 统一技术栈

### 2.1 桌面端
- Tauri `v2.x`
- React `18.x`
- TypeScript `5.x`
- Vite `5.x`
- Zustand `4.x`
- TanStack Query `5.x`
- Tailwind CSS `3.x`

### 2.2 Python 后端
- Python `3.11`（最低 `3.10`）
- FastAPI `>=0.110`
- Uvicorn `>=0.27`
- Pydantic `>=2.6`
- pydantic-settings `>=2.2`
- httpx `>=0.27`
- structlog `>=24.1`
- PyYAML `>=6.0`
- aiosqlite `>=0.20`
- Pillow `>=10.2`
- pyperclip `>=1.8.2`
- chardet `>=5.2`
- mss `>=9.0`

### 2.3 测试与工程工具
- pytest `>=8.0`
- pytest-asyncio `>=0.23`
- respx `>=0.21`
- ruff `>=0.4`
- mypy `>=1.9`
- pre-commit `>=3.7`

### 2.4 统一依赖约束

#### Python `pyproject.toml`
```toml
[project]
name = "ai-desktop-assistant-backend"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
  "fastapi>=0.110.0",
  "uvicorn[standard]>=0.27.0",
  "pydantic>=2.6.0",
  "pydantic-settings>=2.2.0",
  "httpx>=0.27.0",
  "structlog>=24.1.0",
  "pyyaml>=6.0.1",
  "aiosqlite>=0.20.0",
  "pyperclip>=1.8.2",
  "Pillow>=10.2.0",
  "chardet>=5.2.0",
  "mss>=9.0.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0.0",
  "pytest-asyncio>=0.23.0",
  "respx>=0.21.0",
  "ruff>=0.4.0",
  "mypy>=1.9.0",
  "pre-commit>=3.7.0"
]
```

#### 前端 `package.json`
```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.0.0",
    "clsx": "^2.1.0",
    "date-fns": "^3.0.0",
    "lucide-react": "^0.400.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  }
}
```

---

## 3. 统一仓库结构（最终版）

> 说明：保留原“模块边界”思想，但将 **运行时** 统一到一个 Python 服务中；这样既保留可并行开发性，也真正可执行。

```text
project-root/
├── apps/
│   └── desktop/
│       ├── src/
│       │   ├── components/
│       │   ├── hooks/
│       │   ├── services/
│       │   ├── stores/
│       │   ├── types/
│       │   ├── utils/
│       │   ├── App.tsx
│       │   └── main.tsx
│       ├── src-tauri/
│       │   ├── src/
│       │   │   ├── commands/
│       │   │   │   ├── dialog.rs
│       │   │   │   ├── shortcut.rs
│       │   │   │   ├── tray.rs
│       │   │   │   └── window.rs
│       │   │   ├── services/
│       │   │   │   └── shell.rs
│       │   │   └── main.rs
│       │   ├── Cargo.toml
│       │   └── tauri.conf.json
│       └── package.json
│
├── services/
│   └── backend/
│       ├── app/
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── health.py
│       │   │       ├── chat.py
│       │   │       ├── tools.py
│       │   │       ├── models.py
│       │   │       ├── config.py
│       │   │       ├── sessions.py
│       │   │       ├── library.py
│       │   │       └── actions.py
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   ├── logging.py
│       │   │   ├── errors.py
│       │   │   ├── responses.py
│       │   │   └── security.py
│       │   ├── modules/
│       │   │   ├── router/
│       │   │   ├── llm/
│       │   │   │   ├── base.py
│       │   │   │   ├── local_ollama.py
│       │   │   │   ├── remote_openai.py
│       │   │   │   └── factory.py
│       │   │   ├── tools/
│       │   │   │   ├── clipboard.py
│       │   │   │   ├── files.py
│       │   │   │   └── screenshot.py
│       │   │   ├── session/
│       │   │   ├── library/
│       │   │   └── actions/
│       │   ├── storage/
│       │   │   ├── sqlite.py
│       │   │   └── migrations/
│       │   ├── contracts/
│       │   │   ├── enums.py
│       │   │   ├── common.py
│       │   │   ├── chat.py
│       │   │   ├── routing.py
│       │   │   ├── tools.py
│       │   │   ├── library.py
│       │   │   └── actions.py
│       │   └── main.py
│       ├── tests/
│       │   ├── unit/
│       │   ├── integration/
│       │   └── e2e/
│       ├── pyproject.toml
│       ├── .env.example
│       └── config.yaml
│
├── shared/
│   ├── openapi/
│   └── prompts/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_CONTRACT.md
│   └── EXECUTION_MANUAL.md
│
├── scripts/
│   ├── dev_backend.sh
│   ├── dev_desktop.sh
│   ├── export_openapi.py
│   └── generate_ts_types.sh
│
└── README.md
```

---

## 4. 运行架构（最终版）

### 4.1 物理部署
- **桌面端**：Tauri v2 应用
- **后端**：单个 FastAPI 进程，监听 `127.0.0.1:8000`
- **本地模型服务**：Ollama，默认 `http://127.0.0.1:11434`
- **在线模型服务**：OpenAI 兼容 API（可替换）

### 4.2 逻辑模块边界
- `router/`：只做分类、路由、上下文编排
- `llm/`：只做模型调用抽象与 Provider 适配
- `tools/`：只做只读桌面输入
- `session/`：会话与消息持久化
- `library/`：文档库导入、索引、检索
- `actions/`：写入/修改/删除/外发等变更操作

### 4.3 通信原则
- React → Python：**HTTP + SSE**
- React → Rust(Tauri)：**仅系统能力命令**
- Python 内部模块：**直接 import 调用，不走 HTTP**

### 4.4 为什么不采用 `8001/8002/8003` 多服务
对于桌面本地产品，拆成 Router/LLM/Tools 独立 HTTP 服务会显著增加：
- 启动顺序复杂度
- 端口占用与冲突
- 日志与故障定位成本
- AI 编程代理跨模块修改难度

因此：
- **MVP / V1 / V2 一律单进程**
- 若未来需要拆分，只在模块边界稳定后再做

---

## 5. 统一命名规范

### 5.1 DTO 命名
- 所有 HTTP JSON 字段：`snake_case`
- Python 内部字段：`snake_case`
- TypeScript API DTO：**保持 snake_case，不自行 camelCase**
- React 组件 props / 本地变量：可用 `camelCase`

### 5.2 核心名词统一

| 概念 | 统一名称 | 说明 |
|---|---|---|
| 用户输入文本 | `query` | 不再使用 `message` 作为请求根字段 |
| 聊天历史 | `history` | 不再混用 `session_history` |
| 用户模式偏好 | `requested_mode` | 取值 `auto/local/remote/hybrid` |
| 路由结果 | `route_result` | 包含模式、理由、置信度 |
| 上下文数组 | `context_items` | 统一上下文输入容器 |
| 实际执行模式 | `execution_mode` | 取值 `local/remote/hybrid` |
| 工具计划 | `planned_tools` | Router 输出工具需求 |
| 确认需求 | `requires_confirmation` | 风险动作或外发时为 true |

### 5.3 ID 与时间
- 所有主键 ID 使用 `uuid4().hex`
- 时间字段统一为 UTC ISO8601 字符串
- 数据库存储统一使用 UTC

---

## 6. 共享契约（唯一真实来源）

> 规则：**后端 `app/contracts/*.py` 是唯一真实来源**。  
> 前端类型不得手写复制，应从 OpenAPI / JSON Schema 自动生成。

### 6.1 枚举定义

```python
from enum import Enum

class RequestedMode(str, Enum):
    AUTO = "auto"
    LOCAL = "local"
    REMOTE = "remote"
    HYBRID = "hybrid"

class ExecutionMode(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"
    HYBRID = "hybrid"

class ContextSource(str, Enum):
    USER_INPUT = "user_input"
    CLIPBOARD = "clipboard"
    FILE = "file"
    SCREENSHOT = "screenshot"
    DOCUMENT = "document"
    LIBRARY = "library"
    SYSTEM = "system"

class TaskType(str, Enum):
    TEXT_REWRITE = "text_rewrite"
    TEXT_SUMMARY = "text_summary"
    TEXT_GENERATION = "text_generation"
    QNA_GENERAL = "qna_general"
    QNA_FACTUAL = "qna_factual"
    CODE_EXPLAIN = "code_explain"
    CODE_GENERATE = "code_generate"
    CODE_REVIEW = "code_review"
    CODE_DEBUG = "code_debug"
    SEARCH_REQUIRED = "search_required"
    REASONING_SIMPLE = "reasoning_simple"
    REASONING_COMPLEX = "reasoning_complex"
    PLANNING = "planning"
    MULTI_DOC = "multi_doc"
    TRANSLATION = "translation"
    CHAT = "chat"
    DOC_LIBRARY_QUERY = "doc_library_query"
    FILE_MODIFICATION = "file_modification"

class PrivacyLevel(str, Enum):
    PUBLIC = "public"
    NORMAL = "normal"
    SENSITIVE = "sensitive"
    PRIVATE = "private"

class ToolName(str, Enum):
    CLIPBOARD = "clipboard"
    FILE_READ = "file_read"
    SCREENSHOT = "screenshot"
    DOCUMENT_IMPORT = "document_import"

class ActionRiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    HIGH = "high"
    CRITICAL = "critical"
```

### 6.2 通用模型

```python
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

class ContextItem(BaseModel):
    id: str
    source: ContextSource
    name: Optional[str] = None
    mime_type: Optional[str] = None
    text_content: Optional[str] = None
    file_path: Optional[str] = None
    binary_ref: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class ChatMessage(BaseModel):
    id: str
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

class GenerationOptions(BaseModel):
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float | None = None
    stream: bool = False

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
```

### 6.3 聊天请求与响应

```python
class ChatRequest(BaseModel):
    session_id: str | None = None
    query: str
    requested_mode: RequestedMode = RequestedMode.AUTO
    context_items: list[ContextItem] = Field(default_factory=list)
    history: list[ChatMessage] = Field(default_factory=list)
    options: GenerationOptions = Field(default_factory=GenerationOptions)

class RouteResult(BaseModel):
    execution_mode: ExecutionMode
    reason_code: str
    reason_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    task_type: TaskType
    privacy_level: PrivacyLevel
    planned_tools: list[ToolName] = Field(default_factory=list)
    requires_confirmation: bool = False
    confirmation_message: str | None = None
    selected_provider: str
    selected_model: str
    context_summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    reply: ChatMessage
    route_result: RouteResult
    usage: TokenUsage | None = None
```

### 6.4 健康检查与模型状态

```python
class ProviderHealth(BaseModel):
    provider: str
    available: bool
    status: str  # "healthy" | "degraded" | "unavailable"
    latency_ms: float | None = None
    message: str | None = None

class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unavailable"
    version: str
    timestamp: datetime
    services: dict[str, ProviderHealth]
```

### 6.5 错误契约

```python
class ErrorDetail(BaseModel):
    code: str
    message: str
    suggestion: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)

class ApiResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: ErrorDetail | None = None
    request_id: str
    timestamp: datetime
```

---

## 7. 后端 API 合同（最终版）

### 7.1 公开端点

| 方法 | 路径 | 说明 | 阶段 |
|---|---|---|---|
| GET | `/api/v1/health` | 服务健康检查 | P0 |
| POST | `/api/v1/chat` | 非流式对话 | P0 |
| POST | `/api/v1/chat/stream` | SSE 流式对话 | P0 |
| GET | `/api/v1/tools/clipboard` | 读取剪贴板 | P0 |
| POST | `/api/v1/tools/files/read` | 读取文件 | P0 |
| POST | `/api/v1/tools/screenshot` | 获取截图 | V2 |
| GET | `/api/v1/models` | 获取模型列表 | P1 |
| GET | `/api/v1/models/local/status` | 本地模型状态 | P1 |
| GET | `/api/v1/config` | 读取配置 | P1 |
| PUT | `/api/v1/config` | 更新配置 | P1 |
| GET | `/api/v1/sessions/{session_id}` | 获取会话详情 | V2 |
| DELETE | `/api/v1/sessions/{session_id}` | 删除会话 | V2 |
| POST | `/api/v1/library/documents/import` | 导入文档到文档库 | V3 |
| GET | `/api/v1/library/documents` | 文档库列表 | V3 |
| POST | `/api/v1/library/query` | 文档库检索 | V3 |
| POST | `/api/v1/actions/plan` | 生成修改计划 | V3 |
| POST | `/api/v1/actions/apply` | 确认执行修改 | V3 |

### 7.2 健康检查示例

```http
GET /api/v1/health
```

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "0.1.0",
    "timestamp": "2026-04-07T05:00:00Z",
    "services": {
      "backend": {
        "provider": "backend",
        "available": true,
        "status": "healthy"
      },
      "local_llm": {
        "provider": "ollama",
        "available": true,
        "status": "healthy",
        "latency_ms": 12.4
      },
      "remote_llm": {
        "provider": "openai",
        "available": true,
        "status": "healthy",
        "latency_ms": 320.8
      }
    }
  },
  "request_id": "e8b0...",
  "timestamp": "2026-04-07T05:00:00Z"
}
```

### 7.3 聊天示例

```json
{
  "session_id": null,
  "query": "帮我总结这份会议纪要",
  "requested_mode": "auto",
  "context_items": [
    {
      "id": "ctx_1",
      "source": "file",
      "name": "meeting.md",
      "file_path": "/Users/me/Desktop/meeting.md",
      "text_content": "会议全文..."
    }
  ],
  "history": [],
  "options": {
    "temperature": 0.3,
    "max_tokens": 1200,
    "stream": false
  }
}
```

### 7.4 SSE 事件规范

`POST /api/v1/chat/stream` 返回 `text/event-stream`

事件类型：
- `routing`
- `chunk`
- `done`
- `error`

示例：
```text
event: routing
data: {"execution_mode":"local","reason_text":"文本总结且上下文较短"}

event: chunk
data: {"content":"这份会议纪要主要包含三部分..."}

event: done
data: {"message_id":"msg_xxx","session_id":"sess_xxx","usage":{"total_tokens":542}}
```

---

## 8. Router 设计（最终版）

### 8.1 Router 是唯一决策层
禁止在以下位置硬编码路由：
- React 组件
- Tauri Rust 命令
- LLM Provider
- Tools 模块
- API Router 函数

### 8.2 Router 输入与输出
- 输入：`ChatRequest` + 工具检测结果 + 配置
- 输出：`RouteResult` + `formatted_messages`

### 8.3 分类步骤
1. 提取任务类型 `task_type`
2. 判断隐私级别 `privacy_level`
3. 估算上下文规模 `estimated_tokens`
4. 判断是否需要工具 `planned_tools`
5. 判断是否需要确认 `requires_confirmation`
6. 产出最终 `execution_mode`

### 8.4 路由优先级
按优先级从高到低执行：

1. **用户强制模式**
2. **高风险动作强制确认**
3. **隐私优先本地**
4. **联网/最新信息强制远程**
5. **超长上下文倾向混合**
6. **复杂推理/重代码倾向远程**
7. **默认本地**

### 8.5 禁止 `eval`，改用结构化规则 DSL

```python
from pydantic import BaseModel
from typing import Literal

class RuleCondition(BaseModel):
    field: str
    op: Literal["eq", "neq", "in", "not_in", "gt", "gte", "lt", "lte", "contains"]
    value: object

class RuleDefinition(BaseModel):
    id: str
    priority: int
    decision: ExecutionMode
    reason_code: str
    reason_text: str
    all: list[RuleCondition] = []
    any: list[RuleCondition] = []
    confidence: float
```

### 8.6 推荐基础规则
- `privacy_local`: `privacy_level in [sensitive, private] -> local`
- `search_remote`: `task_type == search_required -> remote`
- `long_context_hybrid`: `estimated_tokens > 6000 -> hybrid`
- `simple_rewrite_local`: `task_type == text_rewrite -> local`
- `complex_code_remote`: `task_type in [code_debug, code_review] and estimated_tokens > 4000 -> remote`

### 8.7 混合模式规范
混合模式必须显式分两步：
1. 本地先压缩上下文
2. 在线执行高阶任务

禁止：
- 将所有原始文件全文无筛选发送到远程
- 在混合模式下省略本地摘要步骤

---

## 9. LLM 适配层（最终版）

### 9.1 抽象接口

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class BaseLLMProvider(ABC):
    provider_name: str

    @abstractmethod
    async def complete(self, messages: list[ChatMessage], options: GenerationOptions) -> tuple[str, TokenUsage | None]:
        ...

    @abstractmethod
    async def stream_complete(self, messages: list[ChatMessage], options: GenerationOptions) -> AsyncIterator[str]:
        ...

    @abstractmethod
    async def list_models(self) -> list[dict]:
        ...

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        ...
```

### 9.2 关键约束
- 不允许在 Provider 内部调用 `asyncio.run()`
- 不允许将健康检查设计成同步属性 `is_available`
- 不允许让 Provider 直接读取 UI 状态或 Router 决策
- 不允许把错误吞掉后返回空字符串

### 9.3 默认 Provider
- 本地：`ollama`
- 在线：`openai_compatible`

### 9.4 默认模型
- 本地默认：`qwen3:14b`
- 远程默认：由 `REMOTE_LLM_MODEL` 配置指定

### 9.5 Provider 工厂

```python
class ProviderFactory:
    @staticmethod
    def create_local(provider_name: str, config: dict) -> BaseLLMProvider:
        ...

    @staticmethod
    def create_remote(provider_name: str, config: dict) -> BaseLLMProvider:
        ...
```

### 9.6 错误映射
统一错误码：
- `PROVIDER_UNAVAILABLE`
- `MODEL_NOT_FOUND`
- `AUTHENTICATION_FAILED`
- `RATE_LIMIT_EXCEEDED`
- `REQUEST_TIMEOUT`
- `CONTEXT_LENGTH_EXCEEDED`
- `CONTENT_FILTERED`

---

## 10. Tool Layer（只读输入层）

### 10.1 当前职责
- 读取剪贴板
- 读取文件
- 获取截图

### 10.2 明确非职责
- 不负责文件写入
- 不负责文件覆盖
- 不负责删除
- 不负责外发
- 不负责持久化历史

### 10.3 文件读取规则
- 必须校验路径是否位于允许范围内
- 默认单文件最大读取：`1MB`
- 超大文件必须截断并标记 `truncated=true`
- 对二进制与不支持格式返回结构化错误，不静默失败

### 10.4 统一文件结果

```python
class FileReadResult(BaseModel):
    path: str
    success: bool
    content: str | None = None
    mime_type: str | None = None
    encoding: str | None = None
    truncated: bool = False
    actual_size: int = 0
    error: str | None = None
```

### 10.5 截图
- MVP 不强制实现
- V2 通过 `mss` 提供全屏/区域截图
- 失败时必须返回 `SCREENSHOT_CAPTURE_FAILED`

---

## 11. Session 与存储设计

### 11.1 统一存储方案
- 默认使用 SQLite
- 通过 `aiosqlite` 异步访问
- 文件数据库路径：`data/app.db`

### 11.2 最小表结构
- `sessions`
- `messages`
- `documents`
- `document_chunks`（V3）
- `action_logs`（V3）

### 11.3 MVP 最低要求
- 新建会话
- 保存用户消息与助手回复
- 读取会话历史

### 11.4 存储接口

```python
class SessionStore(Protocol):
    async def create_session(self) -> str: ...
    async def append_message(self, session_id: str, message: ChatMessage) -> None: ...
    async def list_messages(self, session_id: str) -> list[ChatMessage]: ...
```

---

## 12. 文档库管理扩展（V3 预留，但本手册已定义）

> 这是本次整合新增的正式扩展位，用于满足“新增文档库管理”的要求。

### 12.1 模块定位
`modules/library/` 负责：
- 文档导入
- 文本提取
- 元数据存储
- 关键字/全文检索
- 为 Router 提供 `library` 类型上下文

### 12.2 第一阶段支持格式
- `.txt`
- `.md`
- `.json`
- `.csv`
- 代码文本类文件

### 12.3 第二阶段可扩展格式
- `.pdf`
- `.docx`
- 图片 OCR 文本（单独解析器）
- 目录批量导入

### 12.4 文档库核心模型

```python
class DocumentRecord(BaseModel):
    id: str
    title: str
    file_path: str
    mime_type: str
    size_bytes: int
    imported_at: datetime
    hash_sha256: str
    tags: list[str] = []
    metadata: dict[str, Any] = {}

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    token_estimate: int
```

### 12.5 文档库 API
- `POST /api/v1/library/documents/import`
- `GET /api/v1/library/documents`
- `GET /api/v1/library/documents/{document_id}`
- `POST /api/v1/library/query`
- `DELETE /api/v1/library/documents/{document_id}`（需要确认）

### 12.6 与 Router 的集成
当用户请求：
- “在我的文档库里查……”
- “基于已导入文档总结……”
- “把这篇文章存入文档库……”

Router 应识别 `task_type = doc_library_query` 或触发 `document_import` 工具计划。

---

## 13. 修改能力扩展（V3 正式设计）

> 原始文档中工具层坚持只读，这是正确的；但为满足“修改功能”扩展，本手册新增 `actions/` 层，而不是污染 `tools/`。

### 13.1 `actions/` 模块职责
处理所有 **状态改变型动作**：
- 文件写入
- 文件覆盖
- 文件删除
- 批量重命名
- 将内容外发到远程服务
- 打开目录 / 打开文件（可视为低风险系统动作）

### 13.2 两阶段执行模型
1. **Plan 阶段**：生成修改计划、差异预览、风险评估
2. **Apply 阶段**：用户确认后执行

### 13.3 核心模型

```python
class FileMutation(BaseModel):
    path: str
    operation: str  # "create" | "replace" | "append" | "delete" | "rename"
    new_content: str | None = None
    diff_preview: str | None = None

class ActionPlan(BaseModel):
    id: str
    risk_level: ActionRiskLevel
    summary: str
    mutations: list[FileMutation] = []
    requires_confirmation: bool = True
    expires_at: datetime

class ActionApplyRequest(BaseModel):
    action_plan_id: str
    confirmed: bool
    confirmation_text: str | None = None
```

### 13.4 强制安全规则
- `actions/apply` 没有 `confirmed=true` 不得执行
- 删除、覆盖、外发默认 `risk_level >= high`
- 所有执行结果写入 `action_logs`
- 不允许模型直接写文件，必须先产出 `ActionPlan`

### 13.5 与 UI 的关系
UI 需支持：
- 展示 diff
- 展示风险等级
- 明确的确认按钮
- 撤销入口（如可行）

---

## 14. 配置系统（最终版）

### 14.1 配置优先级
1. 环境变量
2. `.env`
3. `config.yaml`
4. 代码默认值

### 14.2 推荐配置字段

```yaml
server:
  host: "127.0.0.1"
  port: 8000

ui:
  desktop_dev_url: "http://localhost:1420"

routing:
  default_mode: "auto"
  force_local_on_sensitive: true
  enable_hybrid: true
  long_context_threshold: 6000

local_llm:
  provider: "ollama"
  base_url: "http://127.0.0.1:11434"
  model: "qwen3:14b"
  timeout_seconds: 60

remote_llm:
  provider: "openai_compatible"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  timeout_seconds: 120

storage:
  sqlite_path: "data/app.db"
  files_root: "data/files"

security:
  allow_write_actions: false
  require_confirmation_for_external_send: true
  allowed_read_roots: []
```

### 14.3 核心环境变量
```bash
API_HOST=127.0.0.1
API_PORT=8000
LOCAL_LLM_PROVIDER=ollama
LOCAL_LLM_BASE_URL=http://127.0.0.1:11434
LOCAL_LLM_MODEL=qwen3:14b
REMOTE_LLM_PROVIDER=openai_compatible
REMOTE_LLM_BASE_URL=https://api.openai.com/v1
REMOTE_LLM_API_KEY=...
REMOTE_LLM_MODEL=gpt-4o-mini
SQLITE_PATH=data/app.db
ALLOW_WRITE_ACTIONS=false
```

---

## 15. 前端边界（最终版）

### 15.1 React 负责
- 消息流
- 输入框
- 上下文预览
- 模式切换
- 调用 Python API
- 展示路由结果与错误

### 15.2 Rust / Tauri 只负责
- 全局快捷键
- 窗口显隐
- 系统托盘
- 原生文件选择对话框
- 打开目录/文件的系统调用
- 可选的权限/平台桥接

### 15.3 禁止
- 在 Rust 里重复实现 Router
- 在 React 里直接拼接模型 Prompt
- 在 React 里硬编码“最新信息一定走远程”的规则

---

## 16. 统一数据流

### 16.1 本地任务
1. UI 发送 `ChatRequest`
2. API 收到请求
3. Router 产出 `RouteResult(local)`
4. Tools 补上下文（如需要）
5. Local Provider 生成回复
6. SessionStore 记录消息
7. UI 渲染结果

### 16.2 在线任务
1. UI 发送 `ChatRequest`
2. Router 产出 `RouteResult(remote)`
3. 若有本地上下文，则先归一化
4. Remote Provider 调用
5. SessionStore 落库
6. UI 渲染结果

### 16.3 混合任务
1. Router 判定 `hybrid`
2. 本地压缩器产出 `context_summary`
3. 远程模型只接收摘要 + 目标 + 约束
4. 返回结果并落库
5. UI 展示“混合执行”标识

### 16.4 文档库任务（V3）
1. 用户导入文档或检索文档库
2. Library 模块返回相关文档片段
3. Router 将其注入 `context_items`
4. 本地或远程按路由执行

### 16.5 修改任务（V3）
1. Router 识别为高风险动作
2. 先生成 `ActionPlan`
3. UI 展示 diff 和风险
4. 用户确认后 API 调 `actions/apply`
5. 记录日志与结果

---

## 17. 开发阶段（统一版）

### Phase 0：骨架与通信
交付：
- Tauri v2 + React 初始化
- FastAPI 初始化
- `/api/v1/health`
- HTTP/SSE 通信验证
- 配置与日志系统

完成标准：
- 桌面端可请求后端并得到 mock 响应

### Phase 1：本地 MVP
交付：
- Ollama 接入
- 会话界面
- 剪贴板读取
- 文件读取
- 路由结果展示
- 会话落库

完成标准：
- 用户可完成一轮真实本地问答

### Phase 2：在线升级
交付：
- 远程 Provider 接入
- 一键转在线
- 自动附带本地摘要
- 本地/在线状态清晰展示

完成标准：
- 用户可将当前任务无缝升级到在线继续处理

### Phase 3：规则式路由
交付：
- TaskType 分类
- 结构化规则 DSL
- 本地/远程/混合判定
- 用户模式覆盖

完成标准：
- 路由结果可解释、可测试、可覆盖

### Phase 4：桌面上下文增强
交付：
- 截图输入
- 历史会话查看
- 本地目录读取（只读）
- 文档库导入能力基础版

完成标准：
- 上下文能力覆盖剪贴板 / 文件 / 截图 / 文档库

### Phase 5：文档库与修改能力
交付：
- 文档库检索
- 文档元数据管理
- `actions/plan` + `actions/apply`
- diff 预览与确认流

完成标准：
- 系统可安全地支持“导入资料并基于资料工作”，以及“先计划后确认的文件修改”

---

## 18. 测试与验收

### 18.1 最低测试清单
- Router 单元测试：`>= 15` 场景
- LLM Provider mock 测试：本地/远程
- Tools 单元测试：剪贴板、文件、截图
- API 集成测试：health/chat/chat_stream
- UI 组件测试：输入区、消息流、状态标识
- E2E 手动验收：本地问答、一键转在线、上下文插入

### 18.2 必测失败路径
- 本地模型不可用
- 远程模型认证失败
- 文件不存在
- 文件过大
- 截图失败
- 路由失败
- 修改动作未确认

### 18.3 工程验收标准
- 代码结构与本手册一致
- DTO 与 OpenAPI 一致
- 关键逻辑有类型标注
- 不存在静默失败
- 日志可追踪关键路径
- 文档随阶段同步更新

### 18.4 性能验收
- 后端启动 < `5s`
- 非 LLM API 响应 P99 < `500ms`
- UI 不阻塞主线程
- SSE 首 chunk 可见

---

## 19. AI 编程执行规则

1. **先保证本阶段闭环，再做扩展。**
2. **任何新增字段必须先写入 `contracts/`。**
3. **前端类型不得手写漂移，必须由后端契约生成。**
4. **不允许为了“先跑通”而在 UI/LLM/Tools 中复制路由逻辑。**
5. **不允许用 `try/except: pass` 隐藏错误。**
6. **不允许直接执行文件修改；必须走 `actions` 计划—确认—执行链。**
7. **不允许在 Provider 内部用 `asyncio.run()`。**
8. **不允许使用 `eval` 解释路由规则。**
9. **每阶段完成后必须更新 `README.md`、`docs/ARCHITECTURE.md`、`docs/API_CONTRACT.md`。**
10. **始终保持项目处于可运行或可恢复状态。**

---

## 20. Done Definition

某阶段只有在以下条件全部满足时才算完成：
- 功能已实现
- 主流程可运行
- 错误流程可感知
- 契约已同步
- 基础测试已通过
- 文档已更新
- 与本手册无冲突

---

## 21. 首轮推荐执行顺序（给 AI Agent）

1. 初始化 `apps/desktop` 与 `services/backend`
2. 建立 `/api/v1/health`
3. 建立统一 `contracts/`
4. 实现会话与消息 DTO
5. 接入本地 Ollama Provider
6. 打通 `/api/v1/chat`
7. 实现剪贴板与文件读取
8. 展示 `route_result`
9. 接入远程 Provider
10. 实现混合模式
11. 增加截图
12. 增加文档库
13. 增加 `actions` 变更能力

---

## 22. 迁移说明（从原始模块手册到本手册）

| 原模块写法 | 本手册替代方案 |
|---|---|
| `services/api`, `services/router`, `services/tools` 各自独立运行 | 统一为 `services/backend/app/modules/*` 进程内模块 |
| `module_service.md` 中多端口依赖 | 改为单后端 + 外部模型服务 |
| `module_router.md` 中 `eval` 规则 | 改为结构化规则 DSL |
| `module_ui.md` 中业务 Tauri Commands | 改为业务走 HTTP/SSE，仅系统能力保留 Tauri Commands |
| `module_skeleton.md` 中 Vue/Tauri v1 | 统一为 React/Tauri v2 |
| 仅只读工具层 | 增加 `library/` 与 `actions/` 作为正式扩展位 |

---

## 23. 最终原则

这个项目最终必须满足五点：
- **本地优先**
- **在线补强**
- **路由集中**
- **行为可控**
- **持续可迭代**

如果某实现与这五点冲突，以这五点为最高优先级。
