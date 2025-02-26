from enum import Enum

class ProcessState(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"