from robot import Robot
from dynamixel import Dynamixel

#updated device name due to me using windows instead of linux lol
leader_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM4').instantiate()
follower_dynamixel = Dynamixel.Config(baudrate=1_000_000, device_name='COM3').instantiate()
# had to remove servo id 1 and 7 from follower and leader due to follower id1 motor being broken :(
follower = Robot(follower_dynamixel, servo_ids=[2, 3, 4, 5, 6])
leader = Robot(leader_dynamixel, servo_ids=[8, 9, 10, 11, 12])
leader.set_trigger_torque()


while True:
    follower.set_goal_pos(leader.read_position())