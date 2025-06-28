import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from io import BytesIO
import frontend

# Render header, CSS, and logo
frontend.render_header_and_css('ground.png', 'logo.png')

# --- Main UI ---

# File uploader
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
FRAME_INTERVAL = 30  # extract one frame every 30 frames

progress_text = ""
progress = st.empty()
progress_percent = st.empty()

if uploaded_file:
    # --- Stage 1: Uploading ---
    percent = 10
    progress_text = f"Uploading video... ({percent}%)"
    progress.progress(percent, text=progress_text)
    progress_percent.markdown(f"<b>{percent}%</b> - Uploading video...", unsafe_allow_html=True)

    # Save uploaded video to a temp file
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    tfile.close()

    # --- Stage 2: Extracting frames ---
    percent = 30
    progress_text = f"Extracting frames from video... ({percent}%)"
    progress.progress(percent, text=progress_text)
    progress_percent.markdown(f"<b>{percent}%</b> - Extracting frames...", unsafe_allow_html=True)

    cap = cv2.VideoCapture(tfile.name)
    frames = []
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    extracted = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % FRAME_INTERVAL == 0:
            frames.append(frame)
            extracted += 1
        frame_count += 1
        # Update progress bar during extraction
        if total_frames > 0 and frame_count % (FRAME_INTERVAL*2) == 0:
            percent = min(30 + int(40 * frame_count / total_frames), 70)
            progress.progress(percent, text=f"Extracting frames... ({percent}%)")
            progress_percent.markdown(f"<b>{percent}%</b> - Extracting frames...", unsafe_allow_html=True)

    cap.release()

    if len(frames) < 2:
        progress.empty()
        progress_percent.empty()
        st.warning("Not enough frames extracted to stitch. Please upload a longer video.")
    else:
        # --- Stage 3: Stitching ---
        percent = 80
        progress_text = f"Stitching frames into panorama... ({percent}%)"
        progress.progress(percent, text=progress_text)
        progress_percent.markdown(f"<b>{percent}%</b> - Stitching frames...", unsafe_allow_html=True)
        stitcher = cv2.Stitcher_create()
        status, pano = stitcher.stitch(frames)

        if status == cv2.Stitcher_OK:
            # --- Stage 4: Done ---
            percent = 100
            progress.progress(percent, text="Done!")
            progress_percent.markdown(f"<b>{percent}%</b> - Done!", unsafe_allow_html=True)
            # Convert BGR to RGB for displaying
            pano_rgb = cv2.cvtColor(pano, cv2.COLOR_BGR2RGB)
            st.image(pano_rgb, caption="Stitched Panorama", use_column_width=True)

            # Download button
            buf = BytesIO()
            is_success, im_buf_arr = cv2.imencode(".jpg", pano)
            if is_success:
                buf.write(im_buf_arr.tobytes())
                st.download_button(
                    label="Download Panorama",
                    data=buf.getvalue(),
                    file_name="panorama.jpg",
                    mime="image/jpeg"
                )
        else:
            progress.empty()
            progress_percent.empty()
            st.error(f"Error during stitching: {status}")

    # Clean up temp file
    os.remove(tfile.name)

# --- Footer ---
frontend.render_footer() 
