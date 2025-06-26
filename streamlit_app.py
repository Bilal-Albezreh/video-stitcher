import streamlit as st

import cv2
import os

# Parameters
VIDEO_PATH = 'input.mp4'  # Change this to your video file
FRAME_INTERVAL = 30       # Extract one frame every 30 frames
OUTPUT_IMAGE = 'panorama.jpg'

# Create a directory to store extracted frames
os.makedirs('frames', exist_ok=True)

# Extract frames from video
cap = cv2.VideoCapture(VIDEO_PATH)
frame_count = 0
saved_frames = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    if frame_count % FRAME_INTERVAL == 0:
        frame_path = f'frames/frame_{frame_count}.jpg'
        cv2.imwrite(frame_path, frame)
        saved_frames.append(frame_path)
    frame_count += 1
cap.release()

# Load extracted frames
images = [cv2.imread(f) for f in saved_frames]

# Stitch images into a panorama
stitcher = cv2.Stitcher_create()
status, pano = stitcher.stitch(images)

if status == cv2.Stitcher_OK:
    cv2.imwrite(OUTPUT_IMAGE, pano)
    print(f'Panorama saved as {OUTPUT_IMAGE}')
else:
    print('Error during stitching:', status) 

st.title("Test App is Working 🎉")
st.write("If you're seeing this, Streamlit + Framer is connected properly!")

