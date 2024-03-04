import cv2
import numpy as np
from HandTrackingModule import HandDetector
import time
import subprocess

# Constants for window size
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Constants for button configuration
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 100
TEXT_COLOR = (255, 255, 255)  # White
EXIT_BUTTON_TEXT = "EXIT"
DELETE_BUTTON_TEXT = "DEL"
CLEAR_BUTTON_TEXT = "CLEAR"
BUTTON_CLICKED_COLOR = (0, 0, 255)  # Red in BGR format

# Delay configuration
CLICK_DELAY = 0.4  # 400 milliseconds

# Text space configuration
TEXT_SPACE_POSITION = (50, 650)
TEXT_SPACE_WIDTH = WINDOW_WIDTH - 100
TEXT_SPACE_HEIGHT = 50

# Gradient colors
c1 = np.array([31, 119, 180])  # blue in BGR
c2 = np.array([0, 128, 0])     # green in BGR

class Button:
    def __init__(self, pos, text, size=(BUTTON_WIDTH, BUTTON_HEIGHT), color=None):
        self.pos = pos
        self.size = size
        self.text = text
        self.color = color if color else c1  # Default to blue gradient if not specified
        self.last_click_time = 0  # Timestamp of the last click

    def draw(self, img, is_clicked=False):
        x, y = self.pos
        w, h = self.size
        if is_clicked:
            cv2.rectangle(img, (x, y), (x + w, y + h), BUTTON_CLICKED_COLOR, cv2.FILLED)
        else:
            # Create gradient
            for i in range(h):
                alpha = i / h
                color = tuple([int((1 - alpha) * self.color[j] + alpha * c2[j]) for j in range(3)])
                cv2.rectangle(img, (x, y + i), (x + w, y + i + 1), color, cv2.FILLED)
        cv2.putText(img, self.text, (x + 20, y + 70), cv2.FONT_HERSHEY_PLAIN, 4, TEXT_COLOR, 4)
        return img

    def isOver(self, pos1, pos2):
        x, y = self.pos
        w, h = self.size
        if (x < pos1[0] < x + w and y < pos1[1] < y + h) and \
           (x < pos2[0] < x + w and y < pos2[1] < y + h):
            return self.click()
        else:
            return False

    def click(self):
        current_time = time.time()
        if current_time - self.last_click_time >= CLICK_DELAY:
            self.last_click_time = current_time
            return True
        else:
            return False

# Define the keys in rows and add special keys
KEY_LAYOUT = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    [" ", "SHIFT", DELETE_BUTTON_TEXT, CLEAR_BUTTON_TEXT]  # Special keys row
]

def initialize_keyboard():
    keyboard = []
    startX, startY = 10, 40
    for i, row in enumerate(KEY_LAYOUT):
        for j, key in enumerate(row):
            if key == "123":
                posX = WINDOW_WIDTH - BUTTON_WIDTH - 50
                posY = startY + i * (BUTTON_HEIGHT + 10)
                keyboard.append(Button((posX, posY), key))
            else:
                posX = startX + j * (BUTTON_WIDTH + 10)
                posY = startY + i * (BUTTON_HEIGHT + 10)
                keyboard.append(Button((posX, posY), key))
    exit_button = Button((WINDOW_WIDTH - BUTTON_WIDTH - 50, 50), EXIT_BUTTON_TEXT)
    keyboard.append(exit_button)
    return keyboard, exit_button

# Define a class for the Keyboard with added functionalities
class Keyboard:
    def __init__(self):
        self.keyboard, self.exit_button = initialize_keyboard()
        self.shift_pressed = False
        self.caps_lock = False
        self.text_space = ""  # Initialize text space

    # Method to handle key presses
    def handle_key_press(self, key):
        if key == "EXIT":
            return "exit"
        elif key == "DEL":
            self.text_space = self.text_space[:-1]  # Remove the last character
        elif key == "CLEAR":
            self.text_space = ""  # Clear the text space
        elif key == "SHIFT":
            self.shift_pressed = not self.shift_pressed
        elif key == "123":
            # Toggle between alphabet and numeric/symbol keys
            self.keyboard, _ = initialize_numeric_keyboard() if self.numeric_mode else initialize_keyboard()
            self.numeric_mode = not self.numeric_mode
        elif key == "SPACE":
            self.text_space += " "
        else:
            # Handle uppercase and lowercase characters based on shift and caps lock state
            if self.shift_pressed or (self.caps_lock and not key.isdigit()):  
                self.text_space += key.upper()
            else:
                self.text_space += key.lower()

    # Method to draw the keyboard
    def draw(self, img):
        for button in self.keyboard:
            is_clicked = button.isOver(index_tip, middle_tip) if hands else False
            img = button.draw(img, is_clicked)
            if is_clicked:
                result = self.handle_key_press(button.text)
                if result == "exit":
                    return "exit"
        return img

def main():
    print("Starting the program...")  # Indicates the program has started
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.8, minTrackCon=0.5)

    keyboard, exit_button = initialize_keyboard()
    text_space = ""  # Initialize text space

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")  # Indicates webcam capture issue
            continue

        hands, img = detector.findHands(img, draw=False)  # Set draw to False to not visualize the hand
        index_tip, middle_tip = None, None  # Initialize as None to prevent reference before assignment

        if hands:
            # print(f"{len(hands)} hand(s) detected.")
            for hand in hands:
                lmList = hand['lmList']
                index_tip = lmList[8]
                middle_tip = lmList[12]

                cv2.circle(img, (index_tip[0], index_tip[1]), 15, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (middle_tip[0], middle_tip[1]), 15, (255, 0, 0), cv2.FILLED)

        # Draw all buttons and check for clicks
        for button in keyboard:
            is_clicked = button.isOver(index_tip, middle_tip) if hands else False
            img = button.draw(img, is_clicked)
            if is_clicked:
                print(f"Button {button.text} clicked.")  # Indicates button click
                if button.text == EXIT_BUTTON_TEXT:
                    cap.release()
                    cv2.destroyAllWindows()
                    return  # Exit the program

                elif button.text == DELETE_BUTTON_TEXT:
                    text_space = text_space[:-1]  # Remove the last character
                elif button.text == CLEAR_BUTTON_TEXT:
                    text_space = ""  # Clear the text space
                else:
                    text_space += button.text
                    print(f"Key {button.text} pressed")

        # Draw the text space
        cv2.rectangle(img, TEXT_SPACE_POSITION, 
                      (TEXT_SPACE_POSITION[0] + TEXT_SPACE_WIDTH, TEXT_SPACE_POSITION[1] + TEXT_SPACE_HEIGHT), 
                      (200, 200, 200), cv2.FILLED)
        cv2.putText(img, text_space, (TEXT_SPACE_POSITION[0], TEXT_SPACE_POSITION[1] + 40), 
                    cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)

        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    subprocess.Popen(["notepad.exe"])  # Open Notepad
    main()
