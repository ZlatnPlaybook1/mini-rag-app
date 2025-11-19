from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    CHOHERE = "CHOHERE"

class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CohereEnums(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnums(Enum):
    DOCUMENT = "document" 
    QUERY = "query"