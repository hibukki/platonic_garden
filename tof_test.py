import machine, neopixel
from machine import Pin, SoftI2C, Timer
from VL53L0X import VL53L0X
from time import sleep
import time
# from rainbow import animate

print("setting up i2c")
sda = Pin(21)
scl = Pin(22)
Xshut0 = Pin (23, Pin.OUT,value=True)
Xshut1 = Pin (4, Pin.OUT,value=True)
Xshut2 = Pin (15, Pin.OUT,value=True)
Xshut3 = Pin (12, Pin.OUT,value=True)
# THIS PIN IS INPUT ONLY FUCK YOU
#Xshut4 = Pin (39, Pin.OUT,value=True)
tofArray = [Xshut0,Xshut1,Xshut2,Xshut3]
triggeredTofArray = [False,False,False,False]

id = 0
i2c = SoftI2C(sda=sda, scl=scl)
# Remove music player code
# music = Player(pin_TX=17, pin_RX=16)
# music.volume(20)
np = neopixel.NeoPixel(Pin(33), 50)
# COLORS = [
#     (255, 0, 0),  # red
#     (0, 255, 0),  # green
#     (0, 0, 255),  # blue
# ]
MIN_REPEATS = 1
CHANGE_CHANCE = 0.1
COLORS = [
    (148, 0, 211),
    (75, 0, 130),
    (0, 0, 255),
    (0, 255, 0),
    (255, 255, 0),
    (255, 127, 0),
    (255, 0, 0)
]
print(i2c.scan())

# print("creating vl53lox object")
# Create a VL53L0X object
sleep(1)
if bool(i2c.scan()):
    tof = VL53L0X(i2c)

# Pre: 12 to 18 (initialized to 14 by default)
# Final: 8 to 14 (initialized to 10 by default)

# the measuting_timing_budget is a value in ms, the longer the budget, the more accurate the reading. 
budget = tof.measurement_timing_budget_us
# print("Budget was:", budget)
tof.set_measurement_timing_budget(5000)

# Sets the VCSEL (vertical cavity surface emitting laser) pulse period for the 
# given period type (VL53L0X::VcselPeriodPreRange or VL53L0X::VcselPeriodFinalRange) 
# to the given value (in PCLKs). Longer periods increase the potential range of the sensor. 
# Valid values are (even numbers only):

# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)

# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)


#     
def gpiotoggle(pin):
    pin.value(not pin.value())
def xshutarrayreset():
    n=len(tofArray)
    for i in range(n):
        tofArray[i].value(False)
    
def tofcycle():
    # First, shut down all sensors
    xshutarrayreset()
    n=len(tofArray)
    distances = []
    
    for i in range(n):
        # Only activate current sensor
        tofArray[i].value(True)
        sleep(0.05)  # Give sensor time to stabilize
        
        if bool(i2c.scan()):
            tof = VL53L0X(i2c)
            tof.set_measurement_timing_budget(1)
            tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
            tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
            
            # Take initial measurements to stabilize
            tof.ping()
            sleep(0.01)
            tof.ping()
            sleep(0.01)
            
            # Take and report actual measurement
            distance = tof.ping()-50
            distances.append(str(distance))
                
            if (distance < 500) and (triggeredTofArray[i]== False):
                triggeredTofArray[i]=True
                tof_array_rst_timer()
        else:
            distances.append("null")
                
        # Deactivate current sensor before moving to next
        tofArray[i].value(False)
        sleep(0.05)  # Give time to shut down completely
    
    # Print all distances on a single line
    print(" ".join(distances))

tof_timer = Timer(0)
tof_array_rst_ = Timer(1)

def perform_tof_scan(timer):
    tofcycle()
    
def tof_scan_timer():
    tof_timer.deinit()
    tof_timer.init(mode=Timer.PERIODIC, period=2000, callback=perform_tof_scan)
    
def tof_array_rst(timer):
    for i in range(len(triggeredTofArray)):
        triggeredTofArray[i] = False
    
def tof_array_rst_timer():
    tof_array_rst_.deinit()
    tof_array_rst_.init(mode=Timer.PERIODIC, period=10000, callback=tof_array_rst) 
    
tof_scan_timer()
tof_array_rst_timer()

def purple(np: neopixel.NeoPixel) -> None:
    for i in range(200):
        sleep(0.001)
        sleep_time_ns = 1000 + i * 10000
#         with wait_for_sleep_time_cm(sleep_time_ns):
        start_time = time.time_ns()
        np.fill((0, i, i))
        np.write()
    for i in range(200):
        sleep_time_ns = 1000 + i * 10000
        sleep(0.001)
#         with wait_for_sleep_time_cm(sleep_time_ns):
        start_time = time.time_ns()
        np.fill((0, 200-i, 200-i))
        np.write()
def yellow(np: neopixel.NeoPixel) -> None:
    for i in range(200):
        sleep_time_ns = 1000 + i * 10000
        sleep(0.001)
#         with wait_for_sleep_time_cm(sleep_time_ns):
        start_time = time.time_ns()
        np.fill((i, i, 0))
        np.write()
    for i in range(200):
        sleep_time_ns = 1000 + i * 10000
        sleep(0.001)
#         with wait_for_sleep_time_cm(sleep_time_ns):
        start_time = time.time_ns()
        np.fill((200-i,200-i , 0))
        np.write()

while True:
# Start ranging
#     print(tof.ping()-50, "mm")
#     tofcycle()
#     print(triggeredTofArray)

    print(triggeredTofArray)
    if(triggeredTofArray[0]):
        yellow(np)
    else:
        purple(np)
        
#     for i in range(3):
#         np.fill(COLORS[i])
#         np.write()
#         time.sleep(1)
#     sleep(0.5)