import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from threading import Thread

# Initialize hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Video capture
cap = cv2.VideoCapture(0)

# Function to handle hand gesture events
def handle_gesture(thumb_tip):
    height, width, _ = frame.shape
    tip_x, tip_y = int(thumb_tip.x * width), int(thumb_tip.y * height)

    for key_info in keys_info:
        x, y, key = key_info
        if x < tip_x < x + key_width and y < tip_y < y + key_height:
            pyautogui.press(key)
            update_keyboard_display(key)
            break

# Function to close the virtual keyboard window gracefully
def close_keyboard():
    keyboard_window.destroy()
    cap.release()
    cv2.destroyAllWindows()

# Create a virtual keyboard window
keyboard_window = tk.Tk()
keyboard_window.title("Virtual Keyboard")
keyboard_window.attributes('-alpha', 0.7)  # Set transparency

# Function to update the virtual keyboard display
def update_keyboard_display(key):
    keyboard_display_var.set(f'Pressed Key: {key}')

keyboard_display_var = tk.StringVar()
keyboard_display = tk.Label(keyboard_window, textvariable=keyboard_display_var, font=('Helvetica', 16))
keyboard_display.pack()

keys_row1 = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P']
keys_row2 = ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L']
keys_row3 = ['Z', 'X', 'C', 'V', 'B', 'N', 'M']

keys_info = []  # Store position and key information

for i, key in enumerate(keys_row1):
    x = i * 40
    y = 0
    keys_info.append((x, y, key))
    tk.Button(keyboard_window, text=key, command=lambda k=key: update_keyboard_display(k)).place(x=x, y=y)

for i, key in enumerate(keys_row2):
    x = i * 40
    y = 40
    keys_info.append((x, y, key))
    tk.Button(keyboard_window, text=key, command=lambda k=key: update_keyboard_display(k)).place(x=x, y=y)

for i, key in enumerate(keys_row3):
    x = i * 40
    y = 80
    keys_info.append((x, y, key))
    tk.Button(keyboard_window, text=key, command=lambda k=key: update_keyboard_display(k)).place(x=x, y=y)

keyboard_window.protocol("WM_DELETE_WINDOW", close_keyboard)

# Tkinter main loop
keyboard_window.mainloop()

# Main loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to detect hands
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract landmarks and use them to control the presentation
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            handle_gesture(thumb_tip)

            # Draw landmarks on the frame
            mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Gesture Presentation', frame)

    if cv2.waitKey(10) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Close the virtual keyboard window after the main loop
close_keyboard()
