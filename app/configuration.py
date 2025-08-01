from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Annotated

from langchain_core.runnables import ensure_config
from langgraph.config import get_config

from app.prompts import SYSTEM_PROMPT
from app.services import Services
from app.settings import settings


@dataclass
class Configuration:

    system_prompt: str = field(
        default=SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
            "This prompt sets the context and behavior for the agent."
        },
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai/gpt-4o",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
        },
    )

    llm_api_key: str = field(
        default=settings.LLM_API_KEY,
        metadata={"description": "LLM API Key for authenticating with LLM services."}
    )

    services: Services = field(
        default_factory=lambda: Services(),
        metadata={
            "description": "Object that contains all the services available for booking."
        }
    )

    max_attempts: int = field(
        default=3,
        metadata={
            "description": "The maximum number of attempts to make to the LLM."
        }
    )

    @classmethod
    def from_context(cls) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        try:
            config = get_config()
        except RuntimeError:
            config = None
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})