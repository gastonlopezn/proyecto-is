import enum

class StateType(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"