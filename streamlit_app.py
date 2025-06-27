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
                    st.warning(f"Stitching failed for segment {idx+1}, attempting optical flow mosaic...")
                    FLOW_MAG_THRESHOLD = 8.0  # Tune this value as needed
                    base = segment[0].copy()
                    h, w = base.shape[:2]
                    canvas = np.zeros_like(base, dtype=np.float32)
                    mask = np.zeros((h, w), dtype=np.float32)
                    canvas[:,:,:] = base[:,:,:]
                    mask[:,:] = 1.0
                    prev_gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
                    mosaic_success = False
                    for f in segment[1:]:
                        curr_gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
                        flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
                        avg_mag = np.mean(mag)
                        if avg_mag > FLOW_MAG_THRESHOLD:
                            prev_gray = curr_gray
                            continue  # Skip this frame
                        # Warp current frame to base using flow
                        h_idx, w_idx = np.mgrid[0:h, 0:w].astype(np.float32)
                        map_x = w_idx + flow[:,:,0]
                        map_y = h_idx + flow[:,:,1]
                        warped = cv2.remap(f, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
                        # Blend warped frame onto canvas
                        alpha = 0.5
                        canvas = cv2.addWeighted(canvas, 1-alpha, warped.astype(np.float32), alpha, 0)
                        prev_gray = curr_gray
                        mosaic_success = True
                    if mosaic_success:
                        mosaic = np.clip(canvas, 0, 255).astype(np.uint8)
                        mosaic_rgb = cv2.cvtColor(mosaic, cv2.COLOR_BGR2RGB)
                        st.image(mosaic_rgb, caption=f"Optical Flow Mosaic {idx+1}")
                    else:
                        st.warning(f"Optical flow mosaic also failed for segment {idx+1}, attempting pushbroom/strip panorama...")
                        # Pushbroom/strip panorama fallback
                        strip_height = 10  # Number of rows to extract from each frame
                        strips = []
                        for frame in segment:
                            center = h // 2
                            strip = frame[center - strip_height//2:center + strip_height//2, :, :]
                            strips.append(strip)
                        if strips:
                            panorama = np.vstack(strips)
                            panorama_rgb = cv2.cvtColor(panorama, cv2.COLOR_BGR2RGB)
                            st.image(panorama_rgb, caption=f"Pushbroom Strip Panorama {idx+1}")
                        else:
                            st.error(f"All stitching methods failed for segment {idx+1}.")
    
    # Clean up temp file
    os.remove(tfile.name) 
