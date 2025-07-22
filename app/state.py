from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, Optional

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated


@dataclass
class InputState:
    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )


@dataclass
class State(InputState):
    is_last_step: IsLastStep = field(default=False)

    intent: Optional[str] = None
    user_full_name: Optional[str] = None
    service_name: Optional[str] = None
    professional_name: Optional[str] = None
    appointment_day: Optional[str] = None
    appointment_time: Optional[str] = None
    appointment_status: Optional[str] = None
    appointment_message: Optional[str] = None