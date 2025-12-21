import cv2
import numpy as np
import os
import tempfile
from fastapi import UploadFile
from typing import List
from app.config import get_settings
from app.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


async def extract_frames_from_video(video_file: UploadFile, num_frames: int = None) -> List[np.ndarray]:
    """
    Extracts evenly spaced frames from an uploaded video file.
    
    Args:
        video_file: FastAPI UploadFile object.
        num_frames: Number of frames to extract. Uses config value if not specified.
        
    Returns:
        List of RGB numpy arrays, or empty list if extraction fails.
    """
    if num_frames is None:
        num_frames = settings.video_num_frames
    
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=settings.video_temp_suffix) as temp_file:
            temp_path = temp_file.name
            contents = await video_file.read()
            temp_file.write(contents)
        
        cap = cv2.VideoCapture(temp_path)
        
        if not cap.isOpened():
            logger.error("Could not open video file")
            return []

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            logger.error("Video has no frames or is unreadable")
            return []

        frames = []
        indices = np.linspace(0, total_frames - 2, num_frames, dtype=int)
        
        for i in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                if w > h:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
        
        logger.info(f"Extracted {len(frames)} frames from video")
        cap.release()
        return frames

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        return []
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Could not delete temp file: {e}")
