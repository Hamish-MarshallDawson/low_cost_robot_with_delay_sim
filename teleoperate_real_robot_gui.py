# main launch file for the teleoperation GUI with delay simulation
import tkinter as tk
from tkinter import ttk
import threading
import time

# Imports all required files for the gui and robot control/delay simulation
import shared_state as state
import robot_controller as rc
import delay_simulator as ds
import gui_components as gc

def robot_control_thread(leader, follower):
    while state.running:
        try:
            # Read leader position and store in buffer
            leader_pos = rc.read_leader_position(leader)
            
            current_time = time.time()
            
            # Handles jitter functionality
            if state.JITTER_ENABLED:
                if current_time - state.LAST_JITTER_TIME > 0.03:
                    if not state.TRANSITION_ACTIVE:
                        state.TARGET_DELAY = ds.smooth_jitter(
                            state.NETWORK_DELAY, state.JITTER_MIN, state.JITTER_MAX)
                        state.TRANSITION_ACTIVE = True
                    state.LAST_JITTER_TIME = current_time
            
            # Handle transitions
            ds.process_transitions()
            
            # Process slider value as its our main form of input for delay
            if not state.TRANSITION_ACTIVE:
                slider_value = delay_slider.get()
                #gets the absolute value of the slider and looks to see if it is different from the current delay
                if abs(slider_value - state.NETWORK_DELAY) > 0.01:
                    if slider_value > state.NETWORK_DELAY:
                        state.DELAY_ANCHOR_TIME = time.time()
                        state.DELAY_ANCHOR_VALUE = state.NETWORK_DELAY
                    state.TARGET_DELAY = slider_value
                    state.TRANSITION_ACTIVE = True
            
            # Get delayed position from buffer
            target_time = ds.calculate_target_time()
            delayed_position = rc.get_delayed_position(leader_pos, target_time)
            
            # Applies that delayed position to the follower robot
            follower.set_goal_pos(delayed_position)
        
        #error handling for the robot thread
        except Exception as e:
            print(f"Error in robot thread: {e}")
            status_var.set(f"ERROR: {e}")
            time.sleep(1)

def update_gui():
    #dynamically updates the gui to display the current delay and other info
    if state.running:
        # Update delay display
        if state.JITTER_ENABLED:
            current_delay_var.set(f"Current Delay: {state.NETWORK_DELAY:.2f}s (Jitter: {state.JITTER_MIN:.2f}-{state.JITTER_MAX:.2f}s)")
        else:
            current_delay_var.set(f"Current Delay: {state.NETWORK_DELAY:.2f} seconds")
        
        # Update progress bar
        delay_progress["value"] = state.NETWORK_DELAY
        
        # Update slider
        if not state.delay_slider_dragging:
            delay_slider.set(state.NETWORK_DELAY)
        
        # Schedule next update
        root.after(50, update_gui)

def on_closing():
    #handles file closing and cleanup
    state.running = False
    root.destroy()

# Main program execution
if __name__ == "__main__":
    # Initialize robots
    leader, follower = rc.initialize_robots()
    
    # Create main window for the program
    root = tk.Tk()
    root.title("Robot Delay Control")
    root.geometry("500x400")
    
    # Create GUI elements
    control_frame = ttk.LabelFrame(root, text="Delay Controls")
    control_frame.pack(padx=10, pady=10, fill='x')
    
    
    # Create current delay display and slider
    current_delay_var = tk.StringVar(value=f"Current Delay: {state.NETWORK_DELAY:.2f} seconds")
    current_delay_label = ttk.Label(control_frame, textvariable=current_delay_var, font=("Arial", 14))
    current_delay_label.pack(pady=10)
    
    delay_slider = ttk.Scale(
        control_frame,
        from_=state.MIN_DELAY,
        to=state.MAX_DELAY,
        orient='horizontal',
        length=400,
    )
    delay_slider.pack(pady=10, padx=10, fill="x")
    
    button_frame = ttk.Frame(control_frame)
    button_frame.pack(pady=10, fill="x")
    
    # Define status var update function
    def update_status(message):
        status_var.set(message)
    
    # Add buttons
    jitter_btn = ttk.Button(
        button_frame, 
        text="Enable Jitter", 
        command=lambda: gc.toggle_jitter(jitter_btn, update_status)
    )
    jitter_btn.pack(side="left", padx=5, expand=True, fill="x")
    
    randomize_btn = ttk.Button(
        button_frame, 
        text="Randomize Delay", 
        command=lambda: update_status(gc.randomize_delay())
    )
    randomize_btn.pack(side="left", padx=5, expand=True, fill="x")
    
    # Status display
    status_var = tk.StringVar(value="System Ready")
    status_label = ttk.Label(root, textvariable=status_var, font=("Arial", 10))
    status_label.pack(pady=10)
    
    # Progress bar
    progress_frame = ttk.LabelFrame(root, text="Delay Visualization")
    progress_frame.pack(padx=10, pady=10, fill='x')
    
    delay_progress = ttk.Progressbar(
        progress_frame,
        orient="horizontal",
        length=400,
        mode='determinate',
        maximum=state.MAX_DELAY
    )
    delay_progress.pack(pady=10, padx=10, fill="x")
    
    # Jitter intensity control
    jitter_intensity_frame = ttk.Frame(control_frame)
    jitter_intensity_frame.pack(pady=5, fill="x")
    
    ttk.Label(jitter_intensity_frame, text="Jitter Intensity:").pack(side="left", padx=5)
    
    jitter_intensity_var = tk.StringVar(value="Medium")
    jitter_intensity_menu = ttk.Combobox(
        jitter_intensity_frame, 
        textvariable=jitter_intensity_var,
        values=list(state.JITTER_INTENSITY_OPTIONS.keys()),
        width=10,
        state="readonly"
    )
    jitter_intensity_menu.pack(side="left", padx=5)
    jitter_intensity_menu.bind(
        "<<ComboboxSelected>>", 
        lambda event: gc.update_jitter_intensity(jitter_intensity_var, update_status)
    )
    
    # handles slider press and release events
    def on_slider_press_local(event):
        delay_slider_dragging = gc.on_slider_press()
    
    def on_slider_release_local(event):
        delay_slider_dragging = gc.on_slider_release(delay_slider, update_status)
    
    delay_slider.bind("<ButtonPress-1>", on_slider_press_local)
    delay_slider.bind("<ButtonRelease-1>", on_slider_release_local)
    
    # Set up closing handler
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start robot control thread
    robot_thread = threading.Thread(target=robot_control_thread, args=(leader, follower))
    robot_thread.daemon = True
    robot_thread.start()
    
    # Start GUI updates
    update_gui()
    
    # Start the GUI main loop
    root.mainloop()