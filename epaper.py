from enum import Enum
import enum
import time
import RPi.GPIO as GPIO
import spidev

class DispState(Enum):
    DISPLAY_TURN_ON  = 1
    DISPLAY_TURN_OFF = 0

class DispOrientation(Enum):
    LANDSCAPE = 1
    PORTRAIT  = 2

class ResponseStatus(Enum):
    EP_SW_NORMAL_PROCESSING              = 0x9000 # Command executed successfully
    EP_SW_MEMORY_FAILURE                 = 0x6581 # An error occurred while interfacing external memory
    EP_SW_WRONG_LENGTH                   = 0x6700 # Incorrect length (invalid Lc value or command too short or too long)
    EP_FRAMEBUFFER_SLOT_NOT_AVAILABLE    = 0x6981 # Frambuffer slot number is either the last displayed slot, or the number is out of range
    EP_SW_WRONG_PARAMETERS_P1P2          = 0x6A00 # Invalid P1 or P2 field
    EP_FRAMEBUFFER_SLOT_OVERRUN          = 0x6A84 # Framebuffer slot overridden
    EP_SW_INVALID_LE                     = 0x6D00 # Specified value for Le field is invalid
    EP_SW_INSTRUCTION_NOT_SUPPORTED      = 0x6D00 # Command not supported
    EP_SW_GENERAL_ERROR                  = 0x6F00 # Internal TCS2 MCU reset triggered due to abnormal behavior the command was not executed properly */
    EP_DISPLAY_NOT_AVAILABLE             = 0x9D54 # Display drivers are broken or display is not attached
    EP_DC_DC_ERROR                       = 0x9E   # Power management IC reports error

class BufferSlot(Enum):
    BUFFER_SLOT_INDEX_0                  = 0x00
    BUFFER_SLOT_INDEX_1                  = 0x01
    BUFFER_SLOT_INDEX_2                  = 0x02
    BUFFER_SLOT_INDEX_3                  = 0x03
    BUFFER_SLOT_INDEX_4                  = 0x04
    BUFFER_SLOT_INDEX_5                  = 0x05
    BUFFER_SLOT_INDEX_6                  = 0x06

class CmdType(Enum):
    IMAGE_DATA_CMD                       = 0x01
    DISP_CTL_CMD                         = 0x02
    DEVICE_INFO_CMD                      = 0x03
    SYSTEM_INFO_CMD                      = 0x04
    SENSOR_DATA_CMD                      = 0x05

class CmdName(Enum):
    UPLOAD_IMAGE_DATA                    = 0x01
    GET_IMAGE_DATA                       = 0x02
    GET_CHECK_SUM                        = 0x03
    RESET_DATA_POINTER                   = 0x04
    IMAGE_ERASE_FRAME_BUFFER             = 0x05
    IMAGE_UPLOAD_SET_ROI                 = 0x06
    IMAGE_UPLOAD_FIX_VAL                 = 0x07
    IMAGE_UPLOAD_COPY_SLOTS              = 0x08
    DISPLAY_UPDATE_DEFAULT1              = 0x09
    DISPLAY_UPDATE_DEFAULT2              = 0x0A
    DISPLAY_UPDATE_FLASHLESS             = 0x0B
    DISPLAY_UPDATE_FLASHLESS_INVERTED    = 0x0C            
    SET_SLOTS_NUMBER                     = 0x0D         
    GET_DEVICE_INFO                      = 0x0E         
    GET_DEVICE_ID                        = 0x0F
    GET_SYSTEM_INFO                      = 0x10
    GET_SYSTEM_VERSION_CODE              = 0x11           
    GET_SENSOR_DATA_RAW                  = 0x12
    GET_SENSOR_DATA_DEG                  = 0x13

class DispUpdate(Enum):
    DISPLAY_UPDATE_BWB_TYPE                = 0 # Default
    DISPLAY_UPDATE_WBW_TYPE                = 1
    DISPLAY_UPDATE_FLASHLESS_TYPE          = 2
    DISPLAY_UPDATE_FLASHLESS_INVERTED_TYPE = 3


class Epaper:

    __MIN_X = 0
    __MAX_X = 0
    __MIN_Y = 0
    __MAX_Y = 0

    __currentDispState = DispState.DISPLAY_TURN_OFF
    __dispOrientation = DispOrientation.LANDSCAPE
    __checkSum = 0
    __deviceInfo = ""
    __deviceID = []
    __systemInfo = []
    __systemVersionCode = []
    __tempRaw = 0
    __tempDeg = 0
    __lastState = ResponseStatus.EP_DISPLAY_NOT_AVAILABLE
    __lastDisplayedSlot = BufferSlot.BUFFER_SLOT_INDEX_0
    __maxSlots = 0

    __spi = spidev.SpiDev()

    def __PinoutInit(self):
        # Blink PIN
        GPIO.setwarnings(False)                            # Ignore warning for now
        GPIO.setmode(GPIO.BOARD)                           # Use physical pin numbering
        GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)          # Set pin 8 to be an output pin and set initial value to low (off)

        # TC Enable pin
        GPIO.setup(10, GPIO.OUT, initial=GPIO.HIGH)        # Set pin 10 to be an output pin and set initial value to high (on)

        # TC Bussy pi
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)# Set pin 12 to be an input pin and set initial value to be pulled low (off)

    """
    Start transmission pulse.
    """
    def __StartTransmission():
        pass

    """
    End transmission pulse.
    """
    def __EndTransmission():
        pass#comment

    """
    Wait while the command will be end.
    """
    def __BusyWait(self):
        time.sleep(0.01)
        while GPIO.input(12) == 0:
            time.sleep(0.01)

    """
    Turn on the display.
    """
    def DisplayOn(self):
        # Enable disp by EN = 0
        GPIO.output(10, GPIO.LOW)
        time.sleep(0.01)

        self.__BusyWait()# Bussy wait

        if((GPIO.input(10) == 0) and (GPIO.input(12) == 1)):
            return True
        else:
            return False




    """
    Turn off the display.
    """
    def DisplayOff(self):
        # Disable disp by EN = 1
        GPIO.output(10, GPIO.HIGH)

    
    """
    Initialization of display.
    """
    def __init__(self, dispState, dispOrientation):
        self.__currentDispState = dispState
        self.__dispOrientation  = dispOrientation

        self.__MIN_X = 0
        self.__MAX_X = 1000
        self.__MIN_Y = 0
        self.__MAX_Y = 1000

        # Settings (for example)
        self.__spi.open(0, 0)              # Opev spi driver
        self.__spi.max_speed_hz = 6000000  # Freq
        self.__spi.mode = 3                # Mode 3
        
        self.__PinoutInit()

        if (dispState == DispState.DISPLAY_TURN_ON):
            self.DisplayOn()
            print(f"Display state = {self.__currentDispState}, orientation = {self.__dispOrientation}")
            #pass
        else:
            self.DisplayOff()

    def Blink(self):
        GPIO.output(8, GPIO.HIGH)   # Turn on
        time.sleep(0.5)             # Sleep for 1 second
        GPIO.output(8, GPIO.LOW)    # Turn off
        time.sleep(0.5)             # Sleep for 1 second
        print("Blink ...")

    """
    The command returns information on system hardware. String data is specific for the particular device
    type and is constant for the same type of devices if no hardware differences occur.
    [String: ?MpicoSys TC2-E133-320_v1.0? terminated by 0x00 byte] + 0x9000 status code in
    case of TC2-E133-320_v1.0, or 2-byte error status code.
    """
    def GetDeviceInfo(self):
        pass
    
    """
    The command returns unique device ID number.
    [20 bytes of data] + 0x9000 status code, or 2-byte error status code.
    """
    def GetDeviceID(self):
        pass
    
    """
    The command returns information on system firmware.
    [String: ?MpicoSys TC2-E133-320_fA_BIN? terminated by 0x00 byte] + 0x9000 status code in
    case of TC2-E133-320_v1.0, or 2-byte error status code.
    """
    def GetDeviceInfo(self):
        pass
    
    """
    The command returns information on system version
    0x D0 B2 00 00 00 00 00 00 3E 09 05 00 00 00 00 00 + 0x9000 status code in case of
    TCS2-E133-320_v1.0, or 2-byte error status code.
    """
    def GetSystemVersionCode(self):
        pass
    
    """
    This command returns the temperature value measured by the TCS2 temperature sensor. The sensor
    is built in the TCM2 board and is included in the TCon reference design. The measurement is based on
    a NCP18WB473E03RB thermistor and 8-bit ADC
    """
    def GetSensorDataRaw(self):
        pass
    
    """
    This command returns the temperature value measured by the TCS2 temperature sensor. The sensor
    is built in the TCM2 board and is included in the TCon reference design. The measurement is based on
    a NCP18WB473E03RB thermistor and 8-bit ADC.
    """
    def GetSensorDataDeg(self):
        pass
    
    """
    This command return info abou controller.
    """
    def GetControllerInfo(self):
        
        # Internal buffer
        buffer = []

        # Create and send command
        cmd = [0, 0, 0, 0]
        cmd[0] = 0x31 # INS
        cmd[1] = 0x01 # P1
        cmd[2] = 0x01 # P2
        cmd[3] = 0x00 # Le
        self.__spi.writebytes(cmd)
        
        # Bussy wait
        self.__BusyWait()

        # Read data to buffer
        buffer = self.__spi.readbytes(27)
        
        # Convert to string
        self.__deviceInfo = str(''.join(chr(val) for val in buffer))

        # Return value
        return print(self.__deviceInfo)
