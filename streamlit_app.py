import streamlit as st
import cv2
import numpy as np
import tempfile
import os

st.title("Video Stitcher Demo")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

# --- User Controls ---
st.sidebar.header("Extraction Settings")
FRAME_INTERVAL = st.sidebar.slider("Frame Interval", min_value=5, max_value=120, value=30, step=5)
SHARPNESS_THRESHOLD = st.sidebar.slider("Sharpness Threshold", min_value=10, max_value=500, value=100, step=10)
SEGMENT_HIST_DIFF = st.sidebar.slider("Scene Change Sensitivity", min_value=0.01, max_value=0.5, value=0.15, step=0.01)

if uploaded_file:
    # Save uploaded video to a temp file
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    tfile.close()
    
    cap = cv2.VideoCapture(tfile.name)
    
    frames = []
    sharpness_vals = []
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    st.info("Extracting frames...")
    progress = st.progress(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % FRAME_INTERVAL == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_vals.append(sharpness)
            if sharpness >= SHARPNESS_THRESHOLD:
                frames.append(frame)
        frame_count += 1
        if total_frames > 0:
            progress.progress(min(frame_count / total_frames, 1.0))
    cap.release()
    progress.empty()
    st.write(f"Extracted {len(frames)} sharp frames out of {frame_count} total frames.")
    if len(frames) < 2:
        st.warning("Not enough sharp frames extracted to stitch. Please upload a longer or higher quality video, or lower the sharpness threshold.")
    else:
        # --- Scene Segmentation (Histogram-based) ---
        st.info("Segmenting video into scenes...")
        segments = []
        current_segment = [frames[0]]
        prev_hist = cv2.calcHist([cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)], [0], None, [64], [0,256])
        prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()
        for i in range(1, len(frames)):
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            curr_hist = cv2.calcHist([curr_gray], [0], None, [64], [0,256])
            curr_hist = cv2.normalize(curr_hist, curr_hist).flatten()
            hist_diff = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_BHATTACHARYYA)
            if hist_diff > SEGMENT_HIST_DIFF:
                if len(current_segment) > 1:
                    segments.append(current_segment)
                current_segment = [frames[i]]
            else:
                current_segment.append(frames[i])
            prev_hist = curr_hist
        if len(current_segment) > 1:
            segments.append(current_segment)
        if not segments:
            st.warning("No valid segments found for stitching.")
        else:
            st.success(f"Found {len(segments)} scene segment(s). Attempting stitching...")
            for idx, segment in enumerate(segments):
                st.write(f"### Panorama for Segment {idx+1}")
                if len(segment) < 2:
                    st.warning("Not enough frames in this segment to stitch.")
                    continue
                # --- Try OpenCV Stitcher ---
                stitcher = cv2.Stitcher_create()
                status, pano = stitcher.stitch(segment)
                if status == cv2.Stitcher_OK:
                    pano_rgb = cv2.cvtColor(pano, cv2.COLOR_BGR2RGB)
                    st.image(pano_rgb, caption=f"Stitched Panorama {idx+1}")
                    continue
                # --- Fallback: Pairwise Warping/Blending ---
                st.warning(f"OpenCV stitcher failed for segment {idx+1}, trying pairwise blending...")
                try:
                    base = segment[0].copy()
                    for f in segment[1:]:
                        gray1 = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
                        gray2 = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
                        orb = cv2.ORB_create()
                        kp1, des1 = orb.detectAndCompute(gray1, None)
                        kp2, des2 = orb.detectAndCompute(gray2, None)
                        if des1 is not None and des2 is not None and len(kp1) > 10 and len(kp2) > 10:
                            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                            matches = bf.match(des1, des2)
                            if len(matches) > 10:
                                src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                                dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                                H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
                                if H is not None:
                                    warped = cv2.warpPerspective(f, H, (base.shape[1], base.shape[0]))
                                    mask_warped = (cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY) > 0).astype(np.uint8)
                                    base = np.where(mask_warped[...,None], warped, base)
                    base_rgb = cv2.cvtColor(base, cv2.COLOR_BGR2RGB)
                    st.image(base_rgb, caption=f"Pairwise Blended Panorama {idx+1}")
                    continue
                except Exception as e:
                    st.warning(f"Pairwise blending failed: {e}")
                # --- Fallback: Optical Flow Mosaic ---
                st.warning(f"Trying optical flow mosaic for segment {idx+1}...")
                try:
                    base = segment[0].copy()
                    h, w = base.shape[:2]
                    canvas = np.zeros_like(base, dtype=np.float32)
                    mask = np.zeros((h, w), dtype=np.float32)
                    canvas[:,:,:] = base[:,:,:]
                    mask[:,:] = 1.0
                    prev_gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
                    for f in segment[1:]:
                        curr_gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
                        flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
                        avg_mag = np.mean(mag)
                        if avg_mag > 8.0:
                            prev_gray = curr_gray
                            continue
                        h_idx, w_idx = np.mgrid[0:h, 0:w].astype(np.float32)
                        map_x = w_idx + flow[:,:,0]
                        map_y = h_idx + flow[:,:,1]
                        warped = cv2.remap(f, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
                        alpha = 0.5
                        canvas = cv2.addWeighted(canvas, 1-alpha, warped.astype(np.float32), alpha, 0)
                        prev_gray = curr_gray
                    mosaic = np.clip(canvas, 0, 255).astype(np.uint8)
                    mosaic_rgb = cv2.cvtColor(mosaic, cv2.COLOR_BGR2RGB)
                    st.image(mosaic_rgb, caption=f"Optical Flow Mosaic {idx+1}")
                except Exception as e:
                    st.error(f"All stitching methods failed for segment {idx+1}: {e}")
    os.remove(tfile.name) 
