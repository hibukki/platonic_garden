import machine, neopixel
import time


def main():
    np = neopixel.NeoPixel(machine.Pin(3), 240)
    while True:
        for i in range(3):
            np.fill((255,255,255))
            np.write()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated")