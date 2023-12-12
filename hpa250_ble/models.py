from typing import Protocol
from .state import State
from .command import Command


class HPA250B(Protocol):
    async def apply_command(self, cmd: Command) -> State:
        ...

    @property
    def current_state(self) -> State:
        ...