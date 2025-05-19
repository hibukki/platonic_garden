import machine
from machine import Pin, SoftI2C, Timer
from VL53L0X import VL53L0X
import asyncio
import utime  # Add this for timing measurements
from utils import SharedState

async def read_sensor(state: SharedState):
    print("setting up i2c")
    sda = Pin(21)
    scl = Pin(22)
    Xshut0 = Pin(23, Pin.OUT, value=False)
    Xshut1 = Pin(4, Pin.OUT, value=False)
    Xshut2 = Pin(15, Pin.OUT, value=False)
    Xshut3 = Pin(27, Pin.OUT, value=False)
    Xshut4 = Pin(25, Pin.OUT, value=False)
    # THIS PIN IS INPUT ONLY FUCK YOU
    #Xshut4 = Pin (39, Pin.OUT,value=True)
    pins = [Xshut0, Xshut1, Xshut2, Xshut3, Xshut4]
    
    # Initialize sensor_temp_array with correct length
    sensor_temp_array = [0] * len(pins)

    # Use a higher I2C frequency for faster communication
    i2c = SoftI2C(sda=sda, scl=scl, freq=400000)  # Max speed for better performance
    print(i2c.scan())

    # Function to shutdown all sensors
    async def xshutarrayreset():
        for pin in pins:
            pin.value(False)
        await asyncio.sleep(0.05)  # Give time to shut down completely

    # Configure a single sensor
    async def configure_tof(sensor_index):
        # Activate only the requested sensor
        # Assumes all others are off or at different addresses due to prior xshutarrayreset and sequential config
        pins[sensor_index].value(True)
        await asyncio.sleep(0.05)  # Give time for the sensor to power up and stabilize

        try:
            # Attempt to initialize the sensor (targets default address 0x29)
            tof = VL53L0X(i2c)
            
            # Configure timing and pulse periods
            tof.set_measurement_timing_budget(20000)
            tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18) # Period_pclks, Vcsel_period
            tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14) # Period_pclks, Vcsel_period for phasecal
            
            # Initial ping to stabilize and confirm sensor is working
            tof.ping()
            await asyncio.sleep(0.01) # Short delay after ping
            
            new_address = 0x33 + sensor_index
            tof.set_address(new_address)
            print(f"Sensor {sensor_index} configured successfully at address {hex(new_address)}")
            return tof
        except Exception as e:
            print(f"Error configuring sensor {sensor_index}: {e}")
            pins[sensor_index].value(False)  # Shut down the problematic sensor
            return None

    async def initialize_sensors(pins, i2c):
        await xshutarrayreset()
        tofs = []
        for i in range(len(pins)):
            tof = await configure_tof(i)
            if tof is not None:
                tofs.append(tof)
            else:
                tofs.append(None)
        return tofs

    tofs = await initialize_sensors(pins, i2c)
    
    # Statistics variables
    total_read_time = 0
    read_count = 0
    min_read_time = float('inf')
    max_read_time = 0
    last_init_time = utime.ticks_ms()  # Track when we last initialized sensors
    REINIT_INTERVAL = 20 * 60 * 1000  # 20 minutes in milliseconds

    while True:
        # Check if we need to reinitialize sensors
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, last_init_time) >= REINIT_INTERVAL:
            print("\nReinitializing sensors...")
            tofs = await initialize_sensors(pins, i2c)
            last_init_time = current_time
        
        # Measure how long the readings take
        start_time = utime.ticks_ms()
        
        sensor_readings = []
        for i, sensor_tof in enumerate(tofs): # Use enumerate for index
            if sensor_tof is not None:
                try:
                    distance = max(0, sensor_tof.ping() - 50) # Adjusted offset if necessary
                    # Update temperature based on distance
                    sensor_temp_array[i] = sensor_temp_array[i] + 10 if distance < 500 else sensor_temp_array[i] - 1
                    sensor_temp_array[i] = min(max(0, sensor_temp_array[i]), 255)
                    # Create a tuple with distance and temperature
                    sensor_readings.append((distance, sensor_temp_array[i]))
                except Exception as e:
                    # Log error and record None for this sensor in this cycle
                    print(f"Error reading from sensor {i} (expected addr {hex(0x33 + i)}): {e}")
                    sensor_readings.append((None, sensor_temp_array[i]))
                    tofs = await initialize_sensors(pins, i2c)
                    # Optional: could mark tofs[i] = None to stop trying to read from it.
                    # For now, it will retry on the next cycle.
            else:
                # Sensor was not configured or failed during configuration
                sensor_readings.append((None, sensor_temp_array[i]))
        
        # Calculate elapsed time
        end_time = utime.ticks_ms()
        elapsed_ms = utime.ticks_diff(end_time, start_time)
        
        # Update statistics
        read_count += 1
        total_read_time += elapsed_ms
        min_read_time = min(min_read_time, elapsed_ms)
        max_read_time = max(max_read_time, elapsed_ms)
        avg_read_time = total_read_time / read_count
        
        await state.update("distances", sensor_readings)
        #print(f"\rDistances: {sensor_readings} Time: {avg_read_time}ms", end="")
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(read_sensor(SharedState()))