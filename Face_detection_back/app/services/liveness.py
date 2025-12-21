import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List
from app.config import get_settings
from app.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=settings.face_detection_confidence
)


def get_head_pose_yaw(frame_rgb: np.ndarray) -> Optional[float]:
    """
    Estimates head yaw using 2D landmark ratios.
    
    Args:
        frame_rgb: RGB numpy array of the frame.
        
    Returns:
        Float representing yaw ratio (1.0 = center, >1.5 = left, <0.6 = right),
        or None if face not detected.
    """
    try:
        results = face_mesh.process(frame_rgb)
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        h, w, _ = frame_rgb.shape
        
        nose = landmarks[1]
        left_ear_tragion = landmarks[234]
        right_ear_tragion = landmarks[454]
        
        nose_x = nose.x * w
        left_ear_x = left_ear_tragion.x * w
        right_ear_x = right_ear_tragion.x * w
        
        dist_nose_to_left = abs(nose_x - left_ear_x)
        dist_nose_to_right = abs(right_ear_x - nose_x)
        
        if dist_nose_to_right == 0:
            return 999.0
        
        ratio = dist_nose_to_left / dist_nose_to_right
        return ratio
    except Exception as e:
        logger.debug(f"Error computing head pose: {e}")
        return None


def check_liveness_pose(frames: List[np.ndarray]) -> Tuple[bool, str, dict]:
    """
    Validates liveness by checking for center-to-left head movement.
    
    Args:
        frames: List of RGB numpy arrays to analyze.
        
    Returns:
        Tuple of (is_live: bool, message: str, details: dict).
    """
    ratios = []
    
    for frame in frames:
        r = get_head_pose_yaw(frame)
        ratios.append(r)
            
    valid_ratios = [r for r in ratios if r is not None]
    
    if len(valid_ratios) < settings.liveness_min_valid_frames:
        logger.warning("Insufficient valid frames for liveness detection")
        return False, "Face not detected clearly. Move slower and ensure good lighting.", {"ratios": ratios}

    logger.debug(f"Detected 2D ratios: {[round(r, 2) for r in valid_ratios]}")
    
    if max(valid_ratios) < settings.liveness_center_ratio_min:
        logger.warning("Face not in center position for liveness")
        return False, "Start by looking straight.", {"ratios": ratios}

    min_ratio = min(valid_ratios)
    max_ratio = max(valid_ratios)
    
    if min_ratio < settings.liveness_left_turn_threshold or max_ratio > settings.liveness_mirror_threshold:
        logger.info("Liveness check passed")
        return True, "Liveness verified (Center -> Left).", {
            "min_ratio": min_ratio,
            "max_ratio": max_ratio,
            "ratios": ratios
        }
    else:
        logger.warning(f"Head turn not detected. Range: {round(min_ratio, 2)} to {round(max_ratio, 2)}")
        return False, f"Head turn LEFT not detected. Range: {round(min_ratio, 2)} to {round(max_ratio, 2)}", {
            "min_ratio": min_ratio,
            "max_ratio": max_ratio,
            "ratios": ratios
        }
        
