"""Utility & helper functions."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage
import pendulum


DAY_MAP = {
        "segunda-feira": pendulum.MONDAY, "lunes": pendulum.MONDAY,
        "terça-feira": pendulum.TUESDAY, "martes": pendulum.TUESDAY,
        "quarta-feira": pendulum.WEDNESDAY, "miércoles": pendulum.WEDNESDAY,
        "quinta-feira": pendulum.THURSDAY, "jueves": pendulum.THURSDAY,
        "sexta-feira": pendulum.FRIDAY, "viernes": pendulum.FRIDAY,
        "sábado": pendulum.SATURDAY, "sabado": pendulum.SATURDAY,
        "domingo": pendulum.SUNDAY 
    }


def convert_history_to_messages(history):
    messages = []
    for role, text in history:
        if role == "Usuário":
            messages.append(HumanMessage(content=text))
        elif role == "Nexia":
            messages.append(AIMessage(content=text))
    return messages


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str, api_key: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider, api_key=api_key)