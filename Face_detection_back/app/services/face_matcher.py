from deepface import DeepFace
import cv2
import numpy as np
from app.config import get_settings
from app.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

try:
    DeepFace.build_model(settings.face_model)
    logger.info(f"{settings.face_model} model loaded successfully")
except Exception as e:
    logger.warning(f"Could not pre-load model: {e}")


def verify_faces(profile_path: str, live_frame_rgb: np.ndarray) -> dict:
    """
    Compares the profile image with a frame from the video.
    
    Args:
        profile_path: Path to the profile image file.
        live_frame_rgb: RGB numpy array of the video frame.
        
    Returns:
        Dictionary containing verification result with keys: verified, distance, 
        threshold, model, and optional error message.
    """
    live_frame_bgr = cv2.cvtColor(live_frame_rgb, cv2.COLOR_RGB2BGR)
    
    try:
        result = DeepFace.verify(
            img1_path=profile_path,
            img2_path=live_frame_bgr,
            model_name=settings.face_model,
            detector_backend=settings.face_detector_backend,
            distance_metric=settings.face_distance_metric,
            enforce_detection=False,
            threshold=settings.face_detection_threshold
        )
        
        logger.info(f"Face verification successful: verified={result['verified']}")
        return {
            "verified": result["verified"],
            "distance": result["distance"],
            "threshold": result["threshold"],
            "model": settings.face_model
        }
        
    except ValueError as e:
        logger.error(f"Face validation error: {e}")
        return {
            "verified": False,
            "error": str(e),
            "distance": 1.0,
            "message": "Face validation failed. Ensure face is clear and visible."
        }
    except Exception as e:
        logger.error(f"Unexpected verification error: {e}")
        return {
            "verified": False,
            "error": str(e),
            "distance": 1.0,
            "message": "Verification service error"
        }
