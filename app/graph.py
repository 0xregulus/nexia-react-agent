from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from app.configuration import Configuration
from app.state import InputState, State
from app.tools import TOOLS
from app.utils import load_chat_model

import logging
from app.configuration import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def call_model(state: State) -> Dict[str, List[AIMessage]]:
    configuration = Configuration.from_context()
    logger.info("Starting call_model with %d previous messages", len(state.messages))
   
    attempts = getattr(state, "attempts", 0) + 1
    if attempts > configuration.max_attempts:
        logger.warning("Max attempts reached (%d), aborting conversation", configuration.max_attempts)
        return {
            "messages": [
                AIMessage(
                    content="Desculpe, não consegui concluir o agendamento devido a um erro técnico. Por favor, tente novamente mais tarde.",
                )
            ],
            "is_last_step": True
        }

    services_list = configuration.services.get_all()
    services_names = ", ".join(service.get_name() for service in services_list)
    model = load_chat_model(configuration.model, api_key=configuration.llm_api_key).bind_tools(TOOLS)

    system_message = configuration.system_prompt.format(
        system_time=datetime.now(tz=ZoneInfo("America/Sao_Paulo")).isoformat(),
        services=services_names
    )
    logger.debug("System prompt: %s", system_message)

    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages]
        ),
    )
    logger.info("Model responded with message id: %s", response.id)

    if state.is_last_step and response.tool_calls:
        logger.info("No valid answer after last step, returning fallback message.")
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    return {"messages": [response], "attempts": attempts}


builder = StateGraph(State, input=InputState, config_schema=Configuration)
builder.add_node(call_model)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge("__start__", "call_model")

def route_model_output(state: State) -> Literal["__end__", "tools"]:
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    logger.debug("Routing model output, tool_calls: %s", bool(last_message.tool_calls))

    if not last_message.tool_calls:
        return "__end__"

    return "tools"

builder.add_conditional_edges(
    "call_model",
    route_model_output,
)
builder.add_edge("tools", "call_model")

graph = builder.compile(name="Nexia")