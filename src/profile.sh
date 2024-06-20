#!/bin/bash
python3 -m cProfile -o o.prof main.py
python3 -m snakeviz --server o.prof
