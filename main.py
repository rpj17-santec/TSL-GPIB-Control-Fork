# -*- coding: utf-8 -*-

import sys
import time
import logging
import datetime
import platform
import pyvisa as visa
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox
from drivers import functions, tsl_control_tool_gui

# About
__version__ = "1.2.0-lan"
__date__ = "2024-10-24"
__organization__ = "Santec Holdings Corporation"

# Date and time for logging
dt = datetime.datetime.now()
dt = dt.strftime("%Y%m%d")

# Logger details
OUTPUT_LOGGER_NAME = f"output_{dt}.log"

# Configure logging
logging.basicConfig(
    filename=OUTPUT_LOGGER_NAME,
    level=logging.DEBUG,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a separate logger for PyVISA
pyvisa_logger = logging.getLogger('pyvisa')
pyvisa_logger.setLevel(logging.DEBUG)

app = QtCore.QCoreApplication.instance()
if app is None:
    app = QtWidgets.QApplication(sys.argv)
TSL_Control_Tool = QtWidgets.QMainWindow()
app.setStyle('Fusion')
ui = tsl_control_tool_gui.UiTslControlTool()
ui.setupUi(TSL_Control_Tool)

icon = QtGui.QIcon()
icon.addPixmap(QtGui.QPixmap("utils/santec.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
TSL_Control_Tool.setWindowIcon(icon)


def log_run_info():
    logging.info(f"Project Version: {__version__}, Date: {__date__}")
    info = [
        f"Python Version: {sys.version}",
        f"Python Implementation: {platform.python_implementation()}"
        f"Architecture: {platform.architecture()[0]}",
        f"Operating System: {platform.system()} {platform.release()}",
        f"Platform ID: {platform.platform()}",
        f"Machine: {platform.machine()}",
        f"Processor: {platform.processor()}"
    ]
    for line in info:
        logging.info(line)


class Operation:
    def __init__(self):
        self.rm = None
        self.tsl = None
        self.tsl_functions = None

    @staticmethod
    def show_error_message(message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def connect_tsl(self):
        ip_address = ui.IP_Address_input.text()
        port_number = ui.Port_Number_input.text()
        subnet = ui.Subnet_Mask_input.text()
        gateway = ui.Default_Gateway_input.text()

        logging.info("Starting TSL connection process.")

        try:
            self.rm = visa.ResourceManager()
            logging.info("ResourceManager created.")

            lan_resource = f'TCPIP::{ip_address}::{port_number}::SOCKET'
            logging.info(f"LAN resource: {lan_resource}")

            self.tsl = self.rm.open_resource(lan_resource, read_termination="\r")
            logging.info(f"Opened resource: {lan_resource}")

            # Additional check for successful connection
            if self.tsl is not None:
                logging.info("Successfully connected to TSL.")
            else:
                logging.error("TSL connection failed: Resource is None.")
                return

        except visa.VisaIOError as e:
            logging.error(f"VisaIOError during TSL connection: {e}")
            self.show_error_message("Failed to connect to the TSL device. Please check the settings.")
        except RuntimeError as e:
            logging.error(f"Runtime error during TSL connection: {e}")
            self.show_error_message("An unexpected runtime error occurred.")
        except Exception as e:
            logging.error(f"Unexpected error during TSL operation: {e}")
            self.show_error_message("An unexpected error occurred.")

        # Proceed with further operations if the connection is successful
        if self.tsl:
            try:
                logging.info("Getting TSL IDN")
                IDN = self.tsl.query("*IDN?")
                logging.info(f"TSL IDN: {IDN}")
                info = IDN.split(",")
                ui.ProdName_disp.setText(str(info[1]))
                ui.SN_disp.setText(str(info[2]))
                ui.Firmware_disp.setText(str(info[3]))
                logging.info(f"Device Info - ProdName: {info[1]}, SN: {info[2]}, Firmware: {info[3]}")

                self.update_subnet_mask(subnet)
                self.update_default_gateway(gateway)
                logging.info(f"Updated subnet mask to {subnet} and default gateway to {gateway}.")

                self.tsl_functions = functions.TSLFunctions(self.tsl, logging)
                self.tsl_functions.ini(IDN)
                logging.info("TSL functions initialized.")

                time.sleep(0.5)
                self.get_lambda()
                self.get_pwr()
                self.get_att()
                logging.info("Completed getting lambda, power, and attenuation.")

            except Exception as e:
                logging.error(f"Error during TSL operations after connection: {e}")
                self.show_error_message("An error occurred during TSL operations.")

    def update_subnet_mask(self, subnet):
        try:
            time.sleep(0.5)
            self.tsl.write(f":SYST:COMM:ETH:SMAS {subnet}")
            logging.info(f"Subnet mask updated to {subnet}.")
        except Exception as e:
            logging.error(f"Error updating subnet mask: {e}")
            self.show_error_message("Failed to update subnet mask.")

    def update_default_gateway(self, gateway):
        try:
            time.sleep(0.5)
            self.tsl.write(f":SYST:COMM:ETH:DGAT {gateway}")
            logging.info(f"Default gateway updated to {gateway}.")
        except Exception as e:
            logging.error(f"Error updating default gateway: {e}")
            self.show_error_message("Failed to update default gateway.")

    def ld_on(self):
        try:
            time.sleep(0.5)
            self.tsl.write("POW:STAT 1")
            logging.info("Laser device turned on.")
        except Exception as e:
            logging.error(f"Error turning on laser device: {e}")
            self.show_error_message("Failed to turn on the laser device.")

    def ld_off(self):
        try:
            time.sleep(0.5)
            self.tsl.write("POW:STAT 0")
            logging.info("Laser device turned off.")
        except Exception as e:
            logging.error(f"Error turning off laser device: {e}")
            self.show_error_message("Failed to turn off the laser device.")

    def pwr_auto(self):
        try:
            time.sleep(0.5)
            self.tsl.write('POW:ATT:AUT 1')
            logging.info("Power set to automatic mode.")
        except Exception as e:
            logging.error(f"Error setting power to automatic mode: {e}")
            self.show_error_message("Failed to set power to automatic mode.")

    def pwr_man(self):
        try:
            time.sleep(0.5)
            self.tsl.write('POW:ATT:AUT 0')
            logging.info("Power set to manual mode.")
        except Exception as e:
            logging.error(f"Error setting power to manual mode: {e}")
            self.show_error_message("Failed to set power to manual mode.")

    def shut_op(self):
        try:
            time.sleep(0.5)
            self.tsl.write('POW:SHUT 0')
            time.sleep(0.1)
            self.get_pwr()
            self.get_att()
            logging.info("Output shut off.")
        except Exception as e:
            logging.error(f"Error shutting output off: {e}")
            self.show_error_message("Failed to shut off output.")

    def shut_close(self):
        try:
            time.sleep(0.5)
            self.tsl.write('POW:SHUT 1')
            time.sleep(0.1)
            self.get_pwr()
            self.get_att()
            logging.info("Output shut closed.")
        except Exception as e:
            logging.error(f"Error closing output shut: {e}")
            self.show_error_message("Failed to close output shut.")

    def set_lambda(self):
        try:
            time.sleep(0.5)
            WriteLambda = round(float(ui.lambda_input.text()), 4)
            self.tsl_functions.set_wl(WriteLambda)
            time.sleep(0.1)
            self.get_lambda()
            self.get_pwr()
            self.get_att()
            logging.info(f"Wavelength set to {WriteLambda}.")
        except Exception as e:
            logging.error(f"Error setting wavelength: {e}")
            self.show_error_message("Failed to set wavelength.")

    def get_lambda(self):
        try:
            time.sleep(0.5)
            ui.lambda_disp.setText(self.tsl_functions.get_wl())
            logging.info("Wavelength retrieved successfully.")
        except Exception as e:
            logging.error(f"Error getting wavelength: {e}")
            self.show_error_message("Failed to retrieve wavelength.")

    def set_pwr(self):
        try:
            time.sleep(0.5)
            WritePwr = round(float(ui.Pwr_input.text()), 2)
            self.tsl_functions.set_pwr(WritePwr)
            time.sleep(0.1)
            self.get_pwr()
            self.get_att()
            logging.info(f"Power set to {WritePwr} dBm.")
        except Exception as e:
            logging.error(f"Error setting power: {e}")
            self.show_error_message("Failed to set power.")

    def get_pwr(self):
        try:
            time.sleep(0.5)
            ui.Pwr_disp.setText(self.tsl_functions.get_pwr())
            logging.info("Power retrieved successfully.")
        except Exception as e:
            logging.error(f"Error getting power: {e}")
            self.show_error_message("Failed to retrieve power.")

    def set_att(self):
        try:
            time.sleep(0.5)
            WriteAtt = round(float(ui.Att_input.text()), 2)
            self.tsl_functions.set_att(WriteAtt)
            time.sleep(0.1)
            self.get_pwr()
            self.get_att()
            logging.info(f"Attenuation set to {WriteAtt} dB.")
        except Exception as e:
            logging.error(f"Error setting attenuation: {e}")
            self.show_error_message("Failed to set attenuation.")

    def get_att(self):
        try:
            time.sleep(0.5)
            ui.Att_disp.setText(self.tsl_functions.get_att())
            logging.info("Attenuation retrieved successfully.")
        except Exception as e:
            logging.error(f"Error getting attenuation: {e}")
            self.show_error_message("Failed to retrieve attenuation.")

    @staticmethod
    def get_data():
        time.sleep(0.5)
        WL_start = ui.lambdaStart_input.text()
        WL_end = ui.lambdaEnd_input.text()
        Swp_mod = ui.Swp_mod_input.currentIndex()
        if Swp_mod == 1 or Swp_mod == 3:
            Arg1 = ui.ScanSpeed_input.text()
            Arg2 = ui.TriggStep_input.text()
            if ui.Swp_mod_input.currentIndexChanged:
                ui.frame_5.hide()
                ui.frame_4.show()
        else:
            Arg1 = ui.Step_input.text()
            Arg2 = ui.Dwell_input.text()
            ui.frame_5.show()
            ui.frame_4.hide()
        Cycle = ui.Repeat_input.text()
        return Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle

    def auto_start(self):
        try:
            time.sleep(0.5)
            Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle = self.get_data()
            self.tsl_functions.auto_start(Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle)
            logging.info("Auto start initiated.")
        except Exception as e:
            logging.error(f"Error in auto start: {e}")
            self.show_error_message("Failed to initiate auto start.")

    def trig_start(self):
        try:
            time.sleep(0.5)
            Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle = self.get_data()
            self.tsl_functions.trig_start(Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle)
            logging.info("Trigger start initiated.")
        except Exception as e:
            logging.error(f"Error in trigger start: {e}")
            self.show_error_message("Failed to initiate trigger start.")

    def del_change(self):
        try:
            time.sleep(0.5)
            self.tsl_functions.del_change(ui.GPIB_DEL_input.currentIndex())
            logging.info("GPIB delimiter changed.")
        except Exception as e:
            logging.error(f"Error changing GPIB delimiter: {e}")
            self.show_error_message("Failed to change GPIB delimiter.")

    def cc_off(self):
        try:
            time.sleep(0.5)
            self.tsl.write('COHC 0')
            logging.info("Coherence control turned off.")
        except Exception as e:
            logging.error(f"Error turning off coherence control: {e}")
            self.show_error_message("Failed to turn off coherence control.")

    def cc_on(self):
        try:
            time.sleep(0.5)
            self.tsl.write('COHC 1')
            logging.info("Coherence control turned on.")
        except Exception as e:
            logging.error(f"Error turning on coherence control: {e}")
            self.show_error_message("Failed to turn on coherence control.")

    def am_on(self):
        try:
            time.sleep(0.5)
            self.tsl.write('AM:STATE 1')
            logging.info("Amplitude modulation turned on.")
        except Exception as e:
            logging.error(f"Error turning on amplitude modulation: {e}")
            self.show_error_message("Failed to turn on amplitude modulation.")

    def am_off(self):
        try:
            time.sleep(0.5)
            self.tsl.write('AM:STATE 0')
            logging.info("Amplitude modulation turned off.")
        except Exception as e:
            logging.error(f"Error turning off amplitude modulation: {e}")
            self.show_error_message("Failed to turn off amplitude modulation.")

    def trig_src(self):
        try:
            time.sleep(0.5)
            self.tsl_functions.trig_src(ui.TrigSrc_input.currentIndex())
            logging.info("Trigger source set.")
        except Exception as e:
            logging.error(f"Error setting trigger source: {e}")
            self.show_error_message("Failed to set trigger source.")

    def trig_mode(self):
        try:
            time.sleep(0.5)
            self.tsl_functions.trig_mode(ui.TrigMode_input.currentIndex())
            logging.info("Trigger mode set.")
        except Exception as e:
            logging.error(f"Error setting trigger mode: {e}")
            self.show_error_message("Failed to set trigger mode.")

    def stop(self):
        try:
            time.sleep(0.5)
            self.tsl.write('WAV:SWE 0')
            logging.info("Wave sweep stopped.")
        except Exception as e:
            logging.error(f"Error stopping wave sweep: {e}")
            self.show_error_message("Failed to stop wave sweep.")


ui.Att_input.hide()
ui.Att_go.hide()
ui.frame_4.hide()
ui.frame_5.hide()


def field_select():
    if ui.Swp_mod_input.currentIndex() == 1 or ui.Swp_mod_input.currentIndex() == 3:
        ui.frame_5.hide()
        ui.frame_4.show()
    else:
        ui.frame_5.show()
        ui.frame_4.hide()


log_run_info()

operations = Operation()

ui.Connect.clicked.connect(operations.connect_tsl)
ui.LD_ON.clicked.connect(operations.ld_on)  # Switch ON LD
ui.LD_OFF.clicked.connect(operations.ld_off)  # Switch OFF LD
ui.Pwr_auto.clicked.connect(operations.pwr_auto)  # Switch to Auto Pwr
ui.Pwr_manual.clicked.connect(operations.pwr_man)  # Switch to Manual Pwr
ui.shut_open.clicked.connect(operations.shut_op)  # Open Shutter
ui.shut_close.clicked.connect(operations.shut_close)  # Close the Shutter
ui.lambda_go.clicked.connect(operations.set_lambda)  # Set Wavelength
ui.lambda_input.editingFinished.connect(operations.set_lambda)  # Set Wavelength
ui.lambda_get.clicked.connect(operations.get_lambda)  # Read Wavelength
ui.Pwr_input.editingFinished.connect(operations.set_pwr)  # Set Pwr
ui.Pwr_go.clicked.connect(operations.set_pwr)  # Set Pwr
ui.Pwr_get.clicked.connect(operations.get_pwr)  # Read Pwr
ui.Att_input.editingFinished.connect(operations.set_att)  # Set Attenuation
ui.Att_go.clicked.connect(operations.set_att)  # Set Attenuation
ui.Att_get.clicked.connect(operations.get_att)  # Read Attenuation
ui.Start.clicked.connect(operations.auto_start)  # Start scanning
ui.SoftTrig.clicked.connect(operations.trig_start)  # Start scanning with soft trigger
ui.Swp_mod_input.currentIndexChanged.connect(field_select)  # Change selectable fields depending on sweep mode
ui.Swp_mode_go.clicked.connect(field_select)  # Change selectable fields depending on sweep mode
ui.Del_go.clicked.connect(operations.del_change)  # Change GPIB delimiter
ui.CC_OFF.clicked.connect(operations.cc_off)  # Switch off Coherence Control
ui.CC_ON.clicked.connect(operations.cc_on)  # Switch on Coherence Control
ui.Amp_Mod_ON.clicked.connect(operations.am_on)  # Switch on Amplitude Modulation
ui.Amp_Mod_OFF.clicked.connect(operations.am_off)  # Switch off Amplitude Modulation
ui.TrigSrc_go.clicked.connect(operations.trig_src)  # Change Trigger Input Source
ui.TrigMode_go.clicked.connect(operations.trig_mode)  # Change Trigger Output Mode
ui.Stop.clicked.connect(operations.stop)  # Stop scan (only works on soft trigger scanning mode)
# ui.ScanSpeed_input.textChanged.connect(Trig_tip)    # Calculate min and max trigger step
# ui.lambdaStart_input.textChanged.connect(Trig_tip)  # Calculate min and max trigger step
# ui.lambdaEnd_input.textChanged.connect(Trig_tip)   # Calculate min and max trigger step
TSL_Control_Tool.show()
sys.exit(app.exec_())
