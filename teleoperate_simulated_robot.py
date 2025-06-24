from robot import Robot
from dynamixel import Dynamixel
import numpy as np
import time
import mujoco.viewer
from simulation.interface import SimulatedRobot
import threading
import collections
import keyboard  # You may need to install this: pip install keyboard

# Configurable delay (in seconds)
NETWORK_DELAY = 0.5  # Start with 500ms delay
MIN_DELAY = 0.0
MAX_DELAY = 2.0
DELAY_STEP = 0.1

# Create position buffer with timestamps
position_buffer = collections.deque()

def read_leader_position():
    global position_buffer
    while True:
        try:
            # Read current position
            current_pos = np.array(leader.read_position())
            current_pos = (current_pos / 2048 - 1) * 3.14
            current_pos[1] = -current_pos[1]
            current_pos[3] = -current_pos[3]
            current_pos[4] = -current_pos[4]
            
            # Store position with current timestamp
            position_buffer.append((time.time(), current_pos))
            
            # Keep buffer from growing too large
            while len(position_buffer) > 1000:
                position_buffer.popleft()
                
            time.sleep(0.01)
        except Exception as e:
            print(f"Error reading position: {e}")
            time.sleep(0.5)

leader_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM4').instantiate()
leader = Robot(leader_dynamixel, servo_ids=[7, 8, 9, 10, 12])
leader.set_trigger_torque()

m = mujoco.MjModel.from_xml_path('simulation/low_cost_robot/scene.xml')
d = mujoco.MjData(m)

r = SimulatedRobot(m, d)

# Default position if no delayed data is available yet
target_pos = np.zeros(5)

# Start the thread for reading leader position
leader_thread = threading.Thread(target=read_leader_position)
leader_thread.daemon = True
leader_thread.start()

with mujoco.viewer.launch_passive(m, d) as viewer:
    start = time.time()
    last_info_time = 0
    
    print("\nDelay Simulation Controls:")
    print("  UP ARROW: Increase delay")
    print("  DOWN ARROW: Decrease delay")
    
    while viewer.is_running():
        step_start = time.time()
        
        # Check for keyboard input to adjust delay
        if keyboard.is_pressed('up'):
            NETWORK_DELAY = min(MAX_DELAY, NETWORK_DELAY + DELAY_STEP)
            time.sleep(0.2)  # Debounce
        elif keyboard.is_pressed('down'):
            NETWORK_DELAY = max(MIN_DELAY, NETWORK_DELAY - DELAY_STEP)
            time.sleep(0.2)  # Debounce
        
        # Display current delay every second
        if time.time() - last_info_time > 1.0:
            print(f"Current network delay: {NETWORK_DELAY*1000:.0f} ms")
            last_info_time = time.time()
        
        # Get position from the buffer that is NETWORK_DELAY seconds old
        target_pos_local = target_pos.copy()  # Default if no delayed data available
        
        current_time = time.time()
        target_time = current_time - NETWORK_DELAY
        
        # Find the closest position in our buffer to the target time
        closest_timestamp = None
        closest_time_diff = float('inf')
        
        for timestamp, pos in position_buffer:
            time_diff = abs(timestamp - target_time)
            if time_diff < closest_time_diff:
                closest_time_diff = time_diff
                closest_timestamp = timestamp
                target_pos_local = pos.copy()
        
        # Apply the delayed position to the robot
        r.set_target_pos(target_pos_local)
        mujoco.mj_step(m, d)
        viewer.sync()

        # Time management
        time_until_next_step = m.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)
