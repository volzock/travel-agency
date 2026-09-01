from langchain_openai import ChatOpenAI

from .environment import Environment


class LLMFactory:

    __cache: dict[int, ChatOpenAI] = {}

    @classmethod
    def get_llm(cls, temperature: int=0, required_new=False, *args, **kwargs) -> ChatOpenAI:
        if required_new:
            return ChatOpenAI(base_url=Environment.BASE_URL, 
                                                  api_key=Environment.API_KEY, 
                                                  model=Environment.MODEL,
                                                  temperature=temperature,
                                                  **kwargs)
        
        if temperature not in cls.__cache:
            cls.__cache[temperature] = ChatOpenAI(base_url=Environment.BASE_URL, 
                                                  api_key=Environment.API_KEY, 
                                                  model=Environment.MODEL,
                                                  temperature=temperature,
                                                  **kwargs)
        return cls.__cache.get(temperature)