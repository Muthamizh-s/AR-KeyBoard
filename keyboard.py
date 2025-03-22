import cv2
import numpy as np
from pyautogui import press

# Define the keyboard layout
ROWS = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
    ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Return'],
    ['LShift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'RShift'],
    ['Ctrl', 'WIN', 'Alt', 'Space', 'Alt', 'WIN', 'Ctrl']
]

# Define key sizes for special keys
SIZES = {
    'Backspace': 2,
    'Tab': 1.5,
    '\\': 1.5,
    'Caps': 1.5,
    'Return': 2.5,
    'LShift': 2.5,
    'RShift': 2.5,
    'Ctrl': 1.5,
    'WIN': 1.5,
    'Alt': 1.5,
    'Space': 6
}

# Key alias mapping for special functionality
ALIASES = {
    'LShift': 'shiftleft',
    'RShift': 'shiftright',
    'Caps': 'capslock',
}

# Function to draw a single key
def _drawKey(image, text, point1, point2, pressed=False):
    overlay = image.copy()
    
    # Set colors: light blue background for the key, green for pressed, gray for unpressed
    key_color = (200, 200, 255) if not pressed else (0, 255, 0)
    thickness = 1 if not pressed else -1  # Outline or filled if pressed

    cv2.rectangle(overlay, point1, point2, key_color, thickness)
    cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)

    # Adjust the font size and letter spacing
    font_scale = max(0.8, 3 - (len(text) / 2))
    text_width = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, font_scale, 2)[0][0]
    text_x = point1[0] + (point2[0] - point1[0] - text_width) // 2  # Center horizontally
    text_y = (point1[1] + point2[1]) // 2 + 5  # Center vertically

    # Change the letter color to white
    cv2.putText(
        image, text,
        org=(text_x, text_y),
        fontFace=cv2.FONT_HERSHEY_PLAIN,
        fontScale=font_scale,
        color=(255, 255, 255),  # White text
        thickness=2,
        lineType=cv2.LINE_AA,
        bottomLeftOrigin=False
    )
    return image

# Function to draw the entire keyboard
def DrawKeyboard(image, pressed_keys):
    X, Y = 0, 0
    height, width, _ = image.shape
    side = width // 15  # Scale the key width based on window width

    Y = (height - (side * len(ROWS))) // 2  # Center the keyboard vertically

    for row in ROWS:
        for key in row:
            is_pressed = key in pressed_keys and pressed_keys[key]

            if key not in SIZES:
                image = _drawKey(image, key, (X, Y), (X + side, Y + side), is_pressed)
                X += side
            else:
                image = _drawKey(
                    image, key, (X, Y),
                    (X + int(side * SIZES[key]), Y + side),
                    is_pressed
                )
                X += int(side * SIZES[key])

        X = 0
        Y += side

    return image

# Simulate key press functionality
def KeyPress(key):
    press(key.lower())

# Main program
if __name__ == "__main__":
    # Set the window dimensions and background color
    width = 1200  # Width of the keyboard window
    height = 800  # Height of the keyboard window
    keyboard_image = np.zeros((height, width, 3), dtype=np.uint8)  # Black background

    # Set a light gray color for the entire background
    keyboard_image[:] = (220, 220, 220)

    # Example of keys currently pressed
    pressed_keys = {'A': True, 'S': True, 'Space': True}

    # Draw the keyboard
    keyboard_image = DrawKeyboard(keyboard_image, pressed_keys)

    # Display the keyboard
    cv2.imshow("Virtual Keyboard", keyboard_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
