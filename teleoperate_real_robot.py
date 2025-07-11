from robot import Robot
from dynamixel import Dynamixel
import collections 
import time
import random
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
NETWORK_DELAY = 0.0  # Start with no delay
MIN_DELAY = 0.0 # what is the least amount of delay that can be set
MAX_DELAY = 2.0 #maximum amount of delay that can be set
TARGET_DELAY = 0.0 #target delay for smooth transtion
TRANSITION_SPEED = 0.1 #how quickly the delay should transtion to the target delay
TRANSITION_ACTIVE = False
DELAY_STEP = 0.1 

#this is to stop multi key presses without causing jackiness in the arms
LAST_KEY_TIME = 0

# Variables to prevent rewinding/time-travel when delay increases
DELAY_ANCHOR_TIME = time.time()  # Time when delay was last changed
DELAY_ANCHOR_VALUE = 0.0         # Value of delay at anchor time

#explains the controls to the user for delay simulation
print("\nDelay Simulation Controls:")
print("  UP ARROW: Increase delay")
print(" r key: Randomize delay")
print("  DOWN ARROW: Decrease delay")

while True:
    
    current_time = time.time()
    if current_time - LAST_KEY_TIME > 0.3:
        if keyboard.is_pressed('up'):
            # Set anchor point if we're increasing delay
            if NETWORK_DELAY < (NETWORK_DELAY + DELAY_STEP):
                DELAY_ANCHOR_TIME = current_time
                DELAY_ANCHOR_VALUE = NETWORK_DELAY
                
            TARGET_DELAY = min(NETWORK_DELAY + DELAY_STEP, MAX_DELAY)
            TRANSITION_ACTIVE = True
            print(f"Increased delay to {NETWORK_DELAY:.2f} seconds")
            LAST_KEY_TIME = current_time  # Update timestamp
        
            #if down arrow is pressed this function decreases the delay
        elif keyboard.is_pressed('down'):
            TARGET_DELAY = max(MIN_DELAY, NETWORK_DELAY - DELAY_STEP)
            TRANSITION_ACTIVE = True
            print(f"Decreased delay to {NETWORK_DELAY:.2f} seconds")
            LAST_KEY_TIME = current_time  # Update timestamp
        
            # allows random amount of delay to be set by pressing r
        elif keyboard.is_pressed('r'):
            # Set anchor if new random delay is greater than current delay
            new_delay = random.uniform(MIN_DELAY, MAX_DELAY)
            if new_delay > NETWORK_DELAY:
                DELAY_ANCHOR_TIME = current_time
                DELAY_ANCHOR_VALUE = NETWORK_DELAY
                
            TARGET_DELAY = new_delay
            TRANSITION_ACTIVE = True
            print(f"Randomized delay from {NETWORK_DELAY:.2f} to {TARGET_DELAY:.2f} seconds")
            LAST_KEY_TIME = current_time  # Update timestamp
    
    if TRANSITION_ACTIVE:
        # Smoothly transition to the target delay
        if abs(NETWORK_DELAY - TARGET_DELAY) < TRANSITION_SPEED:
            NETWORK_DELAY = TARGET_DELAY
            TRANSITION_ACTIVE = False
        elif NETWORK_DELAY < TARGET_DELAY:
            NETWORK_DELAY += TRANSITION_SPEED
        else:
            NETWORK_DELAY -= TRANSITION_SPEED
    
    
    # Function to read leader position and store it in the buffer
    leader_pos = leader.read_position()
    position_buffer.append((time.time(), leader_pos))

    # Calculate how much time has passed since the delay anchor point
    time_since_anchor = current_time - DELAY_ANCHOR_TIME
    
    # Prevent time travel when delay increases
    if NETWORK_DELAY > DELAY_ANCHOR_VALUE and time_since_anchor < (NETWORK_DELAY - DELAY_ANCHOR_VALUE):
        # During increased delay transition, we want to "pause" rather than rewind
        target_time = DELAY_ANCHOR_TIME - DELAY_ANCHOR_VALUE
    else:
        # Normal operation - either we've waited long enough after a delay increase,
        # or we're decreasing delay which doesn't cause time travel
        target_time = current_time - NETWORK_DELAY

    delayed_position = leader_pos
    
    if position_buffer:
        closest_entry = min(position_buffer, 
                           key=lambda x: abs(x[0] - target_time))
        delayed_position = closest_entry[1]
        
    #Apply the delayed position to the follower robot
    follower.set_goal_pos(delayed_position)
    
    time.sleep(0.01)  # Sleep to avoid killing my cpu