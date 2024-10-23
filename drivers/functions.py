# -*- coding: utf-8 -*-

import time


Ini_Cond = {
    'POW:STAT ': '1', 'POW:SHUT ': '0', 'POW:ATT:AUT ': '1', 'POW:UNIT ': '0', 'WAV:UNIT ': '0',
    'TRIG:INP:EXT ': '0', 'TRIG:OUTP ': '3', 'WAV:SWE:MOD ': '1',
    'SYST:COMM:GPIB:DEL ': '2', 'COHC ': '0', 'AM:STAT ': '0'
}
Use_Cond = {
    'POW:STAT ': '', 'POW:SHUT ': '', 'POW:ATT:AUT ': '', 'POW:UNIT ': '', 'WAV:UNIT ': '',
    'TRIG:INP:EXT ': '', 'TRIG:OUTP ': '', 'WAV:SWE:MOD ': '',
    'SYST:COMM:GPIB:DEL ': '', 'COHC ': '', 'AM:STAT ': ''
}


class TSLFunctions:
    def __init__(self, tsl_instrument):
        self.tsl = tsl_instrument

    def ini(self, idn):
        time.sleep(0.2)
        self.tsl.write('*CLS')
        self.tsl.write('*RST')
        for i, j in zip(Ini_Cond.keys(), Ini_Cond.values()):
            self.tsl.write(i + j)
        time.sleep(0.5)
        if '550' in idn or '710' in idn:
            self.tsl.write('GC 1')
        else:
            self.tsl.write('SYST:COMM:COD 0')

    def set_wl(self, WL):
        self.tsl.write(f'WAV {WL}')
        time.sleep(0.2)
        while True:
            check = self.tsl.query("*OPC?")
            if check == '0':
                time.sleep(0.1)
            else:
                self.get_wl()
                break

    def get_wl(self):
        time.sleep(0.2)
        return self.tsl.query('WAV?')

    def set_pwr(self, Pwr):
        time.sleep(0.2)
        if Pwr > 13:
            Pwr = 13
        elif Pwr < -14:
            Pwr = -14
        self.tsl.write(f'POW {Pwr}')

        while True:
            check = self.tsl.query("*opc?")
            if check == '0':
                time.sleep(0.1)
            else:
                self.get_pwr()
                break

    def get_pwr(self):
        time.sleep(0.2)
        return self.tsl.query('POW:ACT?')

    def set_att(self, Att):
        time.sleep(0.2)
        if Att > 30:
            Att = 30
        elif Att < 0:
            Att = 0
        self.tsl.write(f'POW:ATT {Att}')
        while True:
            check = self.tsl.query("*opc?")
            if check == '0':
                time.sleep(0.1)
            else:
                self.get_att()
                self.get_pwr()
                break

    def get_att(self):
        time.sleep(0.2)
        return self.tsl.query('POW:ATT?')

    def auto_start(self, Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle):
        time.sleep(0.2)
        self.tsl.write('TRIG:INP:STAN 0')
        self.scan(Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle)

    def trig_start(self, Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle):
        time.sleep(0.2)
        self.tsl.write('TRIG:INP:STAN 1')
        self.scan(Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle)

    def scan(self, Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle):
        time.sleep(0.2)
        self.tsl.write(f'WAV:SWE:MOD {Swp_mod}')
        self.tsl.write(f'WAV:SWE:STAR {WL_start}')
        self.tsl.write(f'WAV:SWE:STOP {WL_end}')
        if str(Cycle) != '':
            self.tsl.write('WAV:SWE:REP')
            self.tsl.write(f'WAV:SWE:CYCL {Cycle}')

        if Swp_mod == 1 or Swp_mod == 3:  # if Continuous scan modes (one way or two ways) are selected,
            # Arg1 and Arg2 = Scan speed, trigger output step
            self.tsl.write(f'WAV:SWE:SPE {Arg1}')
            self.tsl.write(f'TRIG:OUTP:STEP {Arg2}')
            self.tsl.write('WAV:SWE:STAT 1')
            check = self.tsl.query('WAV:SWE?')
            time.sleep(0.2)
            while True:
                if check != '3':
                    check = self.tsl.query('WAV:SWE?')
                    time.sleep(0.1)
                else:
                    self.tsl.write('WAV:SWE:SOFT')
                    break
                break
        elif Swp_mod == 0 or Swp_mod == 2:
            time.sleep(0.2)
            self.tsl.write(f'WAV:SWE:STEP {Arg1}')
            self.tsl.write(f'WAV:SWE:DWEL {Arg2}')
            self.tsl.write('WAV:SWE:STAT 1')
            check = self.tsl.query('WAV:SWE?')
            while True:
                if check != '3':
                    check = self.tsl.query('WAV:SWE?')
                    time.sleep(0.1)
                else:
                    self.tsl.write('WAV:SWE:SOFT')
                    break
                break

    def del_change(self, delimiter):
        time.sleep(0.2)
        self.tsl.write(f'SYST:COMM:GPIB:DEL {delimiter}')

    def trig_src(self, trigg):
        time.sleep(0.2)
        self.tsl.write(f'TRIG:INP:EXT {trigg}')

    def trig_mode(self, Mode):
        time.sleep(0.2)
        self.tsl.write(f'TRIG:OUTP {Mode}')