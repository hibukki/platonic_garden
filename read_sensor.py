import machine
from machine import Pin, SoftI2C, Timer
from VL53L0X import VL53L0X
import asyncio
import utime  # Add this for timing measurements
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils import SharedState


async def read_sensor(state: SharedState):
    print("setting up i2c")
    sda = Pin(21)
    scl = Pin(22)
    Xshut0 = Pin(23, Pin.OUT, value=False)
    Xshut1 = Pin(4, Pin.OUT, value=False)
    Xshut2 = Pin(15, Pin.OUT, value=False)
    Xshut3 = Pin(12, Pin.OUT, value=False)
    # THIS PIN IS INPUT ONLY FUCK YOU
    #Xshut4 = Pin (39, Pin.OUT,value=True)
    tofArray = [Xshut0, Xshut1, Xshut2, Xshut3]

    # Use a higher I2C frequency for faster communication
    i2c = SoftI2C(sda=sda, scl=scl, freq=400000)  # Max speed for better performance
    print(i2c.scan())

    # Function to shutdown all sensors
    async def xshutarrayreset():
        for pin in tofArray:
            pin.value(False)
        await asyncio.sleep(0.05)  # Give time to shut down completely

    # Configure a single sensor
    async def configure_tof(sensor_index):
        # First shut down all sensors
        
        # Activate only the requested sensor
        tofArray[sensor_index].value(True)
        await asyncio.sleep(0.05)  # Give time to stabilize
        
        if bool(i2c.scan()):
            tof = VL53L0X(i2c)
            tof.set_measurement_timing_budget(20000)
            tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
            tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
            
            # Take initial measurements to stabilize
            tof.ping()
            await asyncio.sleep(0.01)
            
            return tof
        else:
            return None

    await xshutarrayreset()
    tof = await configure_tof(3)  # Using sensor 3 (Xshut3)
    tof.set_address(0x32)

    await asyncio.sleep(0.1)

    tof2 = await configure_tof(2)
    
    # Statistics variables
    total_read_time = 0
    read_count = 0
    min_read_time = float('inf')
    max_read_time = 0
    
    while True:
        # Measure how long the readings take
        start_time = utime.ticks_ms()
        
        # Read from both sensors
        distance = tof.ping() - 50
        distance2 = tof2.ping() - 50
        
        # Calculate elapsed time
        end_time = utime.ticks_ms()
        elapsed_ms = utime.ticks_diff(end_time, start_time)
        
        # Update statistics
        read_count += 1
        total_read_time += elapsed_ms
        min_read_time = min(min_read_time, elapsed_ms)
        max_read_time = max(max_read_time, elapsed_ms)
        avg_read_time = total_read_time / read_count
        
        if distance is not None:
            print(f"Distances: {distance}mm, {distance2}mm - Read time: {elapsed_ms}ms (min: {min_read_time}ms, avg: {avg_read_time:.1f}ms, max: {max_read_time}ms)")
            await state.update("distance", distance)
        else:
            print("Failed to read sensor")
            
        await asyncio.sleep(0.01)