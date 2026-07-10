import cv2
import os
import tempfile
from PIL import Image

def get_video_info(video_path):
    """
    Retrieves metadata about the video.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Could not open video file."}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    duration = total_frames / fps if fps > 0 else 0
    
    cap.release()
    
    return {
        "fps": fps,
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration": duration
    }

def extract_frames(video_path, interval_seconds=3.0, max_width=800):
    """
    Extracts frames from a video file at specified intervals.
    Returns a list of dictionaries, each containing:
    - 'image': PIL Image of the frame
    - 'timestamp': float, timestamp in seconds
    - 'timestamp_str': str, formatted timestamp (MM:SS)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file.")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if fps <= 0:
        fps = 30.0 # Default fallback
        
    duration = total_frames / fps
    
    frames = []
    
    # We want to extract a frame at 0s, Ns, 2Ns, etc.
    # We iterate over timestamps
    current_time = 0.0
    while current_time <= duration:
        frame_idx = int(current_time * fps)
        if frame_idx >= total_frames:
            break
            
        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        success, frame = cap.read()
        
        if not success:
            # If seeking failed or failed to read, try reading sequentially a bit or stop
            break
            
        # Convert BGR (OpenCV format) to RGB (PIL format)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_img = Image.fromarray(rgb_frame)
        
        # Resize preserving aspect ratio if width exceeds max_width
        w, h = pil_img.size
        if w > max_width:
            aspect_ratio = h / w
            new_w = max_width
            new_h = int(new_w * aspect_ratio)
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
        # Format timestamp
        mins = int(current_time // 60)
        secs = int(current_time % 60)
        timestamp_str = f"{mins:02d}:{secs:02d}"
        
        frames.append({
            "image": pil_img,
            "timestamp": current_time,
            "timestamp_str": timestamp_str
        })
        
        current_time += interval_seconds
        
    cap.release()
    return frames

def save_uploaded_file(uploaded_file):
    """
    Saves a Streamlit uploaded file to a temporary file path.
    """
    temp_dir = tempfile.gettempdir()
    # Get extension
    _, ext = os.path.splitext(uploaded_file.name)
    temp_path = os.path.join(temp_dir, f"temp_video_{os.urandom(4).hex()}{ext}")
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
        
    return temp_path
