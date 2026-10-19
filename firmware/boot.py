# boot.py runs at startup, before main.py.
# Kept minimal on purpose: the application logic lives in main.py.
import gc
gc.collect()
