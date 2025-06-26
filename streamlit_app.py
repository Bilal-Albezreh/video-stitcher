import streamlit as st
import cv2
import numpy as np
import tempfile
import os

st.title("Video Stitcher")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

FRAME_INTERVAL = 30  # extract one frame every 30 frames

if uploaded_file:
    # Save uploaded video to a temp file
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    tfile.close()
    
    cap = cv2.VideoCapture(tfile.name)
    
    frames = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % FRAME_INTERVAL == 0:
            frames.append(frame)
        frame_count += 1
    
    cap.release()
    
    if len(frames) < 2:
        st.warning("Not enough frames extracted to stitch. Please upload a longer video.")
    else:
        stitcher = cv2.Stitcher_create()
        status, pano = stitcher.stitch(frames)
        
        if status == cv2.Stitcher_OK:
            # Convert BGR to RGB for displaying
            pano_rgb = cv2.cvtColor(pano, cv2.COLOR_BGR2RGB)
            st.image(pano_rgb, caption="Stitched Panorama")
        else:
            st.error(f"Error during stitching: {status}")
    
    # Clean up temp file
    os.remove(tfile.name) 
