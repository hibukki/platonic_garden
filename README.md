# Platonic Garden

## Pins on PCB are marked with JX
Some of the pins cannot be used
* J9: GPIO 35: ❌ Don't use - input‑only ADC pin; has no output driver.
* J8: GPIO 33: ✅ Use - 
* J7: GPIO 26: ✅ Use
* J6: GPIO 13: ✅ Use
* J2: GPIO 03: ❌ Don't use - UART0 RX for USB/serial; driving it breaks REPL/flash comms.
* J3: GPIO 18: ✅ Use
* J4: GPIO 05: ❌ Don't use - boot‑strapping pin that must be high; NeoPixel lows can trap the chip in bootloader.
* J5: GPIO 02: ❌ Don't use - boot‑strapping pin that must be high; any low at reset prevents normal boot.

## The environment
### Creating the environment
On mack:
```bash
brew install python@3.12
./create_environment
source .venv/bin/activate
```

### Burning the ESP32 for the 1st time
This installs micropython on the ESP32 and runs all the other shell scripts in order to install dependencies and deploy the code
```bash
./burn.sh
```

### Installing dependencies on esp32
If you added an esp32 dependency, add it to the end of the line in `install_dependencies.sh` and run
```bash
./install_dependencies.sh
```

### Deploying the code
If you added files that need to be deployed to the esp32, add it to `deploy.sh`.

Every time you change the code run
```bash
./depoy.sh
```
