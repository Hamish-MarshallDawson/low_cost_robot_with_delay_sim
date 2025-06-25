#handles the actual movement of the leader and follower robots
# this is exlusively for windows, to change it to linux change the device names
from robot import Robot
from dynamixel import Dynamixel
import time
import shared_state as state


# a lot of this code is copied from the original low_cost_robot repo as all 
# I have added on top of it is the delay simulation and gui interface

def initialize_robots():
    #starts and configures the leader and follower robots
    #leader_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM4').instantiate()
    #follower_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM3').instantiate()
    leader_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='/dev/ttyACM1').instantiate()
    follower_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='/dev/ttyACM0').instantiate()
    
    
    follower = Robot(follower_dynamixel, servo_ids=[1, 2, 3, 4, 5, 6])
    leader = Robot(leader_dynamixel, servo_ids=[7, 8, 9, 10, 11, 12])
    leader.set_trigger_torque()
    
    return leader, follower

def read_leader_position(leader):
    #reads the leaders position and add it to the buffer
    leader_pos = leader.read_position()
    state.position_buffer.append((time.time(), leader_pos))
    return leader_pos

def get_delayed_position(leader_pos, target_time):
    #get the position of the leader from the buffer at the target time
    if not state.position_buffer:
        return leader_pos
    
    closest_entry = min(state.position_buffer, 
                       key=lambda x: abs(x[0] - target_time))
    return closest_entry[1]


##new feature!
def measure_system_delay(start_time):
    #measures actual system delay by calculating the time taken to excecute a command
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Adds the inputs from the leader to the delay samples
    state.DELAY_SAMPLES.append(elapsed_ms)
    if len(state.DELAY_SAMPLES) > state.MAX_DELAY_SAMPLES:
        state.DELAY_SAMPLES.pop(0)
    
    # Calculates the average
    state.SYSTEM_DELAY_MS = sum(state.DELAY_SAMPLES) / len(state.DELAY_SAMPLES)
    return elapsed_ms