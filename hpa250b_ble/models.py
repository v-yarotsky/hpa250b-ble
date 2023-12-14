from typing import Protocol
from .command import Command
from .state import State


class HPA250BModel(Protocol):
    async def apply_command(self, cmd: Command):
        ...

    @property
    def current_state(self) -> State:
        ...

    @property
    def name(self) -> str:
        ...
