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
    def __init__(self, tsl_instrument, logger):
        self.tsl = tsl_instrument
        self.logger = logger

    def ini(self, idn):
        try:
            time.sleep(0.5)
            self.tsl.write('*CLS')
            self.tsl.write('*RST')
            for i, j in zip(Ini_Cond.keys(), Ini_Cond.values()):
                self.tsl.write(i + j)
            time.sleep(0.5)
            if '550' in idn or '710' in idn:
                self.tsl.write('GC 1')
            else:
                self.tsl.write('SYST:COMM:COD 0')
            self.logger.info("Initialization completed successfully.")
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")

    def set_wl(self, WL):
        try:
            self.tsl.write(f'WAV {WL}')
            time.sleep(0.5)
            while True:
                check = self.tsl.query("*OPC?")
                if check == '0':
                    time.sleep(0.1)
                else:
                    self.get_wl()
                    self.logger.info(f"Wavelength set to {WL}.")
                    break
        except Exception as e:
            self.logger.error(f"Error setting wavelength: {e}")

    def get_wl(self):
        try:
            time.sleep(0.5)
            return self.tsl.query('WAV?')
        except Exception as e:
            self.logger.error(f"Error getting wavelength: {e}")

    def set_pwr(self, Pwr):
        try:
            time.sleep(0.5)
            Pwr = max(min(Pwr, 13), -14)  # Clamp power value
            self.tsl.write(f'POW {Pwr}')
            while True:
                check = self.tsl.query("*opc?")
                if check == '0':
                    time.sleep(0.1)
                else:
                    self.get_pwr()
                    self.logger.info(f"Power set to {Pwr} dBm.")
                    break
        except Exception as e:
            self.logger.error(f"Error setting power: {e}")

    def get_pwr(self):
        try:
            time.sleep(0.5)
            return self.tsl.query('POW:ACT?')
        except Exception as e:
            self.logger.error(f"Error getting power: {e}")

    def set_att(self, Att):
        try:
            time.sleep(0.5)
            Att = max(min(Att, 30), 0)  # Clamp attenuation value
            self.tsl.write(f'POW:ATT {Att}')
            while True:
                check = self.tsl.query("*opc?")
                if check == '0':
                    time.sleep(0.1)
                else:
                    self.get_att()
                    self.get_pwr()
                    self.logger.info(f"Attenuation set to {Att} dB.")
                    break
        except Exception as e:
            self.logger.error(f"Error setting attenuation: {e}")

    def get_att(self):
        try:
            time.sleep(0.5)
            return self.tsl.query('POW:ATT?')
        except Exception as e:
            self.logger.error(f"Error getting attenuation: {e}")

    def auto_start(self, Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle):
        try:
            time.sleep(0.5)
            self.tsl.write('TRIG:INP:STAN 0')
            self.scan(Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle)
            self.logger.info("Auto-start initiated.")
        except Exception as e:
            self.logger.error(f"Error in auto start: {e}")

    def trig_start(self, Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle):
        try:
            time.sleep(0.5)
            self.tsl.write('TRIG:INP:STAN 1')
            self.scan(Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle)
            self.logger.info("Trigger start initiated.")
        except Exception as e:
            self.logger.error(f"Error in trigger start: {e}")

    def scan(self, Swp_mod, WL_start, WL_end, Arg1, Arg2, Cycle):
        try:
            time.sleep(0.5)
            self.tsl.write(f'WAV:SWE:MOD {Swp_mod}')
            self.tsl.write(f'WAV:SWE:STAR {WL_start}')
            self.tsl.write(f'WAV:SWE:STOP {WL_end}')
            if str(Cycle) != '':
                self.tsl.write('WAV:SWE:REP')
                self.tsl.write(f'WAV:SWE:CYCL {Cycle}')

            # Check for continuous or step scan modes
            if Swp_mod in [1, 3]:
                self.tsl.write(f'WAV:SWE:SPE {Arg1}')
                self.tsl.write(f'TRIG:OUTP:STEP {Arg2}')
                self.tsl.write('WAV:SWE:STAT 1')
                self.wait_for_scan_completion()
            elif Swp_mod in [0, 2]:
                time.sleep(0.5)
                self.tsl.write(f'WAV:SWE:STEP {Arg1}')
                self.tsl.write(f'WAV:SWE:DWEL {Arg2}')
                self.tsl.write('WAV:SWE:STAT 1')
                self.wait_for_scan_completion()

            self.logger.info("Scan initiated successfully.")
        except Exception as e:
            self.logger.error(f"Error in scan: {e}")

    def wait_for_scan_completion(self):
        check = self.tsl.query('WAV:SWE?')
        while True:
            if check != '3':
                check = self.tsl.query('WAV:SWE?')
                time.sleep(0.1)
            else:
                self.tsl.write('WAV:SWE:SOFT')
                break

    def del_change(self, delimiter):
        try:
            time.sleep(0.5)
            self.tsl.write(f'SYST:COMM:GPIB:DEL {delimiter}')
            self.logger.info(f"Delimiter changed to {delimiter}.")
        except Exception as e:
            self.logger.error(f"Error changing delimiter: {e}")

    def trig_src(self, trigg):
        try:
            time.sleep(0.5)
            self.tsl.write(f'TRIG:INP:EXT {trigg}')
            self.logger.info(f"Trigger source set to {trigg}.")
        except Exception as e:
            self.logger.error(f"Error setting trigger source: {e}")

    def trig_mode(self, Mode):
        try:
            time.sleep(0.5)
            self.tsl.write(f'TRIG:OUTP {Mode}')
            self.logger.info(f"Trigger mode set to {Mode}.")
        except Exception as e:
            self.logger.error(f"Error setting trigger mode: {e}")
