import cv2
import mediapipe
import numpy
from keyboard import DrawKeyboard, ROWS, SIZES, ALIASES
from win32api import GetSystemMetrics

# Set resolution for faster processing (lower resolution)
WIDTH, HEIGHT = int(cv2.CAP_PROP_FRAME_WIDTH * GetSystemMetrics(0) / 7), int(cv2.CAP_PROP_FRAME_HEIGHT * GetSystemMetrics(1) / 7)
KEY_SIDE = WIDTH // 15
START = (HEIGHT - (KEY_SIDE * len(ROWS))) // 2

# Set up mediapipe hand detection model
MP_HANDS = mediapipe.solutions.hands
MP_DRAWING = mediapipe.solutions.drawing_utils

# Define the points to track for finger tips
POINTS = [
    MP_HANDS.HandLandmark.INDEX_FINGER_TIP,
    MP_HANDS.HandLandmark.MIDDLE_FINGER_TIP,
    MP_HANDS.HandLandmark.RING_FINGER_TIP,
]

# Set threshold values for each finger tip for detection
THRESHOLDS = {
    MP_HANDS.HandLandmark.THUMB_TIP: -0.13,
    MP_HANDS.HandLandmark.INDEX_FINGER_TIP: -0.15,
    MP_HANDS.HandLandmark.MIDDLE_FINGER_TIP: -0.17,
    MP_HANDS.HandLandmark.RING_FINGER_TIP: -0.16,
    MP_HANDS.HandLandmark.PINKY_TIP: -0.14,
}

TIMEOUT = {}
EXCLUDED = ['Backspace']
TIMEOUT_FRAMES = 15  # Reduce timeout for faster processing

# Initialize mediapipe hands detector with optimized settings for speed
HANDS = MP_HANDS.Hands(
    model_complexity=0,  # Fast model
    min_detection_confidence=0.3,  # Lower for faster processing
    min_tracking_confidence=0.3,   # Lower for faster tracking
    max_num_hands=1  # Track only one hand for faster performance
)

# Function to map finger positions to keyboard keys
def _getKey(coords):
    if coords[1] < START:
        return None
    row = int(((coords[1] - START) // KEY_SIDE))
    if row >= 0 and row < len(ROWS):
        KEY_END = 0
        for i in range(len(ROWS[row])):
            key = ROWS[row][i]
            if coords[0] >= KEY_END:
                if (key in SIZES and coords[0] <= KEY_END + (SIZES[key] * KEY_SIDE)) \
                    or coords[0] <= KEY_END + KEY_SIDE:
                    return key
                if key in SIZES: KEY_END += (SIZES[key] * KEY_SIDE)
                else: KEY_END += KEY_SIDE
    return None

# Main function to process image and detect key presses
def ProcessImage(image, calc):
    pressed = set()

    # Resize and flip the image for better performance
    image_resized = cv2.resize(image, (WIDTH, HEIGHT))
    image_flipped = cv2.flip(image_resized, 1)
    image_rgb = cv2.cvtColor(image_flipped, cv2.COLOR_BGR2RGB)
    
    # Process the image using mediapipe hand detection model
    results = HANDS.process(image_rgb)

    image.flags.writeable = True
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # Create an empty frame to draw the keyboard
    frame = numpy.zeros((HEIGHT, WIDTH, 3), numpy.uint8)

    # If hands are detected, process the landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw the hand landmarks and connections
            MP_DRAWING.draw_landmarks(frame, hand_landmarks, MP_HANDS.HAND_CONNECTIONS)

            if calc:
                # Check for finger positions and map to keyboard keys
                for point in POINTS:
                    landmark = hand_landmarks.landmark[point]
                    x, y, z = float(landmark.x * WIDTH), float(landmark.y * HEIGHT), landmark.z
                    
                    # If finger tip is within threshold, map to key press
                    if z <= THRESHOLDS[point]:
                        key = _getKey((x, y))
                        if key and key not in EXCLUDED and key not in TIMEOUT:
                            if key in ALIASES:
                                pressed.add(ALIASES[key])
                            else:
                                pressed.add(key.lower())
                            TIMEOUT[key] = TIMEOUT_FRAMES

    # Update timeouts for each key
    for key in TIMEOUT:
        TIMEOUT[key] = max(TIMEOUT[key]-1, 0)

    # Return the updated keyboard frame and the pressed keys
    return DrawKeyboard(frame, TIMEOUT), pressed

# Main loop to capture video and process the frames
if __name__ == "__main__":
    # Open the webcam feed
    cap = cv2.VideoCapture(0)

    # Process every other frame to reduce load
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process every second frame
        frame_count += 1
        if frame_count % 2 == 0:
            # Process the image and detect pressed keys
            keyboard_frame, pressed_keys = ProcessImage(frame, True)

            # Overlay the virtual keyboard on top of the camera feed
            combined_frame = cv2.addWeighted(frame, 1, keyboard_frame, 0.5, 0)

            # Display the combined frame (live camera feed + virtual keyboard)
            cv2.imshow("Virtual Keyboard", combined_frame)

        # Display the original camera feed (optional)
        # cv2.imshow("Camera Feed", frame)

        # Exit the loop if 'ESC' key is pressed
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
