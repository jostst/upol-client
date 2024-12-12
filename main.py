#from components.client import WebSocketClient
from components.model import Model
from components.model import MsgTypes
from components.model import Direction
#import time
import tkinter as tk
#from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import font
#import json
import numpy as np
#import matplotlib.pyplot as plt
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
#import cv2

PASSWORD = "your_password"
MESSAGE = {"action": "example_action", "data": "example_data"}

class Morty(tk.Tk):
    def __init__(self):
        # Invoke parent constructor
        super().__init__()
        # Create the model to manage variables and WebSockets interface
        self.model = Model(self.handler, verbose=True, password=PASSWORD)
        self.title("Microscopy ORienTed proxY")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)
        self.create_widgets()
        # Bind window close event to a method
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Create the image windows
        self.imgwind = ImageWindow(self)
        self.live = False

    def create_widgets(self):
        default_font = font.nametofont("TkDefaultFont")
        bold_font = default_font.copy()
        bold_font.configure(weight="bold")

        #######################################################################
        # Connection control part
        #######################################################################
        connection_title = tk.Label(self, text="Connection", font=bold_font)
        connection_title.grid(row=0, column=0, columnspan=1, pady=(10,0), padx=5, sticky="nw")
        self.connection_frame = tk.Frame(self, borderwidth=2, relief="groove", padx=5, pady=5)
        self.connection_frame.grid(row=1, column=0, columnspan=1, pady=0, padx=5, sticky="new")
        self.connection_frame.grid_columnconfigure(0, weight=0)
        self.connection_frame.grid_columnconfigure(1, weight=1)
        self.connection_frame.grid_columnconfigure(2, weight=0)
        self.connection_frame.grid_columnconfigure(3, weight=1)
        self.connection_frame.grid_columnconfigure(4, weight=0)
        self.connection_frame.grid_columnconfigure(5, weight=0)
        
        # Host Entry
        host_label = tk.Label(self.connection_frame, text="Host:")
        host_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.host_entry = tk.Entry(self.connection_frame)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.host_entry.insert(0, "localhost")

        # Port Entry
        port_label = tk.Label(self.connection_frame, text="Port:")
        port_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.port_entry = tk.Entry(self.connection_frame)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
        self.port_entry.insert(0, "1234")

        # Connect Button
        self.connect_button = tk.Button(self.connection_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=4, padx=5, pady=5)

        # Disconnect Button
        self.disconnect_button = tk.Button(self.connection_frame, text="Disconnect", command=self.disconnect)
        self.disconnect_button.grid(row=0, column=5, padx=5, pady=5)
        
        #######################################################################
        # Camera control part
        #######################################################################
        camera_title = tk.Label(self, text="Camera", font=bold_font)
        camera_title.grid(row=2, column=0, columnspan=1, pady=(10,0), padx=5, sticky="nw")
        self.camera_frame = tk.Frame(self, borderwidth=2, relief="groove", padx=5, pady=5)
        self.camera_frame.grid(row=3, column=0, columnspan=1, pady=0, padx=5, sticky="new")
        self.camera_frame.grid_columnconfigure(0, weight=0)
        self.camera_frame.grid_columnconfigure(1, weight=1)
        self.camera_frame.grid_columnconfigure(2, weight=0)
        self.camera_frame.grid_columnconfigure(3, weight=1)
        self.camera_frame.grid_columnconfigure(4, weight=0)
        self.camera_frame.grid_columnconfigure(5, weight=0)
        
        # EXPOSURE
        exposure_label = tk.Label(self.camera_frame, text="Exposure [ms]:")
        exposure_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.exposure_entry = tk.Entry(self.camera_frame)
        self.exposure_entry.insert(0, "100.0")
        self.exposure_entry.bind('<Return>', self.send_exposure)
        self.exposure_entry.bind('<FocusOut>', self.send_exposure)
        self.exposure_entry.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky=tk.EW)

        # GAIN
        gain_label = tk.Label(self.camera_frame, text="Gain [-]:")
        gain_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.gain_entry = tk.Entry(self.camera_frame)
        self.gain_entry.insert(0, "1.0")
        self.gain_entry.bind('<Return>', self.send_gain)
        self.gain_entry.bind('<FocusOut>', self.send_gain)
        self.gain_entry.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=tk.EW)

        # SNAPSHOT
        self.snapshot_button = tk.Button(self.camera_frame, text="Snapshot", command=self.get_snapshot)
        self.snapshot_button.grid(row=0, column = 4, columnspan=1, padx=5, pady=5)

        # TOGGLE LIVE
        self.live_button = tk.Button(self.camera_frame, text="LIVE", command=self.toggle_live)
        self.live_button.grid(row=0, column = 5, columnspan=1, padx=5, pady=5)
        
        #######################################################################
        # Focus control part
        #######################################################################
        focus_title = tk.Label(self, text="Focusing", font=bold_font)
        focus_title.grid(row=4, column=0, columnspan=1, pady=(10,0), padx=5, sticky="nw")
        self.focus_frame = tk.Frame(self, borderwidth=2, relief="groove", padx=5, pady=5)
        self.focus_frame.grid(row=5, column=0, columnspan=1, pady=0, padx=5, sticky="new")
        self.focus_frame.grid_columnconfigure(0, weight=0)
        self.focus_frame.grid_columnconfigure(1, weight=1)
        self.focus_frame.grid_columnconfigure(2, weight=0)
        self.focus_frame.grid_columnconfigure(3, weight=0)
        self.focus_frame.grid_columnconfigure(4, weight=0)
        self.focus_frame.grid_columnconfigure(5, weight=0)
        self.focus_frame.grid_columnconfigure(6, weight=0)
        
        # CURRENT POSITION
        focus_current_label = tk.Label(self.focus_frame, text="Current [mm]: ")
        focus_current_label.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky=tk.W)
        self.focus_current_entry = tk.Entry(self.focus_frame)
        self.focus_current_entry.insert(0, "N/A")
        self.focus_current_entry.config(state=tk.DISABLED)
        self.focus_current_entry.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky=tk.EW)

        # GO-TO POSITION
        focus_goto_label = tk.Label(self.focus_frame, text="GoTo [mm]: ")
        focus_goto_label.grid(row=1, column=0, columnspan=1, padx=5, pady=5, sticky=tk.W)
        self.focus_goto_entry = tk.Entry(self.focus_frame)
        self.focus_goto_entry.insert(0, "0.0")
        self.focus_goto_entry.grid(row=1, column=1, columnspan=1, padx=5, pady=5, sticky=tk.EW)

        # HOME
        self.focus_home_button = tk.Button(self.focus_frame, text="Home", command=self.focus_home)
        self.focus_home_button.grid(row=0, column=2, columnspan=1, padx=5, pady=5)

        # GOTO
        self.focus_goto_button = tk.Button(self.focus_frame, text="GoTo", command=self.focus_goto)
        self.focus_goto_button.grid(row=1, column=2, columnspan=1, padx=5, pady=5)

        # UP COARSE 1 mm
        self.focus_up_coarse_button = tk.Button(self.focus_frame, text="Ʌ Ʌ", command=self.focus_up_coarse)
        self.focus_up_coarse_button.grid(row=0, column=3, columnspan=1, padx=5, pady=5)

        # DOWN COARSE 1 mm
        self.focus_down_coarse_button = tk.Button(self.focus_frame, text="V V", command=self.focus_down_coarse)
        self.focus_down_coarse_button.grid(row=1, column=3, columnspan=1, padx=5, pady=5)
        
        # UP FINE 0.1 mm
        self.focus_up_fine_button = tk.Button(self.focus_frame, text=" Ʌ ", command=self.focus_up_fine)
        self.focus_up_fine_button.grid(row=0, column=4, columnspan=1, padx=5, pady=5)

        # DOWN FINE 0.1 mm
        self.focus_down_fine_button = tk.Button(self.focus_frame, text=" V ", command=self.focus_down_fine)
        self.focus_down_fine_button.grid(row=1, column=4, columnspan=1, padx=5, pady=5)

        # JOG STEP
        focus_step_label = tk.Label(self.focus_frame, text="Jog [mm]")
        focus_step_label.grid(row=0, column=5, columnspan=1, padx=5, pady=5, sticky=tk.EW)
        self.focus_step_entry = tk.Entry(self.focus_frame)
        self.focus_step_entry.insert(0, "0.01")
        self.focus_step_entry.bind('<Return>', self.send_jog)
        self.focus_step_entry.bind('<FocusOut>', self.send_jog)
        self.focus_step_entry.grid(row=1, column=5, columnspan=1, padx=5, pady=5, sticky=tk.EW)

        # JOG UP
        self.focus_up_step_button = tk.Button(self.focus_frame, text="Ʌ", command=self.focus_up_step)
        self.focus_up_step_button.grid(row=0, column=6, columnspan=1, padx=5, pady=5)

        # JOG DOWN
        self.focus_down_step_button = tk.Button(self.focus_frame, text="V", command=self.focus_down_step)
        self.focus_down_step_button.grid(row=1, column=6, columnspan=1, padx=5, pady=5)

        #######################################################################
        # Polarization and control part
        #######################################################################
        pol_title = tk.Label(self, text="Polarization & filters", font=bold_font)
        pol_title.grid(row=6, column=0, columnspan=1, pady=(10,0), padx=5, sticky="nw")
        self.pol_frame = tk.Frame(self, borderwidth=2, relief="groove", padx=5, pady=5)
        self.pol_frame.grid(row=7, column=0, columnspan=1, pady=0, padx=5, sticky="new")
        self.pol_frame.grid_columnconfigure(0, weight=90)
        self.pol_frame.grid_columnconfigure(1, weight=10)
        self.pol_frame.grid_columnconfigure(2, weight=90)
        self.pol_frame.grid_columnconfigure(3, weight=10)
        self.pol_frame.grid_columnconfigure(4, weight=20)
        self.pol_frame.grid_columnconfigure(5, weight=20)
        self.pol_frame.grid_columnconfigure(6, weight=20)
        self.pol_frame.grid_columnconfigure(7, weight=20)
        self.pol_frame.grid_columnconfigure(8, weight=20)

        # PSG and PSA labels
        psg_label = tk.Label(self.pol_frame, text="PSG", bg="gray")
        psg_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        psg_label = tk.Label(self.pol_frame, text="PSA", bg="gray")
        psg_label.grid(row=0, column=2, columnspan=7, padx=5, pady=5, sticky=tk.EW)

        # Control labels
        rot1_label = tk.Label(self.pol_frame, text="Rotator [deg]")
        rot1_label.grid(row=1, column=0, columnspan=2, rowspan=1, padx=5, pady=5, sticky="nsew")
        rot2_label = tk.Label(self.pol_frame, text="Rotator [deg]")
        rot2_label.grid(row=1, column=2, columnspan=2, rowspan=1, padx=5, pady=5, sticky="nsew")
        flt1_label = tk.Label(self.pol_frame, text="Filter [pos]")
        flt1_label.grid(row=1, column=4, columnspan=5, rowspan=1, padx=5, pady=5, sticky=tk.EW)

        # Input fields
        self.rot1_entry = tk.Entry(self.pol_frame)
        self.rot1_entry.insert(0, "N/A")
        self.rot1_entry.bind('<Return>', self.rot1_goto)
        self.rot1_entry.bind('<FocusOut>', self.rot1_goto)
        self.rot1_entry.grid(row=2, column=0, padx=5, pady=5)
        self.rot1_home = tk.Button(self.pol_frame, text="⌂", command=self.rot1_home)
        self.rot1_home.grid(row=2, column=1, padx=5, pady=5)

        self.rot2_entry = tk.Entry(self.pol_frame)
        self.rot2_entry.insert(0, "N/A")
        self.rot2_entry.bind('<Return>', self.rot2_goto)
        self.rot2_entry.bind('<FocusOut>', self.rot2_goto)
        self.rot2_entry.grid(row=2, column=2, padx=5, pady=5)
        self.rot2_home = tk.Button(self.pol_frame, text="⌂", command=self.rot2_home)
        self.rot2_home.grid(row=2, column=3, padx=5, pady=5)

        self.flt1_selected = tk.IntVar(value=-1)
        self.flt1_trace = self.flt1_selected.trace_add('write', self.flt1_goto)
        self.ftl1_0_radio= tk.Radiobutton(self.pol_frame, text="1", value=0, variable=self.flt1_selected)
        self.ftl1_0_radio.grid(row=2, column=4, padx=5, pady=5)
        self.ftl1_1_radio= tk.Radiobutton(self.pol_frame, text="2", value=1, variable=self.flt1_selected)
        self.ftl1_1_radio.grid(row=2, column=5, padx=5, pady=5)
        self.ftl1_2_radio= tk.Radiobutton(self.pol_frame, text="3", value=2, variable=self.flt1_selected)
        self.ftl1_2_radio.grid(row=2, column=6, padx=5, pady=5)
        self.ftl1_3_radio= tk.Radiobutton(self.pol_frame, text="4", value=3, variable=self.flt1_selected)
        self.ftl1_3_radio.grid(row=2, column=7, padx=5, pady=5)

        self.flt1_home = tk.Button(self.pol_frame, text="⌂", command=self.flt1_home)
        self.flt1_home.grid(row=2, column=8, padx=5, pady=5)


        #######################################################################
        # LCTF part
        # (WL, BLACK, STATUS, TEMP)
        #######################################################################
        lctf_title = tk.Label(self, text="LCTF", font=bold_font)
        lctf_title.grid(row=8, column=0, columnspan=1, pady=(10,0), padx=5, sticky="nw")
        self.lctf_frame = tk.Frame(self, borderwidth=2, relief="groove", padx=5, pady=5)
        self.lctf_frame.grid(row=9, column=0, columnspan=1, pady=0, padx=5, sticky="new")
        self.lctf_frame.grid_columnconfigure(0, weight=90)
        self.lctf_frame.grid_columnconfigure(1, weight=5)
        self.lctf_frame.grid_columnconfigure(2, weight=5)
        self.lctf_frame.grid_columnconfigure(3, weight=10)
        self.lctf_frame.grid_columnconfigure(4, weight=10)
        self.lctf_frame.grid_columnconfigure(5, weight=45)
        self.lctf_frame.grid_columnconfigure(6, weight=45)

        lam_label = tk.Label(self.lctf_frame, text="Wavelength [nm]")
        lam_label.grid(row=0, column=0, columnspan=1, rowspan=1, padx=10, pady=5, sticky="nsew")
        self.lam_entry = tk.Entry(self.lctf_frame)
        self.lam_entry.insert(0, "N/A")
        self.lam_entry.bind('<Return>', self.lam_set)
        self.lam_entry.bind('<FocusOut>', self.lam_set)
        self.lam_entry.grid(row=1, column=0, padx=10, pady=5)

        black_label = tk.Label(self.lctf_frame, text="Blackout")
        black_label.grid(row=0, column=1, columnspan=2, rowspan=1, padx=5, pady=5, sticky="nsew")
        self.black_selected = tk.IntVar(value=0)
        self.black_trace = self.black_selected.trace_add('write', self.black_set)
        self.black_off_radio= tk.Radiobutton(self.lctf_frame, text="False", value=0, variable=self.black_selected)
        self.black_off_radio.grid(row=1, column=1, padx=5, pady=5)
        self.black_on_radio= tk.Radiobutton(self.lctf_frame, text="True", value=1, variable=self.black_selected)
        self.black_on_radio.grid(row=1, column=2, padx=5, pady=5)

        hs_temp_label = tk.Label(self.lctf_frame, text="Temperature [C]: ")
        hs_temp_label.grid(row=0, column=3, columnspan=1, padx=10, pady=5, sticky=tk.W)
        self.hs_temp_entry = tk.Entry(self.lctf_frame)
        self.hs_temp_entry.insert(0, "N/A")
        self.hs_temp_entry.config(state=tk.DISABLED)
        self.hs_temp_entry.grid(row=1, column=3, columnspan=1, padx=10, pady=5, sticky=tk.EW)

        hs_status_label = tk.Label(self.lctf_frame, text="Status")
        hs_status_label.grid(row=0, column=4, columnspan=1, padx=10, pady=5, sticky=tk.W)
        self.hs_status_entry = tk.Entry(self.lctf_frame)
        self.hs_status_entry.insert(0, "N/A")
        self.hs_status_entry.config(state=tk.DISABLED)
        self.hs_status_entry.grid(row=1, column=4, columnspan=1, padx=10, pady=5, sticky=tk.EW)
        
        hs_min_label = tk.Label(self.lctf_frame, text="min [nm]")
        hs_min_label.grid(row=0, column=5, columnspan=1, padx=10, pady=5, sticky=tk.W)
        self.hs_min_entry = tk.Entry(self.lctf_frame)
        self.hs_min_entry.insert(0, "N/A")
        self.hs_min_entry.config(state=tk.DISABLED)
        self.hs_min_entry.grid(row=1, column=5, columnspan=1, padx=10, pady=5, sticky=tk.EW)

        hs_max_label = tk.Label(self.lctf_frame, text="max [nm]")
        hs_max_label.grid(row=0, column=6, columnspan=1, padx=10, pady=5, sticky=tk.W)
        self.hs_max_entry = tk.Entry(self.lctf_frame)
        self.hs_max_entry.insert(0, "N/A")
        self.hs_max_entry.config(state=tk.DISABLED)
        self.hs_max_entry.grid(row=1, column=6, columnspan=1, padx=10, pady=5, sticky=tk.EW)

        #######################################################################
        # Acquisition
        #######################################################################
        acq_title = tk.Label(self, text="Acquisition", font=bold_font)
        acq_title.grid(row=10, column=0, columnspan=1, pady=(10,0), padx=5, sticky="nw")
        self.acq_frame = tk.Frame(self, borderwidth=2, relief="groove", padx=5, pady=5)
        self.acq_frame.grid(row=11, column=0, columnspan=1, pady=0, padx=5, sticky="new")
        self.acq_frame.grid_columnconfigure(0, weight=10)
        self.acq_frame.grid_columnconfigure(1, weight=100)
        self.acq_frame.grid_columnconfigure(2, weight=5)
        self.acq_frame.grid_columnconfigure(3, weight=10)

        acq_label = tk.Label(self.acq_frame, text="Script file")
        acq_label.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky=tk.W)
        self.acq_entry = tk.Entry(self.acq_frame)
        self.acq_entry.insert(0, "N/A")
        self.acq_entry.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky=tk.EW)
        self.acq_select_btn = tk.Button(self.acq_frame, text="📁", command=self.acq_select)
        self.acq_select_btn.grid(row=0, column=2, padx=5, pady=5,sticky=tk.EW)

        self.acq_run_btn = tk.Button(self.acq_frame, text="Run", command=self.acq_run)
        self.acq_run_btn.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)

        #######################################################################
        # Message/log part
        #######################################################################
        self.message_frame = tk.Frame(self, borderwidth=2, relief="groove", padx=5, pady=5)
        self.message_frame.grid(row=99, column=0, columnspan=1, pady=15, padx=5, sticky="sew")
        self.message_frame.grid_columnconfigure(0, weight=0)
        self.message_frame.grid_columnconfigure(1, weight=1)
        self.message_frame.grid_columnconfigure(2, weight=0)
        
        # Message Entry
        message_label = tk.Label(self.message_frame, text="Message:")
        message_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.message_entry = tk.Entry(self.message_frame)
        self.message_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        # Send Button
        self.send_button = tk.Button(self.message_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=2, padx=5, pady=5)

        # Received Messages Display
        received_label = tk.Label(self.message_frame, text="Received Messages:")
        received_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.received_messages = ScrolledText(self.message_frame, height=10)
        self.received_messages.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        self.received_messages.config(state=tk.DISABLED)
    
    #######################################################################
    # Callbacks
    #######################################################################
    def connect(self):
        self.connect_button.focus_set()
        self.model.host = self.host_entry.get()
        self.model.connect()
    
    def disconnect(self):
        self.disconnect_button.focus_set()
        self.model.disconnect()

    def send_exposure(self, event):
        self.model.cam_exposure = self.exposure_entry.get()

    def send_gain(self, event):
        self.model.cam_gain = self.gain_entry.get()

    def get_snapshot(self):
        self.snapshot_button.focus_set()
        self.model.cam_request_snapshot()

    def toggle_live(self):
        self.live_button.focus_set()
        self.model.cam_toggle_live()

    def focus_home(self):
        self.focus_home_button.focus_set()
        self.model.focus_home()

    def focus_goto(self):
        self.focus_goto_button.focus_set()
        val = self.focus_goto_entry.get()
        self.model.focus_position = val

    def focus_up_coarse(self):
        self.focus_up_coarse_button.focus_set()
        self.model.focus_step_major(Direction.UP)

    def focus_down_coarse(self):
        self.focus_down_coarse_button.focus_set()
        self.model.focus_step_major(Direction.DOWN)

    def focus_up_fine(self):
        self.focus_up_fine_button.focus_set()
        self.model.focus_step_minor(Direction.UP)

    def focus_down_fine(self):
        self.focus_down_fine_button.focus_set()
        self.model.focus_step_minor(Direction.DOWN)

    def focus_up_step(self):
        self.focus_up_step_button.focus_set()
        self.model.focus_step_jog(Direction.UP)

    def focus_down_step(self):
        self.focus_down_step_button.focus_set()
        self.model.focus_step_jog(Direction.UP)

    def send_message(self):
        self.send_button.focus_set()
        msg = self.message_entry.get()
        self.model.sender(msg, MsgTypes.MSG)

    def send_jog(self, event):
        self.model.focus_jogstep = self.focus_step_entry.get()

    def rot1_home(self):
        self.model.rot1_home()

    def rot1_goto(self, event):
        val = self.rot1_entry.get()
        self.model.rot1_position = val

    def rot2_home(self):
        self.model.rot2_home()

    def rot2_goto(self, event):
        val = self.rot2_entry.get()
        self.model.rot2_position = val

    def flt1_home(self):
        self.model.flt1_home()

    def flt1_goto(self, *args):
        val = self.flt1_selected.get()
        self.model.flt1_position = val

    def lam_set(self, event):
        val = self.lam_entry.get()
        if self.model.lam_min <= float(val) <= self.model.lam_max:
            self.model.lam_value = val
        else:
            self.log_message("ERROR: Value {} nm is out of range".format(val))
            self.model.hs_get_status()

    def black_set(self, *args):
        val = self.black_selected.get()
        self.model.black_value = val

    def acq_select(self):
        file_path = filedialog.askopenfilename(
            title="Load .input acquisition script",
            filetypes=[("Input files", "*.input")]
        )
        self.acq_entry.delete(0, tk.END)
        self.acq_entry.insert(0,  file_path)

    def acq_run(self):
        # Open the file and save contents to string
        path = self.acq_entry.get()
        with open(path, "r") as file:
            file_content = file.read()
        # Send contents to the server
        self.model.sender(file_content, MsgTypes.ACQ)


    #######################################################################
    # Halndler for interactions from the model
    #######################################################################
    def handler(self, msg, type):
        # Handle messages - just log
        if type == MsgTypes.MSG:
            if msg == "Received":
                pass
            else:
                self.log_message(msg)
        # Handle heartbeat 
        elif type == MsgTypes.HRB:
            self.log_message("Recieved heartbeat")
        # Handle list of changed values
        elif type == MsgTypes.VAL:
            if msg["module"] == "focus":
                if msg["field"] == "positionMM":
                    position = round(float(msg["value"]), 3)
                    self.focus_current_entry.config(state=tk.NORMAL)
                    self.focus_current_entry.delete(0, tk.END)
                    self.focus_current_entry.insert(0, f"{position:.3f}")
                    self.focus_current_entry.config(state=tk.DISABLED)
            elif msg["module"] == "cam":
                if msg["field"] == "Exposure":
                    exposure = round(float(msg["value"]), 3)
                    self.exposure_entry.delete(0, tk.END)
                    self.exposure_entry.insert(0, f"{exposure:.1f}")
                elif msg["field"] =="Gain":
                    gain = round(float(msg["value"]), 3)
                    self.gain_entry.delete(0, tk.END)
                    self.gain_entry.insert(0, f"{gain:.1f}")
            elif msg["module"] == "polarization":
                if msg["submodule"] == "rot1":
                    position = round(float(msg["value"]), 5)
                    self.rot1_entry.delete(0, tk.END)
                    self.rot1_entry.insert(0,  f"{position:.3f}")
                elif msg["submodule"] == "rot2":
                    position = round(float(msg["value"]), 5)
                    self.rot2_entry.delete(0, tk.END)
                    self.rot2_entry.insert(0,  f"{position:.3f}")
                elif msg["submodule"] == "flt1":
                    position = int(msg["value"])
                    self.flt1_selected.trace_remove('write', self.flt1_trace)
                    self.flt1_selected.set(position)
                    self.flt1_trace = self.flt1_selected.trace_add('write', self.flt1_goto)
            elif msg["module"] == 'hyperspectral':
                if msg["field"] == "wavelength":
                    lam = round(float(msg["value"]), 5)
                    self.lam_entry.delete(0, tk.END)
                    self.lam_entry.insert(0,  f"{lam:.3f}")
                elif msg["field"] == "black":
                    black = msg["value"]
                    self.black_selected.trace_remove('write', self.black_trace)
                    if black:
                        self.black_selected.set(1)
                        self.lam_entry.config(state=tk.DISABLED)
                    else:
                        self.black_selected.set(0)
                        self.lam_entry.config(state=tk.NORMAL)
                    self.black_trace = self.black_selected.trace_add('write', self.black_set)
                elif msg["field"] == "temperature":
                    temp = round(float(msg["value"]), 3)
                    self.hs_temp_entry.config(state=tk.NORMAL)
                    self.hs_temp_entry.delete(0, tk.END)
                    self.hs_temp_entry.insert(0, f"{temp:.3f}")
                    self.hs_temp_entry.config(state=tk.DISABLED)
                elif msg["field"] == "status":
                    status = msg["value"]
                    self.hs_status_entry.config(state=tk.NORMAL)
                    self.hs_status_entry.delete(0, tk.END)
                    self.hs_status_entry.insert(0, status)
                    self.hs_status_entry.config(state=tk.DISABLED)
                elif msg["field"] == "range":
                    min = round(float(msg["min"]), 5)
                    self.model.lam_min = min
                    max = round(float(msg["max"]), 5)
                    self.model.lam_max = max
                    self.hs_min_entry.config(state=tk.NORMAL)
                    self.hs_min_entry.delete(0, tk.END)
                    self.hs_min_entry.insert(0, f"{min:.3f}")
                    self.hs_min_entry.config(state=tk.DISABLED)
                    self.hs_max_entry.config(state=tk.NORMAL)
                    self.hs_max_entry.delete(0, tk.END)
                    self.hs_max_entry.insert(0, f"{max:.3f}")
                    self.hs_max_entry.config(state=tk.DISABLED)
            else:        
                print("Not implemented")
        # Handle updated image
        elif type == MsgTypes.IMG:
            self.imgwind.img = msg

    def log_message(self, msg):
            self.received_messages.config(state=tk.NORMAL)  # Enable editing to append new message
            self.received_messages.insert(tk.END, msg + "\n")
            self.received_messages.config(state=tk.DISABLED)  # Disable editing
            self.received_messages.see(tk.END)  # Scroll to the end to show the new message

    def on_closing(self):
        # Add cleanup or other necessary tasks before closing the window
        self.model.disconnect()
        self.destroy()

class ImageWindow:
    def __init__(self, master):
        # Generate dummy image to start the window up
        img = np.random.rand(600,960)
        img = img.astype(np.float32)
        #img = cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        img = self.normalize_image(img)
        img = img.astype(np.uint8)
        img = Image.fromarray(img, mode='L') 


        self.plot_window = tk.Toplevel(master)
        self.plot_window.title("Image display")
        self.plot_window.geometry("960x600")

        # Create the photo image and show it
        img = ImageTk.PhotoImage(img)
        self.img_label = tk.Label(self.plot_window, image=img)
        self.__img = img
        self.img_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=0, pady=0)

    @property
    def img(self):
        return self.__img
    
    @img.setter
    def img(self, img):
        # Create a suitable image
        img = ImageTk.PhotoImage(img)

        # Update the image
        self.img_label.configure(image=img)
        self.__img = img
        self.plot_window.update()

    def normalize_image(self, img, alpha=0, beta=255):
        # Convert the image to float type, necessary for proper division
        img = img.astype(np.float32)
        
        # Get the minimum and maximum pixel values from the image
        min_val = np.min(img)
        max_val = np.max(img)
        
        # Normalize the image to the range [alpha, beta]
        normalized_img = (img - min_val) / (max_val - min_val) * (beta - alpha) + alpha
        
        # Convert normalized image to uint8 if beta is 255 (common for images)
        if beta == 255:
            normalized_img = np.clip(normalized_img, alpha, beta).astype(np.uint8)
        
        return normalized_img

def main():
    app = Morty()
    # Add any further initialization logic here
    app.mainloop()

if __name__ == "__main__":
    main()
