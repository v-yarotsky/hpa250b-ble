import binascii


class StateError(Exception):
    def __init__(self, message: str, state_bytes: bytes):
        self.state_bytes = state_bytes
        return super().__init__(self, message)

    def __str__(self):
        message = super().__str__()
        return f'{message} (data: "{binascii.hexlify(self.state_bytes)}")'
