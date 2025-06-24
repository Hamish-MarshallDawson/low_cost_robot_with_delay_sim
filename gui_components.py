#This is the file that provides the visual aspect of the delay simulator, I don't really understand the gui aspect but learning
import tkinter as tk
from tkinter import ttk
import time
import random
import shared_state as state

# Event handler functions
def randomize_delay():
    #gives random delay between the min and max set in shared_state.py
    new_delay = random.uniform(state.MIN_DELAY, state.MAX_DELAY)
    if new_delay > state.NETWORK_DELAY:
        state.DELAY_ANCHOR_TIME = time.time()
        state.DELAY_ANCHOR_VALUE = state.NETWORK_DELAY
        
    state.TARGET_DELAY = new_delay
    state.TRANSITION_ACTIVE = True
    
    return f"Randomized delay to {state.TARGET_DELAY:.2f} seconds"

def toggle_jitter(jitter_btn, status_callback):
    #toggles the jitter effect on and off
    if state.JITTER_ENABLED:
        state.JITTER_ENABLED = False
        jitter_btn.config(text="Enable Jitter")
        status_callback("Jitter Disabled")
    else:
        state.JITTER_ENABLED = True
        state.JITTER_RANGE = state.JITTER_INTENSITY
        state.JITTER_MIN = max(state.MIN_DELAY, state.NETWORK_DELAY - state.JITTER_RANGE/2)
        state.JITTER_MAX = min(state.MAX_DELAY, state.NETWORK_DELAY + state.JITTER_RANGE/2)
        
        state.DELAY_ANCHOR_TIME = time.time()
        state.DELAY_ANCHOR_VALUE = state.NETWORK_DELAY
        jitter_btn.config(text="Disable Jitter")
        status_callback(f"Jitter Enabled: {state.JITTER_MIN:.2f}s - {state.JITTER_MAX:.2f}s")

def update_jitter_intensity(selection, status_callback):
    #depending on what jitter intensity is selected it will change the range of the jitter effect
    selected = selection.get()
    state.JITTER_INTENSITY = state.JITTER_INTENSITY_OPTIONS[selected]
    state.JITTER_RANGE = state.JITTER_INTENSITY
    
    if state.JITTER_ENABLED:
        state.JITTER_MIN = max(state.MIN_DELAY, state.NETWORK_DELAY - state.JITTER_RANGE/2)
        state.JITTER_MAX = min(state.MAX_DELAY, state.NETWORK_DELAY + state.JITTER_RANGE/2)
        status_callback(f"Jitter intensity set to {selected}: {state.JITTER_MIN:.2f}s-{state.JITTER_MAX:.2f}s")
    else:
        status_callback(f"Jitter intensity set to {selected}")

def on_slider_press():
    #handles the slider stuff
    return True

def on_slider_release(slider, status_callback):
    #handles what happens when the slider is released 
    new_delay = slider.get()
    if new_delay > state.NETWORK_DELAY:
        state.DELAY_ANCHOR_TIME = time.time()
        state.DELAY_ANCHOR_VALUE = state.NETWORK_DELAY
    
    state.TARGET_DELAY = new_delay
    state.TRANSITION_ACTIVE = True
    status_callback(f"Setting delay to {state.TARGET_DELAY:.2f} seconds")
    return False