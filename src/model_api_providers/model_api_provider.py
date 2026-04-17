from abc import ABC, abstractmethod

from langchain_core.language_models.chat_models import BaseChatModel

from utils.env_manager import add_env_variable, get_env_variable


class ModelApiProvider(ABC):
    
    name: str
    api_key_name: str

    def __init__(self, name: str, api_key_name: str) -> None:
        self.name = name
        self.api_key_name = api_key_name
    
    def is_setup(self) -> bool:
        return get_env_variable(self.api_key_name) is not None
    
    def set_api_key(self, api_key: str) -> None:
        add_env_variable(self.api_key_name, api_key)
    
    @abstractmethod
    def get_model_names(self) -> list[str]:
        pass

    @abstractmethod
    def get_chat_model(self, model_name: str) -> BaseChatModel:
        pass