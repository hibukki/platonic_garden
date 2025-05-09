#!/bin/bash

mpremote fs mkdir shapes
mpremote cp shapes/* :shapes
mpremote cp main.py :main.py 
mpremote reset
