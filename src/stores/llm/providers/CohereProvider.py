from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums, DocumentTypeEnums
import cohere  # pyright: ignore[reportMissingImports]
import logging


class CohereProvider(LLMInterface):

    def __init__(self,api_key : str ,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_token: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_token = default_generation_max_output_token
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.clinet = cohere.ClientV2(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)

    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
    
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        if not isinstance(text, str):
            text = str(text)
        return text[: self.default_input_max_characters].strip()
    
    def generate_text(self, prompt: str,chat_history: list= [] , max_output_tokens: int = None, temperature: float = None):
        if not self.client:
            self.logger.error("Cohere was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for Cohere was not set")
            return None 
        
        if chat_history is None:
            chat_history = []
        
        response = self.client.chat(
                        model=self.generation_model_id,
                        messages=self.process_text(prompt),
                        temperature=temperature,
                        max_tokens=max_output_tokens)
        
        if not response or not response.message.content:
            self.logger.error("Error while generating text with Cohere")
            return None

        return response.message.content[0].text
    
    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("OpenAI was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for Cohere was not set")
            return None 
        
        input_type = CohereEnums.DOCUMENT
        if document_type == DocumentTypeEnums.QUERY:
            input_type = CohereEnums.QUERY

        response = self.clinet.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types=["float"],
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with Cohere")
            return None
        
        return response.embeddings.float[0]
        
    def construct_prompt(self, prompt: str, role: str):
        return  {
            "role" : role,
            "content" : self.process_text(prompt)
        }
    
    




