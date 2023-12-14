from hpa250_ble.models import HPA250B
from hpa250_ble.command import Command
from hpa250_ble.state import State
from hpa250_ble.enums import Preset, Backlight, VOCLight


class VirtualHPA250B(HPA250B):
    _state: State

    def __init__(self, initial_state=State.empty()):
        self._state = initial_state
        self._commands: list[Command] = []

    @property
    def name(self) -> str:
        return "VirtualHPA250B"

    @property
    def commands(self) -> list[Command]:
        return self._commands

    async def apply_command(self, cmd: Command):
        self._commands.append(cmd)

        is_on = self._state.is_on
        preset = self._state.preset
        backlight = self._state.backlight
        voc_light = self._state.voc_light
        timer = self._state.timer

        if cmd.is_toggle_power:
            if self._state.is_on:
                self._state = State.empty()
                return self._state
            else:
                is_on = True
                backlight = Backlight.ON
                preset = Preset.GENERAL

        if cmd.is_toggle_germ:
            preset = Preset.GERM
            voc_light = None
        elif cmd.is_toggle_general:
            preset = Preset.GENERAL
            voc_light = None
        elif cmd.is_toggle_allergen:
            preset = Preset.ALLERGEN
            voc_light = None
        elif cmd.is_toggle_turbo:
            preset = Preset.TURBO
            voc_light = None
        elif cmd.is_toggle_auto_voc and cmd.is_toggle_auto_pollen:
            preset = Preset.AUTO_VOC_POLLEN
            voc_light = VOCLight.GREEN
        elif cmd.is_toggle_auto_voc:
            preset = Preset.AUTO_VOC
            voc_light = VOCLight.GREEN
        elif cmd.is_toggle_auto_pollen:
            preset = Preset.AUTO_POLLEN
            voc_light = VOCLight.GREEN

        if cmd.is_cycle_light:
            if backlight == Backlight.ON:
                backlight = Backlight.DIM
            elif backlight == Backlight.DIM:
                backlight = Backlight.OFF
            else:
                backlight = Backlight.ON

        if cmd.is_timer_up:
            if timer is None:
                timer = 1
            elif timer == 18:
                timer = None
            else:
                timer += 1

        if cmd.is_timer_down:
            if timer is None:
                timer = 18
            elif timer == 1:
                timer = None
            else:
                timer -= 1

        self._state = State(is_on, preset, backlight, voc_light, timer)
        return self._state

    @property
    def current_state(self) -> State:
        return self._state
