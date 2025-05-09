#!/bin/bash

mpremote fs mkdir shapes
mpremote fs mkdir animations
mpremote cp shapes/* :shapes
mpremote cp animations/* :animations
mpremote cp main.py :main.py 
mpremote reset
