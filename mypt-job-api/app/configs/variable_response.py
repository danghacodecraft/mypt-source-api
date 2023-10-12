import enum

class ERROR_MESSAGE(enum.Enum):
    SYSTEM : str = "Lỗi hệ thống"
    
class STATUS(enum.Enum):
    SUCCESS : int = 1
    NO_LOGIN : int = 2
    IS_VALID : int = 4
    ERROR_SYSTEM : int = 5
    SESSION_EXPIRED : int = 7