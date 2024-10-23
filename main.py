# -*- coding: utf-8 -*-

import sys
import time
import pyvisa as visa
from PyQt5 import QtCore, QtWidgets, QtGui
from drivers import functions, TSL_Control_Tool_GUI

app = QtCore.QCoreApplication.instance()
if app is None:
    app = QtWidgets.QApplication(sys.argv)
TSL_Control_Tool = QtWidgets.QMainWindow()
app.setStyle('Fusion')
ui = TSL_Control_Tool_GUI.UiTslControlTool()
ui.setupUi(TSL_Control_Tool)

icon = QtGui.QIcon()
icon.addPixmap(QtGui.QPixmap("utils/santec_logo_small.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
TSL_Control_Tool.setWindowIcon(icon)


class Operation:
    def __init__(self):
        self.rm = None
        self.tsl = None
        self.tsl_functions = None

    def update_subnet_mask(self, subnet):
        time.sleep(1)
        self.tsl.write(f":SYST:COMM:ETH:SMAS {subnet}")

    def update_default_gateway(self, gateway):
        time.sleep(1)
        self.tsl.write(f":SYST:COMM:ETH:DGAT {gateway}")

    def ld_on(self):
        time.sleep(1)
        self.tsl.write("POW:STAT 1")

    def ld_off(self):
        time.sleep(1)
        self.tsl.write("POW:STAT 0")

    def pwr_auto(self):
        time.sleep(1)
        self.tsl.write('POW:ATT:AUT 1')

    def pwr_man(self):
        time.sleep(1)
        self.tsl.write('POW:ATT:AUT 0')

    def shut_op(self):
        time.sleep(1)
        self.tsl.write('POW:SHUT 0')
        time.sleep(0.1)
        self.get_pwr()
        self.get_att()

    def shut_close(self):
        time.sleep(1)
        self.tsl.write('POW:SHUT 1')
        time.sleep(0.1)
        self.get_pwr()
        self.get_att()

    def set_lambda(self):
        time.sleep(1)
        WriteLambda = round(float(ui.lambda_input.text()), 4)
        self.tsl_functions.set_wl(WriteLambda)
        time.sleep(0.1)
        self.get_lambda()
        self.get_pwr()
        self.get_att()

    def get_lambda(self):
        time.sleep(1)
        ui.lambda_disp.setText(self.tsl_functions.get_wl())

    def set_pwr(self):
        time.sleep(1)
        WritePwr = round(float(ui.Pwr_input.text()), 2)
        self.tsl_functions.set_pwr(WritePwr)
        time.sleep(0.1)
        self.get_pwr()
        self.get_att()

    def get_pwr(self):
        time.sleep(1)
        ui.Pwr_disp.setText(self.tsl_functions.get_pwr())

    def set_att(self):
        time.sleep(1)
        WriteAtt = round(float(ui.Att_input.text()), 2)
        self.tsl_functions.set_att(WriteAtt)
        time.sleep(0.1)
        self.get_pwr()
        self.get_att()

    def get_att(self):
        time.sleep(1)
        ui.Att_disp.setText(self.tsl_functions.get_att())

    @staticmethod
    def get_data():
        time.sleep(1)
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
        time.sleep(1)
        Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle = self.get_data()
        self.tsl_functions.auto_start(Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle)

    def trig_start(self):
        time.sleep(1)
        Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle = self.get_data()
        self.tsl_functions.trig_start(Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle)

    def del_change(self):
        time.sleep(1)
        self.tsl_functions.del_change(ui.GPIB_DEL_input.currentIndex())

    def cc_off(self):
        time.sleep(1)
        self.tsl.write('COHC 0')

    def cc_on(self):
        time.sleep(1)
        self.tsl.write('COHC 1')

    def am_on(self):
        time.sleep(1)
        self.tsl.write('AM:STATE 1')

    def am_off(self):
        time.sleep(1)
        self.tsl.write('AM:STATE 0')

    def trig_src(self):
        time.sleep(1)
        self.tsl_functions.trig_src(ui.TrigSrc_input.currentIndex())

    def trig_mode(self):
        time.sleep(1)
        self.tsl_functions.trig_mode(ui.TrigMode_input.currentIndex())

    def stop(self):
        time.sleep(1)
        self.tsl.write('WAV:SWE 0')

    def connect_tsl(self):
        time.sleep(1)
        self.rm = visa.ResourceManager()

        ip_address = ui.IP_Address_input.text()
        port_number = ui.Port_Number_input.text()
        subnet = ui.Subnet_Mask_input.text()
        gateway = ui.Default_Gateway_input.text()

        lan_resource = 'TCPIP::' + ip_address + '::' + port_number + '::SOCKET'
        self.tsl = self.rm.open_resource(lan_resource, read_termination="\r")
        # self.tsl.timeout = 3000

        IDN = self.tsl.query("*IDN?")
        info = IDN.split(",")
        ui.ProdName_disp.setText(str(info[1]))
        ui.SN_disp.setText(str(info[2]))
        ui.Firmware_disp.setText(str(info[3]))
        # return self.tsl

        self.update_subnet_mask(subnet)
        self.update_default_gateway(gateway)

        self.tsl_functions = functions.TSLFunctions(self.tsl)
        self.tsl_functions.ini(IDN)

        time.sleep(0.5)
        self.get_lambda()
        self.get_pwr()
        self.get_att()


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
