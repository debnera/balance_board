import vgamepad as vg
import time

# Create a gamepad object
gamepad = vg.VX360Gamepad()

# Function to press the A button (commonly used for jump)

def get_orientation():
    yaw = pitch = roll = 0
    return yaw, pitch, roll

def press_jump():
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    time.sleep(0.15)  # Hold the button for a short duration
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    yaw, pitch, roll = get_orientation()
    max_angle = 30
    gamepad.left_joystick_float(x_value_float=roll / max_angle, y_value_float=pitch / max_angle)

# Main loop to press the jump button every 10 seconds
while True:
    press_jump()
    print("jumputi jump")
    time.sleep(2)

#%%
