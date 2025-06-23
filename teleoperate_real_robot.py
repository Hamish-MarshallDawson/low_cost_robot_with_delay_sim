from robot import Robot
from dynamixel import Dynamixel

import collections 
import time


#decided to try add keyboard controls for variable delay
import keyboard  

#updated device name due to me using windows instead of linux lol
leader_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM4').instantiate()
follower_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM3').instantiate()
# had to remove servo id 1 and 7 from follower and leader due to follower id1 motor being broken :(
follower = Robot(follower_dynamixel, servo_ids=[2, 3, 4, 5, 6])
leader = Robot(leader_dynamixel, servo_ids=[8, 9, 10, 11, 12])
leader.set_trigger_torque()

position_buffer = collections.deque(maxlen=1000) # buffer that creates a queue of the leaders movements the last 1000 movements
last_info_time = 0  # Variable to track the last time we printed info

# Configurable delay (in seconds)
NETWORK_DELAY = 0.0  # Start with 500ms delay
MIN_DELAY = 0.0
MAX_DELAY = 2.0
DELAY_STEP = 0.1


print("\nDelay Simulation Controls:")
print("  UP ARROW: Increase delay")
print("  DOWN ARROW: Decrease delay")

while True:
    
    # function to add delay when users presses up arrow key 
    if keyboard.is_pressed('up'):
        NETWORK_DELAY = min(NETWORK_DELAY + DELAY_STEP, MAX_DELAY)
        print(f"Increased delay to {NETWORK_DELAY:.2f} seconds")
        time.sleep(0.5) # to prevent accidental multi press

    #if down arrow is pressed this function decreases the delay
    elif keyboard.is_pressed('down'):
        NETWORK_DELAY = max(MIN_DELAY, NETWORK_DELAY - DELAY_STEP)
        print(f"Decreased delay to {NETWORK_DELAY:.2f} seconds")
        time.sleep(0.5) # to prevent accidental multi press
    
    
    # Function to read leader position and store it in the buffer
    leader_pos =leader.read_position()
    position_buffer.append((time.time(), leader_pos))

    #   get the specific position from the que based on the delay currently set
    current_time = time.time()
    target_time = current_time - NETWORK_DELAY

    delayed_position = leader_pos
    
    if position_buffer:
        closet_entry = min(position_buffer, 
                           key=lambda x: abs(x[0] - target_time))
        delayed_position = closet_entry[1]
        
    #Apply the delayed position to the follower robot
    
    
    follower.set_goal_pos(delayed_position)
    
    time.sleep(0.01)  # Sleep to avoid killing my cpu 