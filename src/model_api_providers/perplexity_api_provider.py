from langchain_core.language_models.chat_models import BaseChatModel
from langchain_perplexity import ChatPerplexity

from model_api_providers.model_api_provider import ModelApiProvider

PERPLEXITY_MODELS = [
    "sonar",
    "sonar-pro",
    "sonar-deep-research",
    "sonar-reasoning",
    "sonar-reasoning-pro"
]

class PerplexityApiProvider(ModelApiProvider):
    def __init__(self) -> None:
        super().__init__(name="Perplexity AI", api_key_name="PPLX_API_KEY")
    
    def get_model_names(self) -> list[str]:
        return list(PERPLEXITY_MODELS)
    
    def get_chat_model(self, model_name: str) -> BaseChatModel:
        return ChatPerplexity(model=model_name)