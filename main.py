# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtWidgets, QtGui
import pyvisa as visa
import time
from drivers import functions, TSL_Control_Tool_GUI

global TSL


# FUNCTIONS DEFINITIONS

def ld_on():
    TSL.write("POW:STAT 1")


def ld_off():
    TSL.write("POW:STAT 0")


def pwr_auto():
    TSL.write('POW:ATT:AUT 1')


def pwr_man():
    TSL.write('POW:ATT:AUT 0')


def shut_op():
    TSL.write('POW:SHUT 0')
    time.sleep(0.1)
    get_pwr()
    get_att()


def shut_close():
    TSL.write('POW:SHUT 1')
    time.sleep(0.1)
    get_pwr()
    get_att()


def set_lambda():
    WriteLambda = round(float(ui.lambda_input.text()), 4)
    functions.SetWL(WriteLambda)
    time.sleep(0.1)
    get_lambda()
    get_pwr()
    get_att()


def get_lambda():
    ui.lambda_disp.setText(functions.GetWL())


def set_pwr():
    WritePwr = round(float(ui.Pwr_input.text()), 2)
    functions.SetPwr(WritePwr)
    time.sleep(0.1)
    get_pwr()
    get_att()


def get_pwr():
    ui.Pwr_disp.setText(functions.GetPwr())


def set_att():
    WriteAtt = round(float(ui.Att_input.text()), 2)
    functions.SetAtt(WriteAtt)
    time.sleep(0.1)
    get_pwr()
    get_att()


def get_att():
    ui.Att_disp.setText(functions.GetAtt())


def get_data():
    WLstart = ui.lambdaStart_input.text()
    WLend = ui.lambdaEnd_input.text()
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
    return Swp_mod, WLstart, WLend, Arg1, Arg2, Cycle


def auto_start():
    Swp_mod, WLstart, WLend, Arg1, Arg2, Cycle = get_data()
    functions.Auto_Start(Swp_mod, WLstart, WLend, Arg1, Arg2, Cycle)


def trig_start():
    Swp_mod, WLstart, WLend, Arg1, Arg2, Cycle = get_data()
    functions.Trig_Start(Swp_mod, WLstart, WLend, Arg1, Arg2, Cycle)


def del_change():
    functions.Del_change(ui.GPIB_DEL_input.currentIndex())


def cc_off():
    TSL.write('COHC 0')


def cc_on():
    TSL.write('COHC 1')


def am_on():
    TSL.write('AM:STATE 1')


def am_off():
    TSL.write('AM:STATE 0')


def trig_src():
    functions.TrigSrc(ui.TrigSrc_input.currentIndex())


def trig_mode():
    functions.TrigMode(ui.TrigMode_input.currentIndex())


def stop():
    TSL.write('WAV:SWE 0')


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


def connect():
    global TSL
    rm = visa.ResourceManager()
    listing = rm.list_resources()
    tools = [i for i in listing if 'GPIB' in i]
    for i in tools:
        buffer = rm.open_resource(i, read_termination='\r\n')
        if 'TSL' in buffer.query('*IDN?'):
            TSL = buffer

    IDN = TSL.query("*IDN?")
    info = IDN.split(",")
    ui.ProdName_disp.setText(str(info[1]))
    ui.SN_disp.setText(str(info[2]))
    ui.Firmware_disp.setText(str(info[3]))
    # return TSL

    functions.Ini()
    time.sleep(0.5)
    get_lambda()
    get_pwr()
    get_att()


ui.Att_input.hide()
ui.Att_go.hide()
ui.frame_5.hide()


def Field_select():
    if ui.Swp_mod_input.currentIndex() == 1 or ui.Swp_mod_input.currentIndex() == 3:
        ui.frame_5.hide()
        ui.frame_4.show()
    else:
        ui.frame_5.show()
        ui.frame_4.hide()


# if '550' in info[1]:
#         ui.TriggStep_input.setToolTip(str(float(TSL.query('WAV:SWE:SPE?'))/1000)+'nm ~ '+str(float(TSL.query('WAV:SWE:STOP?'))-float(TSL.query('WAV:SWE:STAR?')))+'nm')
# elif '710' in info[1]:
#     ui.TriggStep_input.setToolTip(str(float(TSL.query('WAV:SWE:SPE?'))/5000)+'nm ~ '+str(float(TSL.query('WAV:SWE:STOP?'))-float(TSL.query('WAV:SWE:STAR?')))+'nm')

# def Trig_tip():
#     try:
#         if '550' in info[1]:
#             ui.TriggStep_input.setToolTip(str(float(ui.ScanSpeed_input.text())/1000)+'nm ~ '+str(float(ui.lambdaEnd_input.text())-float(ui.lambdaStart_input.text()))+'nm')
#         elif '710' in info[1]:
#             ui.TriggStep_input.setToolTip(str(float(ui.ScanSpeed_input.text())/5000)+'nm ~ '+str(float(ui.lambdaEnd_input.text())-float(ui.lambdaStart_input.text()))+'nm')
#     except ValueError:
#         try:
#             if ui.ScanSpeed_input.text()=='':
#                 if '550' in info[1]:
#                     ui.TriggStep_input.setToolTip(str(float(TSL.query('WAV:SWE:SPE?'))/1000)+'nm ~ '+str(float(ui.lambdaEnd_input.text())-float(ui.lambdaStart_input.text()))+'nm')
#                 elif '710' in info[1]:
#                     ui.TriggStep_input.setToolTip(str(float(TSL.query('WAV:SWE:SPE?'))/5000)+'nm ~ '+str(float(ui.lambdaEnd_input.text())-float(ui.lambdaStart_input.text()))+'nm')
#         except ValueError:
#             try:
#                 if ui.lambdaEnd_input.text()=='':
#                     if '550' in info[1]:
#                         ui.TriggStep_input.setToolTip(str(float(ui.ScanSpeed_input.text())/1000)+'nm ~ '+str(float(TSL.query('WAV:SWE:STOP?'))-float(ui.lambdaStart_input.text()))+'nm')
#                     elif '710' in info[1]:
#                         ui.TriggStep_input.setToolTip(str(float(ui.ScanSpeed_input.text())/5000)+'nm ~ '+str(float(TSL.query('WAV:SWE:STOP?'))-float(ui.lambdaStart_input.text()))+'nm')
#             except ValueError:
#                 try:
#                     if ui.lambdaStart_input.text()=='':
#                         if '550' in info[1]:
#                             ui.TriggStep_input.setToolTip(str(float(ui.ScanSpeed_input.text())/1000)+'nm ~ '+str(float(ui.lambdaEnd_input.text())-float(TSL.query('WAV:SWE:STAR?')))+'nm')
#                         elif '710' in info[1]:
#                             ui.TriggStep_input.setToolTip(str(float(ui.ScanSpeed_input.text())/5000)+'nm ~ '+str(float(ui.lambdaEnd_input.text())-float(TSL.query('WAV:SWE:STAR?')))+'nm')
#                 except ValueError:
#                     if '550' in info[1]:
#                             ui.TriggStep_input.setToolTip(str(float(TSL.query('WAV:SWE:SPE?'))/1000)+'nm ~ '+str(float(TSL.query('WAV:SWE:STOP?'))-float(TSL.query('WAV:SWE:STAR?')))+'nm')
#                     elif '710' in info[1]:
#                         ui.TriggStep_input.setToolTip(str(float(TSL.query('WAV:SWE:SPE?'))/5000)+'nm ~ '+str(float(TSL.query('WAV:SWE:STOP?'))-float(TSL.query('WAV:SWE:STAR?')))+'nm')

ui.Connect.clicked.connect(connect)
ui.LD_ON.clicked.connect(ld_on)  # Switch ON LD
ui.LD_OFF.clicked.connect(ld_off)  # Switch OFF LD
ui.Pwr_auto.clicked.connect(pwr_auto)  # Switch to Auto Pwr
ui.Pwr_manual.clicked.connect(pwr_man)  # Switch to Manual Pwr
ui.shut_open.clicked.connect(shut_op)  # Open Shutter
ui.shut_close.clicked.connect(shut_close)  # Close the Shutter
ui.lambda_go.clicked.connect(set_lambda)  # Set Wavelength
ui.lambda_input.editingFinished.connect(set_lambda)  # Set Wavelength
ui.lambda_get.clicked.connect(get_lambda)  # Read Wavelength
ui.Pwr_input.editingFinished.connect(set_pwr)  # Set Pwr
ui.Pwr_go.clicked.connect(set_pwr)  # Set Pwr
ui.Pwr_get.clicked.connect(get_pwr)  # Read Pwr
ui.Att_input.editingFinished.connect(set_att)  # Set Attenuation
ui.Att_go.clicked.connect(set_att)  # Set Attenuation
ui.Att_get.clicked.connect(get_att)  # Read Attenuation
ui.Start.clicked.connect(auto_start)  # Start scanning
ui.SoftTrig.clicked.connect(trig_start)  # Start scanning with soft trigger
ui.Swp_mod_input.currentIndexChanged.connect(Field_select)  # Change selectable fieds depending on sweep mode
ui.Swp_mode_go.clicked.connect(Field_select)  # Change selectable fieds depending on sweep mode
ui.Del_go.clicked.connect(del_change)  # Change GPIB delimiter
ui.CC_OFF.clicked.connect(cc_off)  # Switch off Coherence Contorl
ui.CC_ON.clicked.connect(cc_on)  # Switch on Coherence Control
ui.Amp_Mod_ON.clicked.connect(am_on)  # Switch on Amplitude Modulation
ui.Amp_Mod_OFF.clicked.connect(am_off)  # Switch off Amplitude Modulation
ui.TrigSrc_go.clicked.connect(trig_src)  # Change Trigger Input Source
ui.TrigMode_go.clicked.connect(trig_mode)  # Change Trigger Output Mode
ui.Stop.clicked.connect(stop)  # Stop scan (only works on soft trigger scanning mode)
# ui.ScanSpeed_input.textChanged.connect(Trig_tip)                                #Calculate min and max trigger step
# ui.lambdaStart_input.textChanged.connect(Trig_tip)                              #Calculate min and max trigger step
# ui.lambdaEnd_input.textChanged.connect(Trig_tip)                                #Calculate min and max trigger step
TSL_Control_Tool.show()
sys.exit(app.exec_())
