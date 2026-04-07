from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


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
