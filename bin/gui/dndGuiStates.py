from enum import Enum

class DndGuiStates(Enum):
    WAIT_FOR_INPUT = 1
    READY_INPUT = 2
    PROCESSING_INPUT = 3