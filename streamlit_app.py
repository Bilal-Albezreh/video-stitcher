import streamlit as st
import cv2
import numpy as np
import tempfile
import os

st.title("Video Stitcher")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

FRAME_INTERVAL = 30  # extract one frame every 30 frames
SEGMENT_HOMOGRAPHY_THRESHOLD = 0.15  # threshold for starting a new segment (tune as needed)
MIN_SEGMENT_FRAMES = 2  # minimum frames per segment

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
        # --- Segment frames based on homography ---
        segments = []
        current_segment = [frames[0]]
        prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        for i in range(1, len(frames)):
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            # Detect ORB keypoints and descriptors
            orb = cv2.ORB_create()
            kp1, des1 = orb.detectAndCompute(prev_gray, None)
            kp2, des2 = orb.detectAndCompute(curr_gray, None)
            if des1 is not None and des2 is not None and len(kp1) > 10 and len(kp2) > 10:
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                matches = bf.match(des1, des2)
                matches = sorted(matches, key=lambda x: x.distance)
                if len(matches) > 10:
                    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    if H is not None:
                        # Check translation part of homography
                        dx = H[0, 2]
                        dy = H[1, 2]
                        translation = np.sqrt(dx**2 + dy**2)
                        if translation > SEGMENT_HOMOGRAPHY_THRESHOLD * max(frames[i].shape[:2]):
                            # Start new segment
                            if len(current_segment) >= MIN_SEGMENT_FRAMES:
                                segments.append(current_segment)
                            current_segment = [frames[i]]
                        else:
                            current_segment.append(frames[i])
                    else:
                        current_segment.append(frames[i])
                else:
                    current_segment.append(frames[i])
            else:
                current_segment.append(frames[i])
            prev_gray = curr_gray
        if len(current_segment) >= MIN_SEGMENT_FRAMES:
            segments.append(current_segment)
        
        if not segments:
            st.warning("No valid segments found for stitching.")
        else:
            for idx, segment in enumerate(segments):
                st.write(f"### Panorama for Segment {idx+1}")
                if len(segment) < 2:
                    st.warning("Not enough frames in this segment to stitch.")
                    continue
                stitcher = cv2.Stitcher_create()
                status, pano = stitcher.stitch(segment)
                if status == cv2.Stitcher_OK:
                    pano_rgb = cv2.cvtColor(pano, cv2.COLOR_BGR2RGB)
                    st.image(pano_rgb, caption=f"Stitched Panorama {idx+1}")
                else:
                    st.error(f"Error during stitching segment {idx+1}: {status}")
    
    # Clean up temp file
    os.remove(tfile.name) 
