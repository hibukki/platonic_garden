#!/bin/bash

mpremote fs mkdir shapes
mpremote fs mkdir animations
mpremote cp shapes/* :shapes
mpremote cp animations/* :animations
mpremote cp wifi_consts.py :wifi_consts.py
mpremote cp utils.py :utils.py
mpremote cp wifi_client.py :wifi_client.py
mpremote cp main.py :main.py 
mpremote reset
