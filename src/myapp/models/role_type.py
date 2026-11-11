import enum

class RoleType(str, enum.Enum):
    ADMIN = "ADMIN"
    POLYUSER = "POLYUSER"
    