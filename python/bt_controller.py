import vgamepad as vg
import time

from python.bt_server import BtServer
from python.animate import start_gui

# Create a gamepad object
gamepad = vg.VX360Gamepad()

def start_bt_server():
    bt_server = BtServer(verbose=False)
    bt_server.run()
    print("Waiting for bt service to start")
    while not bt_server.is_ready():
        time.sleep(0.1)
    print("BT service is up!")
    return bt_server

# Main loop to press the jump button every 10 seconds
print("Preparing to launch BT service")
max_angle = 20
deadzone = 5
bt_server = start_bt_server()
watchdog_tolerance = 2  # Restart connection, if no new values received for this time (seconds)
gui_visualizer = start_gui(max_angle)
# time.sleep(5)
while True:
    yaw, pitch, roll = bt_server.get_orientation()

    if time.time() - bt_server.update_timestamp > watchdog_tolerance:
        print("Connection lost... attempting to re-establish!")
        bt_server.stop()
        bt_server = start_bt_server()

    # pitch = -pitch
    roll = -roll

    if abs(pitch) < deadzone:
        pitch = 0
    # if abs(roll) < deadzone:
    #     roll = 0
    gui_visualizer.update_values(yaw, pitch, roll)
    roll = roll / max_angle  # From [-90, 90] to [-1, 1]
    pitch = pitch / max_angle  # From [-90, 90] to [-1, 1]
    roll = max(min(roll, 1), -1)  # Clamp between [-1, 1]
    pitch = max(min(pitch, 1), -1)  # Clamp between [-1, 1]
    gamepad.left_joystick_float(x_value_float=roll, y_value_float=pitch)
    gamepad.update()
    gamepad.right_trigger_float(pitch)
    gamepad.left_trigger_float(-pitch)
    gamepad.update()
    time.sleep(0.01)
    print(yaw, pitch, roll)
bt_server.stop()



#%%
