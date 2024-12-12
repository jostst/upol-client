from time import sleep
import json
import pickle
import base64
import io
from PIL import Image
import numpy as np
from enum import Enum
from components.client import WebSocketClient

class MsgTypes(Enum):
    MSG = 1     # Text message to the client
    CON = 2     # Connection message
    VAL = 3     # Value changed
    IMG = 4     # Image frame
    HRB = 5     # Heartbeat
    ACQ = 6     # Acquisition script

class Direction(Enum):
    UP = 1
    DOWN = -1

class Model:
    def __init__(self, handler, host="localhost", port=1234, password="your_password", verbose=False):
        self.handler = handler
        self.host = host
        self.port = port
        self.password = password
        self.connected = False
        self.thread = None
        self.verbose = verbose

        # Camera properties
        self.__cam_exposure = 100.0
        self.__cam_gain = 1
        self.__cam_live = False

        # Stage properties
        self.__focus_jogstep = 0.01
        self.__focus_position = 0

        # Polarization properties
        self.__rot1_position = 0
        self.__rot2_position = 0
        self.__flt1_position = 0

        # Hyperspectral properties
        self.__lam_value = 0
        self.lam_min = 420
        self.lam_max = 730
        self.__black_value = 0

    def connect(self):
        '''CONNECT will connect to the WebSocket server using WebSocketClient.'''
        # Construct the thread to run the client
        self.thread = WebSocketClient(self.host, self.port, self.password, self.reciever)

        # Start the thread
        self.thread.start()

        # Wait for the server to initialize
        while not self.connected:
            sleep(0.1)
        
        # Initialize hardware on conenction
        self.__cam_initialize()
        self.focus_home()
        self.rot1_home()
        self.rot2_home()
        self.flt1_home()
        self.hs_get_status()

    def disconnect(self):
        '''DISCONNECT will drop the connection by stopping the client thread and synchronize.'''
        if self.thread:
            self.thread.stop()
            while self.connected:
                sleep(0.1)
            self.thread.join()

    def sender(self, msg, type):
        '''SENDER will check for active connection then dump the JSON payload as string to the thread.'''
        if self.connected:
            if type == MsgTypes.MSG:
                data = json.dumps({"type":MsgTypes.MSG.value, "data":msg})
                self.thread.send(data)

            if type == MsgTypes.VAL:
                data = json.dumps({"type":MsgTypes.VAL.value, "data":msg})
                self.thread.send(data)

            if type == MsgTypes.ACQ:
                data = json.dumps({"type":MsgTypes.ACQ.value, "data":msg})
                self.thread.send(data)

        # In verbose mode, print what was sent
        if self.connected and self.verbose:
            print("S: " + data)

    def reciever(self, msg):
        '''RECIEVER will parse payload and send GUI oriented updates to the application.'''
        data = json.loads(msg)
        if data["type"] == MsgTypes.MSG.value:
            self.handler(data["data"], MsgTypes.MSG)
        if data["type"] == MsgTypes.HRB.value:
            self.handler(None, MsgTypes.HRB)
        if data["type"] == MsgTypes.IMG.value:
            img_str = data["data"]
            img_data = base64.b64decode(img_str)
            img = Image.open(io.BytesIO(img_data))
            self.handler(img, MsgTypes.IMG)
        if data["type"] == MsgTypes.VAL.value:
            msg = data["data"]
            self.handler(msg, MsgTypes.VAL)

        # In verbose mode, print what was recieved
        if self.verbose:
            if data["type"] == MsgTypes.IMG.value:
               pass
            else:
                print("R: " + str(data))

    @property
    def connected(self):
        if self.thread:
            return self.thread.open
        else:
            return False
    
    @connected.setter
    def connected(self, val):
        pass

    def __cam_initialize(self):
        self.cam_exposure = self.cam_exposure
        self.cam_gain = self.cam_gain
        self.cam_live = self.cam_live

    @property
    def cam_exposure(self):
        return self.__cam_exposure
    
    @cam_exposure.setter
    def cam_exposure(self, value):
        self.__cam_exposure = value
        msg = {"module":"cam", "field":"ExposureTime", "value":value}
        self.sender(msg, MsgTypes.VAL)

    @property
    def cam_gain(self):
        return self.__cam_gain
    
    @cam_gain.setter
    def cam_gain(self, value):
        self.__cam_gain = value
        msg = {"module":"cam", "field":"Gain", "value":value}
        self.sender(msg, MsgTypes.VAL)

    @property
    def cam_live(self):
        return self.__cam_live
    
    @cam_live.setter
    def cam_live(self, value):
        self.__cam_live = value
        msg = {"module":"cam", "field":"Live", "value":value}
        self.sender(msg, MsgTypes.VAL)

    def cam_toggle_live(self):
        self.cam_live = not self.cam_live
    
    def cam_request_snapshot(self):
        msg = {"module":"cam", "field":"Snapshot", "value":True}
        self.sender(msg, MsgTypes.VAL)
        # Server goes into snapshot mode on request for snapshot!
        self.cam_live = False

    @property
    def focus_jogstep(self):
        return self.__focus_jogstep
    
    @focus_jogstep.setter
    def focus_jogstep(self, value):
        msg = {"module":"focus", "field":"set_jog", "value":value}
        self.sender(msg, MsgTypes.VAL)

    @property
    def focus_position(self):
        return self.__focus_position
    
    @focus_position.setter
    def focus_position(self, value):
        msg = {"module":"focus", "field":"goto", "value":value}
        self.sender(msg, MsgTypes.VAL)

    def focus_home(self):
        msg = {"module":"focus", "field":"home", "value":True}
        self.sender(msg, MsgTypes.VAL)

    def focus_step_major(self, direction: Direction):
        msg = {"module":"focus", "field":"step_major", "value":direction.value}
        self.sender(msg, MsgTypes.VAL)

    def focus_step_minor(self, direction: Direction):
        msg = {"module":"focus", "field":"step_minor", "value":direction.value}
        self.sender(msg, MsgTypes.VAL)
    
    def focus_step_jog(self, direction: Direction):
        msg = {"module":"focus", "field":"step_jog", "value":direction.value}
        self.sender(msg, MsgTypes.VAL)

    @property
    def rot1_position(self):
        return self.__rot1_position
    
    @rot1_position.setter
    def rot1_position(self, value):
        msg = {"module":"polarization", "submodule":"rot1", "field":"goto", "value":value}
        self.sender(msg, MsgTypes.VAL)
        self.__rot1_position = value

    def rot1_home(self):
        msg = {"module":"polarization", "submodule":"rot1", "field":"home", "value":True}
        self.sender(msg, MsgTypes.VAL)

    @property
    def rot2_position(self):
        return self.__rot2_position
    
    @rot2_position.setter
    def rot2_position(self, value):
        msg = {"module":"polarization", "submodule":"rot2", "field":"goto", "value":value}
        self.sender(msg, MsgTypes.VAL)
        self.__rot2_position = value
    
    def rot2_home(self):
        msg = {"module":"polarization", "submodule":"rot2", "field":"home", "value":True}
        self.sender(msg, MsgTypes.VAL)

    @property
    def flt1_position(self):
        return self.__flt1_position
    
    @flt1_position.setter
    def flt1_position(self, value):
        msg = {"module":"polarization", "submodule":"flt1", "field":"goto", "value":value}
        self.sender(msg, MsgTypes.VAL)

    def flt1_home(self):
        msg = {"module":"polarization", "submodule":"flt1", "field":"home", "value":True}
        self.sender(msg, MsgTypes.VAL)

    def hs_get_status(self):
        msg = {"module":"hyperspectral", "field":"status", "value":True}
        self.sender(msg, MsgTypes.VAL)

    @property
    def lam_value(self):
        return self.__lam_value

    @lam_value.setter
    def lam_value(self, value):
        msg = {"module":"hyperspectral", "field":"wavelength", "value":value}
        self.sender(msg, MsgTypes.VAL)

    @property
    def black_value(self):
        return self.__black_value

    @black_value.setter
    def black_value(self, value):
        msg = {"module":"hyperspectral", "field":"black", "value":value}
        self.sender(msg, MsgTypes.VAL)