from .models import HPA250B
from .state import State


class ReconcileError(Exception):
    def __init__(self, message: str, device: HPA250B, desired_state: State):
        self.device_name = device.name
        self.actual_state = device.current_state
        self.desired_state = desired_state
        return super().__init__(self, message)

    def __str__(self):
        message = super().__str__()
        return (
            f"{message}\n"
            + f"device name:\t{self.device_name}\n"
            + f"actual state:\t{self.actual_state}\n"
            + f"desired state:\t{self.desired_state}"
        )


class BTError(Exception):
    def __init__(self, message: str):
        return super().__init__(self, message)


class BTClientDisconnectedError(BTError):
    pass
