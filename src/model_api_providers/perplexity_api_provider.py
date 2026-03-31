import json
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_perplexity import ChatPerplexity

from model_api_providers.model_api_provider import ModelApiProvider


class PerplexityApiProvider(ModelApiProvider):
    def __init__(self) -> None:
        super().__init__(name="Perplexity AI", api_key_name="PPLX_API_KEY")
    
    def get_model_names(self) -> list[str]:
        json_path = Path(__file__).parent.parent.parent / "data" / "global" / "perplexity_models.json"
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def get_chat_model(self, model_name: str) -> BaseChatModel:
        return ChatPerplexity(model_name=model_name)