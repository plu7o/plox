class Returns(Exception):
    def __init__(self, value) -> None:
        self.value = value
