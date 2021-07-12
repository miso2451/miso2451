# Import Modules
from enum import Enum
import enum
import epaper

class SystemStates(Enum):
    SYSTEM_STATE_INIT = 0
    SYSTEM_STATE_IDLE = 1

class System:
    # Current state
    __currentState = SystemStates.SYSTEM_STATE_INIT
    # Previous state
    __prevState    = SystemStates.SYSTEM_STATE_INIT
    # Epaper instance
    ePaper = None

    def __init__(self):
        self.__currentState = SystemStates.SYSTEM_STATE_INIT
        self.__prevState    = SystemStates.SYSTEM_STATE_INIT

        # Create instance of Epaper
        self.ePaper = epaper.Epaper(epaper.DispState.DISPLAY_TURN_ON, epaper.DispOrientation.LANDSCAPE)

    """
    Get current state.
    """
    def GetCurrentState(self):
        return self.__currentState

    """
    Set current state.
    """
    def SetCurrentState(self, state):
        self.__currentState = state

    """
    Get previous state.
    """
    def GetPrevState(self):
        return self.__prevState

    """
    Set previous state.
    """
    def SetPrevState(self, state):
        self.__prevState = state

# System data
systemData = System()

def Tasks():
    # Infinite loop
    #while True:
        # INIT STATE
        if (systemData.GetCurrentState() is SystemStates.SYSTEM_STATE_INIT):
            print(systemData.GetCurrentState())
            systemData.ePaper.GetControllerInfo()
            #systemData.SetCurrentState(SystemStates.SYSTEM_STATE_IDLE)
            #systemData.SetPrevState(SystemStates.SYSTEM_STATE_INIT)
        
        # IDLE STATE
        elif (systemData.GetCurrentState() is SystemStates.SYSTEM_STATE_IDLE):
            print(systemData.GetCurrentState())
            systemData.ePaper.Blink()
            systemData.SetCurrentState(SystemStates.SYSTEM_STATE_IDLE)
            systemData.SetPrevState(SystemStates.SYSTEM_STATE_IDLE)
        
        else:
            pass

