"""
CALIBRATION FOR OHMPI. MOST OF THE MULTIPLEXER TESTING CODE IS FROM THE OHMPI TEAM'S TESTING HERE:
https://gitlab.irstea.fr/reversaal/OhmPi/-/tree/master
"""
import time , board, busio,adafruit_tca9548a
from adafruit_mcp230xx.mcp23017 import MCP23017
import digitalio
from digitalio import Direction
from utils import read_csv

address_a=0X70# choose the mux board address
address_b=0X71
address_m=0X72
address_n=0X73

class Calibration:
    def __init__(self, whichBoards, activationTime = 1):
       self.boards = whichBoards
       self.activation_time = activationTime
       self.i2c = busio.I2C(board.SCL, board.SDA)

    def switch_mux_on(electrode, address):
       tca = adafruit_tca9548a.TCA9548A(i2c, address)
       if electrode < 17:
           nb_i2C = 7
           a = electrode
       elif electrode > 16 and electrode < 33:
           nb_i2C = 6
           a = electrode - 16
       elif electrode > 32 and electrode < 49:
           nb_i2C = 5
           a = electrode - 32
       elif electrode > 48 and electrode < 65:
           nb_i2C = 4
           a = electrode - 48

       mcp2 = MCP23017(tca[nb_i2C])
       mcp2.get_pin(a - 1).direction = Direction.OUTPUT
       mcp2.get_pin(a - 1).value = True

    def switch_mux_off(electrode, address):
        tca = adafruit_tca9548a.TCA9548A(i2c, address)
        if electrode < 17:
            nb_i2C = 7
            a = electrode
        elif electrode > 16 and electrode < 33:
            nb_i2C = 6
            a = electrode - 16
        elif electrode > 32 and electrode < 49:
            nb_i2C = 5

            a = electrode - 32
        elif electrode > 48 and electrode < 65:
            nb_i2C = 4
            a = electrode - 48

        mcp2 = MCP23017(tca[nb_i2C])
        mcp2.get_pin(a - 1).direction = digitalio.Direction.OUTPUT
        mcp2.get_pin(a - 1).value = False

    def run_scheme(self, a, b, m, n, fn="simple_rainfall.csv"):
        df = read_csv("simple_rainfall.csv")
        for i in range(len(a)):
            self.switch_mux_on(a[i], address_a)
            self.switch_mux_on(b[i],address_b)
            self.switch_mux_on(m[i],address_m)
            self.switch_mux_on(n[i],address_n)
            print('electrodes:', a[i], ' ', b[i], ' ', m[i], ' ', n[i], ' activate')
            time.sleep(self.activation_time)

            self.switch_mux_off(a[i], address_a)
            self.switch_mux_off(b[i],address_b)
            self.switch_mux_off(m[i],address_m)
            self.switch_mux_off(n[i],address_n)
            print('electrodes:', a[i], ' ', b[i], ' ', m[i], ' ', n[i], ' deactivate')
            time.sleep(self.activation_time)

            print(
                f"Time: {df['time'][i]}  Injection Time: {df['inj time [ms]'][i]} Injected Current (A) {df['I [mA]'][i]}  Measured Potential (V): {df['Vmn [mV]'][i]}  Rhoa (ohmm): {df['Rhoa'][i]}  Acq. Depth (m): {df['z'][i]}")

    def format_scheme(self, scheme_file):
        df = read_csv(scheme_file)

        return df["A"].astype(int), df["B"].astype(int), df["M"].astype(int), df["N"].astype(int)

    def run_one_cycle(self, fn="simple_rainfall.csv", repeat=10):
        a, b, m, n = self.format_scheme(fn)
        print("STARTING DIPOLE DIPOLE SCHEME FOR", len(a), "ELECTRODE COMBINATIONS")
        print("Time: ", time.ctime(time.time()))
        print("Estimated time for one cycle: ", round(self.activation_time*2*len(a)/60), " minutes.")
        print("Repeating cycle every ", repeat, " minutes.")

        start = time()
        self.run_scheme(a, b, m, n)
        duration = start - time()

        print("FINISHED CYCLE. SLEEPING FOR ", round(repeat - duration/60), "MINUTES.")

        time.sleep(repeat - duration/60)