from rapid_trigger import factory
import pydirectinput as input
from threading import Thread
from vector import Vector2
import pyautogui
import keyboard
import pygame
import math
import time

input.FAILSAFE = False
input.PAUSE = 0

pygame.init()

clock = pygame.time.Clock()

joystick = pygame.joystick.Joystick(0)

# --- Config ---
sensitivity = 1     # Overall speed multiplier
deadzone = 0.05     # Deadzone for joystick (recommended 0.05 to 0.1)
exponent = 2.5      # How steeply speed increases (> 1)
linear_mix = 0.2    # How much linear control (0 to 1). Higher = more initial speed.
repeat_delay = 0.3  # Delay before repeat starts (in seconds)

keybinds = {
    'dpad_up':       (0.05, lambda: input.press('up')),
    'dpad_down':     (0.05, lambda: input.press('down')),
    'dpad_left':     (0.05, lambda: input.press('left')),
    'dpad_right':    (0.05, lambda: input.press('right')),
    'button_a':      (None, lambda: input.press('enter')),
    'button_b':      (None, lambda: input.press('backspace')),
    'button_x':      (0.05, lambda: input.press('space')),
    'button_y':      (0.05, lambda: input.press('tab')),
    'left_bumper':   (None, lambda: input.click(button='middle')),
    'right_bumper':  (None, lambda: hold_key('§', 0.5)),
}

# --- End Config ---

# Dont change these unless you know what you're doing
dpad_map = {
    'dpad_up': (0, 1),
    'dpad_down': (0, -1),
    'dpad_left': (-1, 0),
    'dpad_right': (1, 0),
}

button_map = {
    'button_a': 0,
    'button_b': 1,
    'button_x': 2,
    'button_y': 3,
    'left_bumper': 4,
    'right_bumper': 5,
}

# Calculate factors based on mix
lin_factor = sensitivity * linear_mix
exp_factor = sensitivity * (1.0 - linear_mix)

left_rapid = factory()
right_rapid = factory()

# Initialize state tracking for key repeats
key_repeat_state = {
    key: {'pressed': False, 'press_time': 0.0, 'last_action_time': 0.0}
    for key in keybinds
}

def hold_key(key, duration, block=False):
    """Presses and holds a key for a specified duration in a separate thread."""
    if not block:
        Thread(target=hold_key, args=(key, duration, True)).start()
        return

    try:
        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)
    except Exception as e:
        ...

mouse_state = [False, False]
def setMouseState(left, right):
    global mouse_state
    if left and not mouse_state[0]:
        input.mouseDown()
    elif not left and mouse_state[0]:
        input.mouseUp()

    if right and not mouse_state[1]:
        input.mouseDown(button='right')
    elif not right and mouse_state[1]:
        input.mouseUp(button='right')

    mouse_state = [left, right]

# Handlers
def handle_mouse():
    # Mouse movement
    x, y = 0.0, 0.0
    raw_x = joystick.get_axis(0)
    raw_y = joystick.get_axis(1)

    if abs(raw_x) > deadzone:
        x = raw_x

    if abs(raw_y) > deadzone:
        y = raw_y

    movement = Vector2(x,y)

    if movement.magnitude_squared() > 0:
        # Combine linear and exponential components
        x_abs = abs(movement.x)
        y_abs = abs(movement.y)

        x_combined = exp_factor * (x_abs ** exponent) + lin_factor * x_abs
        y_combined = exp_factor * (y_abs ** exponent) + lin_factor * y_abs

        # Apply sign and delta time
        x_move = math.copysign(x_combined, movement.x) * dt
        y_move = math.copysign(y_combined, movement.y) * dt

        if abs(x_move) > 0 or abs(y_move) > 0: # Only move if there's calculated movement
            input.moveRel(
                round(x_move),
                round(y_move)
            )

        return x_move, y_move
    return 0, 0

def handle_click():
    # Rapid trigger
    left  = (joystick.get_axis(4) + 1) / 2
    right = (joystick.get_axis(5) + 1) / 2

    click = [left_rapid(left), right_rapid(right)]
    setMouseState(*click)
    return click

def handle_scroll():
    # Scroll with right joystick
    scroll_y = joystick.get_axis(3) # Use a different variable name
    if abs(scroll_y) > deadzone:
        # Scale scroll amount by dt, ensure it's an integer
        scroll_amount = round(-scroll_y * dt * 5) # Added sensitivity scaling
        if scroll_amount != 0:
            pyautogui.scroll(scroll_amount, _pause=False)
            return scroll_amount
    return 0


# Helper to check if a specific keybind is active based on controller state
def is_key_active(key_name, hat_state, button_states):
    num_buttons = len(button_states)

    # Check D-pad
    if key_name.startswith('dpad'):
        return key_name in dpad_map and hat_state == dpad_map[key_name]

    # Check Buttons (including bumpers LB/RB)
    elif key_name.startswith('button') or key_name.endswith('bumper'): # Check both prefixes/suffixes
        if key_name in button_map:
            idx = button_map[key_name]
            return idx < num_buttons and button_states[idx]

    # Removed trigger axis check from here - handled separately if needed

    return False # Key type not recognized or mapped

# Simplified button/dpad handler with repeat logic
def handle_buttons():
    hat_state = joystick.get_hat(0)
    num_buttons = joystick.get_numbuttons()
    button_states = [joystick.get_button(i) for i in range(num_buttons)]
    current_time = time.monotonic()

    for key, (repeat_interval, action) in keybinds.items():
        # Skip keys handled elsewhere if necessary (e.g., if triggers were also in keybinds)
        # if key in ['left_trigger_axis', 'right_trigger_axis']: continue

        state = key_repeat_state[key]
        is_active = is_key_active(key, hat_state, button_states) # Use simplified checker

        if is_active:
            if not state['pressed']:
                # Initial press
                action()
                state['pressed'] = True
                state['press_time'] = current_time
                state['last_action_time'] = current_time
            # --- Repeat logic ---
            elif repeat_interval is not None and repeat_interval >= 0:
                time_since_press = current_time - state['press_time']
                time_since_last_action = current_time - state['last_action_time']

                initial_delay_met = (repeat_delay == 0 or time_since_press >= repeat_delay)
                repeat_interval_met = (repeat_interval == 0 or time_since_last_action >= repeat_interval)

                if initial_delay_met and repeat_interval_met:
                    action()
                    state['last_action_time'] = current_time
        else: # Key is not active
            if state['pressed']:
                state['pressed'] = False
                state['press_time'] = 0.0
                state['last_action_time'] = 0.0

while True:
    # Update dt (delta time in seconds)
    dt = clock.tick(1000)

    # Process Pygame events to update joystick states
    pygame.event.pump()

    movement = handle_mouse()
    click    = handle_click()
    scroll   = handle_scroll()
    handle_buttons()

    print(movement, click, end=' '*50 + '\r')


