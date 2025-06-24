# All the main varaibles of the shared state for the network delay simulation.
import time
import collections

# Configuration constants
MIN_DELAY = 0.0
#adjust this to change the maximum delay amount
MAX_DELAY = 10.0
DELAY_STEP = 0.1
TRANSITION_SPEED = 0.2

# Shared state variables
position_buffer = collections.deque(maxlen=1000)
NETWORK_DELAY = 0.0
TARGET_DELAY = 0.0
TRANSITION_ACTIVE = False
#prevents robot timetravelling when delay increases
DELAY_ANCHOR_TIME = time.time()
DELAY_ANCHOR_VALUE = 0.0

# Jitter config
JITTER_ENABLED = False
JITTER_RANGE = 0.20
#these are set here and changed later in delay_simulator.py
JITTER_MIN = 0.0
JITTER_MAX = 0.0
LAST_JITTER_TIME = 0
JITTER_INTENSITY = 0.2
JITTER_INTENSITY_OPTIONS = {
    "Low": 0.05,
    "Medium": 0.2,
    "High": 0.5
}

# Flag to indicate if the slider is being dragged for gui
delay_slider_dragging = False  

# Threading control
running = True