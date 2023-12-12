from .state import State
from .command import Command
from .enums import Preset


def reconcile(current: State, desired: State) -> Command:
    if current.is_on != desired.is_on:
        return Command().toggle_power()

    command = Command()
    if (c := current.preset) != (d := desired.preset):
        if d == Preset.AUTO_VOC_POLLEN:
            if c == Preset.AUTO_VOC:
                command.toggle_auto_pollen()
            elif c == Preset.AUTO_POLLEN:
                command.toggle_auto_voc()
            else:
                command.toggle_auto_voc()
                command.toggle_auto_pollen()
        elif d == Preset.AUTO_VOC:
            if c == Preset.AUTO_VOC_POLLEN:
                command.toggle_auto_pollen()
            elif c == Preset.AUTO_POLLEN:
                command.toggle_auto_pollen()
                command.toggle_auto_voc()
            else:
                command.toggle_auto_voc()
        elif d == Preset.AUTO_POLLEN:
            if c == Preset.AUTO_VOC_POLLEN:
                command.toggle_auto_voc()
            elif c == Preset.AUTO_VOC:
                command.toggle_auto_voc()
                command.toggle_auto_pollen()
            else:
                command.toggle_auto_pollen()
        elif d == Preset.GERM:
            command.toggle_germ()
        elif d == Preset.GENERAL:
            command.toggle_general()
        elif d == Preset.ALLERGEN:
            command.toggle_allergen()
        elif d == Preset.TURBO:
            command.toggle_turbo()

    if (c := current.backlight) != (d := desired.backlight):
        command.cycle_light()

    if (c := current.timer) != (d := desired.timer):
        if d is None:
            command.timer_down()
        else:
            if c is None:
                command.timer_up()
            elif c < d:
                command.timer_up()
            else:
                command.timer_down()

    return command
