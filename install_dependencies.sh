#!/bin/bash

PORT=${PORT:-/dev/cu.usbserial-210}

mpremote connect "$PORT" mip install pathlib github:josverl/micropython-stubs/mip/typing.mpy github:josverl/micropython-stubs/mip/typing_extensions.mpy copy
