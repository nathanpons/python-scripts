import keyboard
import threading
import time

toggle = False
w_thread = None

def hold_w():
    while toggle:
        keyboard.press('w')
        time.sleep(0.01)  # Keeps the key pressed

def on_f6(e):
    global toggle, w_thread
    toggle = not toggle
    if toggle:
        w_thread = threading.Thread(target=hold_w)
        w_thread.start()
    else:
        keyboard.release('w')

keyboard.on_press_key('f6', on_f6)

print("Press F6 to toggle holding 'W'. Press ESC to quit.")
keyboard.wait('esc')