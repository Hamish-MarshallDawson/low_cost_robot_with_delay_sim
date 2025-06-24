# This handles the network delay simulation and jitter effect 
# to adjust delay in any manner it is better to change shared_state.py than this file
import time
import random
import shared_state as state

def smooth_jitter(current_delay, jitter_min, jitter_max):
    """Generate smoother jitter transitions."""
    jitter_step = 0.005
    range_center = (jitter_min + jitter_max) / 2
    
    if current_delay >= range_center:
        move_up_probability = 0.3
    else:
        move_up_probability = 0.7
    
    if random.random() < move_up_probability:
        new_delay = min(jitter_max, current_delay + jitter_step)
    else:
        new_delay = max(jitter_min, current_delay - jitter_step)
    
    return new_delay

def update_jitter_range():
    """Update jitter range around current delay."""
    if state.JITTER_ENABLED:
        state.JITTER_MIN = max(state.MIN_DELAY, state.NETWORK_DELAY - state.JITTER_RANGE/2)
        state.JITTER_MAX = min(state.MAX_DELAY, state.NETWORK_DELAY + state.JITTER_RANGE/2)

def calculate_target_time():
    """Calculate target time for delay simulation with time-travel prevention."""
    current_time = time.time()
    time_since_anchor = current_time - state.DELAY_ANCHOR_TIME
    
    if (state.NETWORK_DELAY > state.DELAY_ANCHOR_VALUE and 
            time_since_anchor < (state.NETWORK_DELAY - state.DELAY_ANCHOR_VALUE)):
        # Prevent time travel
        return state.DELAY_ANCHOR_TIME - state.DELAY_ANCHOR_VALUE
    else:
        # Normal delay
        return current_time - state.NETWORK_DELAY

def process_transitions():
    """Handle delay transitions smoothly."""
    if state.TRANSITION_ACTIVE:
        if abs(state.NETWORK_DELAY - state.TARGET_DELAY) < state.TRANSITION_SPEED:
            state.NETWORK_DELAY = state.TARGET_DELAY
            state.TRANSITION_ACTIVE = False
        elif state.NETWORK_DELAY < state.TARGET_DELAY:
            state.NETWORK_DELAY += state.TRANSITION_SPEED
        else:
            state.NETWORK_DELAY -= state.TRANSITION_SPEED