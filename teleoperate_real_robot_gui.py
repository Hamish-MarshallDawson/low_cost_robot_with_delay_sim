from robot import Robot
from dynamixel import Dynamixel
import collections 
import time
import random
#decided to try add keyboard controls for variable delay
import keyboard  

#for gui stuff
import tkinter as tk
from tkinter import ttk
import threading


#updated device name due to me using windows instead of linux lol
leader_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM4').instantiate()
follower_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM3').instantiate()
# had to remove servo id 1 and 7 from follower and leader due to follower id1 motor being broken :(
follower = Robot(follower_dynamixel, servo_ids=[2, 3, 4, 5, 6])
leader = Robot(leader_dynamixel, servo_ids=[8, 9, 10, 11, 12])
leader.set_trigger_torque()

position_buffer = collections.deque(maxlen=1000) # buffer that creates a queue of the leaders movements the last 1000 movements

# Configurable delay (in seconds)
NETWORK_DELAY = 0.0  # Start with no delay
MIN_DELAY = 0.0 # what is the least amount of delay that can be set
MAX_DELAY = 2.0 #maximum amount of delay that can be set
TARGET_DELAY = 0.0 #target delay for smooth transtion
TRANSITION_SPEED = 0.1 #how quickly the delay should transtion to the target delay
TRANSITION_ACTIVE = False
DELAY_STEP = 0.1 
# Variables to prevent rewinding/time-travel when delay increases
DELAY_ANCHOR_TIME = time.time()  # Time when delay was last changed
DELAY_ANCHOR_VALUE = 0.0         # Value of delay at anchor time

#makes the main window for the gui
root = tk.Tk()
root.title("Robot Delay Control")
root.geometry("500x400")

#create frame for the control
control_frame = ttk.LabelFrame(root, text="Delay Controls")
control_frame.pack(padx=10, pady=10, fill='x')

#Current delay 
current_delay_var = tk.StringVar(value=f"Current Delay: {NETWORK_DELAY:.2f} seconds")
current_delay_label =ttk.Label(control_frame, textvariable=current_delay_var, font=("Arial", 14))
current_delay_label.pack(pady=10)

#Slider for delay control
delay_slider =ttk.Scale(
    control_frame,
    from_=MIN_DELAY,
    to=MAX_DELAY,
    orient='horizontal',
    length=400,
)
delay_slider.pack(pady=10, padx=10, fill="x")


#Buttons frame
button_frame = ttk.Frame(control_frame)
button_frame.pack(pady=10, fill="x")

# Modify button handler functions to allow interruption:
# def increase_delay():
#     global TARGET_DELAY, TRANSITION_ACTIVE, DELAY_ANCHOR_TIME, DELAY_ANCHOR_VALUE
#     DELAY_ANCHOR_TIME = time.time()
#     DELAY_ANCHOR_VALUE = NETWORK_DELAY
#     # Allow immediate response by updating TARGET_DELAY directly
#     TARGET_DELAY = min(TARGET_DELAY + DELAY_STEP, MAX_DELAY)
#     TRANSITION_ACTIVE = True
#     status_var.set(f"Increased delay to {TARGET_DELAY:.2f} seconds")
    
#     # Visual feedback
#     increase_btn.state(['pressed'])
#     root.after(100, lambda: increase_btn.state(['!pressed']))

# def decrease_delay():
#     global TARGET_DELAY, TRANSITION_ACTIVE
#     # Allow immediate response by updating TARGET_DELAY directly
#     TARGET_DELAY = max(MIN_DELAY, TARGET_DELAY - DELAY_STEP)
#     TRANSITION_ACTIVE = True
#     status_var.set(f"Decreased delay to {TARGET_DELAY:.2f} seconds")
    
#     # Visual feedback
#     decrase_btn.state(['pressed'])
#     root.after(100, lambda: decrase_btn.state(['!pressed']))

def randomize_delay():
    global TARGET_DELAY, TRANSITION_ACTIVE, DELAY_ANCHOR_TIME, DELAY_ANCHOR_VALUE
    new_delay = random.uniform(MIN_DELAY, MAX_DELAY)
    if new_delay > NETWORK_DELAY:
        DELAY_ANCHOR_TIME = time.time()
        DELAY_ANCHOR_VALUE = NETWORK_DELAY
        
    TARGET_DELAY = new_delay
    TRANSITION_ACTIVE = True
    status_var.set(f"Randomized delay to {TARGET_DELAY:.2f} seconds")  # Changed from print()
    
    # Visual feedback
    randomize_btn.state(['pressed'])
    root.after(100, lambda: randomize_btn.state(['!pressed']))
    
# #adds buttons to the gui
# increase_btn = ttk.Button(button_frame, text="Increase (+0.1s)", command=increase_delay)
# increase_btn.pack(side="left", padx=5, expand=True, fill="x")

# decrase_btn = ttk.Button(button_frame, text="Decrease (-0.1s)", command=decrease_delay)
# decrase_btn.pack(side="left", padx=5, expand=True, fill="x")

randomize_btn = ttk.Button(button_frame, text="Randomize Delay", command=randomize_delay)
randomize_btn.pack(side="left", padx=5, expand=True, fill="x")

#Status display 
status_var = tk.StringVar(value="System Ready")
status_label = ttk.Label(root, textvariable=status_var, font=("Arial", 10))
status_label.pack(pady=10)

#Progress bar to visualse current delay
progress_frame = ttk.LabelFrame(root, text ="Delay Visualization")
progress_frame.pack(padx=10, pady=10, fill='x')

delay_progress = ttk.Progressbar(
    
    progress_frame,
    orient="horizontal",
    length=400,
    mode='determinate',
    maximum=MAX_DELAY
)

delay_progress.pack(pady=10, padx=10, fill="x")



#func to run to control robot in separate thread

def robot_control_thread():
    # Add DELAY_ANCHOR_TIME and DELAY_ANCHOR_VALUE to the global declaration:
    global NETWORK_DELAY, TRANSITION_ACTIVE, DELAY_ANCHOR_TIME, DELAY_ANCHOR_VALUE, TARGET_DELAY  
    
    while running:
        try:
            # Read leader position and store in buffer
            leader_pos = leader.read_position()
            position_buffer.append((time.time(), leader_pos))
            
            # Handle the delay transition
            if TRANSITION_ACTIVE:
                if abs(NETWORK_DELAY - TARGET_DELAY) < TRANSITION_SPEED:
                    NETWORK_DELAY = TARGET_DELAY
                    TRANSITION_ACTIVE = False
                elif NETWORK_DELAY < TARGET_DELAY:
                    NETWORK_DELAY += TRANSITION_SPEED
                else:
                    NETWORK_DELAY -= TRANSITION_SPEED
            
            # Process slider value when not actively transitioning
            if not TRANSITION_ACTIVE:
                slider_value = delay_slider.get()
                if abs(slider_value - NETWORK_DELAY) > 0.01:
                    # Handle anchor point if delay is increasing
                    if slider_value > NETWORK_DELAY:
                        DELAY_ANCHOR_TIME = time.time()
                        DELAY_ANCHOR_VALUE = NETWORK_DELAY
                    TARGET_DELAY = slider_value
                    TRANSITION_ACTIVE = True
            
            # Calculate time since anchor point
            current_time = time.time()
            time_since_anchor = current_time - DELAY_ANCHOR_TIME
            
            # Prevent time travel when delay increases
            if NETWORK_DELAY > DELAY_ANCHOR_VALUE and time_since_anchor < (NETWORK_DELAY - DELAY_ANCHOR_VALUE):
                target_time = DELAY_ANCHOR_TIME - DELAY_ANCHOR_VALUE
            else:
                target_time = current_time - NETWORK_DELAY
            
            # Find the delayed position
            delayed_position = leader_pos
            if position_buffer:
                closest_entry = min(position_buffer, 
                                   key=lambda x: abs(x[0] - target_time))
                delayed_position = closest_entry[1]
            
            # Apply to follower robot
            follower.set_goal_pos(delayed_position)
            
            # Sleep to avoid high CPU usage
            time.sleep(0.01)
        
        except Exception as e:
            # Log error and update status
            print(f"Error in robot thread: {e}")
            status_var.set(f"ERROR: {e}")
            time.sleep(1)  # Pause to avoid rapid error loops

# Modify update_gui to ensure correct values:
def update_gui():
    if running:
        # Update with correct current values
        current_delay_var.set(f"Current Delay: {NETWORK_DELAY:.2f} seconds")
        
        # Update progress bar - ensure it shows current value
        delay_progress["value"] = NETWORK_DELAY
        delay_progress["maximum"] = MAX_DELAY  # Ensure max is correct
        
        # Update slider position only when not being dragged
        if not delay_slider_dragging:
            delay_slider.set(NETWORK_DELAY)
        
        # Faster updates for more responsive UI
        root.after(50, update_gui)  # Update twice as fast (was 100ms)

# Flag to track if slider is being dragged
delay_slider_dragging = False

def on_slider_press(event):
    global delay_slider_dragging
    delay_slider_dragging = True

def on_slider_release(event):
    global delay_slider_dragging, TARGET_DELAY, TRANSITION_ACTIVE, DELAY_ANCHOR_TIME, DELAY_ANCHOR_VALUE
    delay_slider_dragging = False
    
    # Set new target delay from slider
    new_delay = delay_slider.get()
    if new_delay > NETWORK_DELAY:
        DELAY_ANCHOR_TIME = time.time()
        DELAY_ANCHOR_VALUE = NETWORK_DELAY
    
    TARGET_DELAY = new_delay
    TRANSITION_ACTIVE = True
    status_var.set(f"Setting delay to {TARGET_DELAY:.2f} seconds")

# Connect slider events
delay_slider.bind("<ButtonPress-1>", on_slider_press)
delay_slider.bind("<ButtonRelease-1>", on_slider_release)

# Flag to control the robot thread
running = True

# Start robot control thread
robot_thread = threading.Thread(target=robot_control_thread)
robot_thread.daemon = True
robot_thread.start()

# Start GUI updates
update_gui()

# Handle window close
def on_closing():
    global running
    running = False
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI main loop
root.mainloop()