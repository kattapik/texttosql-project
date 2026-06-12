from typing import Optional
from app.domain.interfaces import ILLMService
from app.infrastructure.gemini_llm import GeminiService
from app.infrastructure.openai_compat_llm import OpenAICompatibleService

PROVIDER_PRESETS = {
    "gemini": {
        "label": "Google Gemini",
        "class": GeminiService,
        "default_model": "gemini-3-flash-preview",
        "base_url": None
    },
    "openrouter": {
        "label": "OpenRouter",
        "class": OpenAICompatibleService,
        "default_model": "openai/gpt-4o-mini",
        "base_url": "https://openrouter.ai/api/v1"
    },
    "zai": {
        "label": "ZAI",
        "class": OpenAICompatibleService,
        "default_model": "zai-default-model",
        "base_url": "https://api.z.ai/v1"
    },
    "custom": {
        "label": "Custom Provider",
        "class": OpenAICompatibleService,
        "default_model": "",
        "base_url": ""
    }
}

class LLMFactory:
    @staticmethod
    def create(provider: str, api_key: str,
               model_name: Optional[str] = None,
               base_url: Optional[str] = None) -> ILLMService:
        preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["gemini"])
        model = model_name or preset["default_model"]
        url = base_url or preset["base_url"]

        if preset["class"] == GeminiService:
            return GeminiService(api_key=api_key, model_name=model)

        return OpenAICompatibleService(
            api_key=api_key,
            base_url=url,
            model_name=model
        )
