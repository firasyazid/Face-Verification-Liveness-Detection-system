from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import tempfile
import os
import shutil
import cv2
import numpy as np
from typing import Optional

from app.services.video_utils import extract_frames_from_video
from app.services.liveness import check_liveness_pose, get_head_pose_yaw
from app.services.face_matcher import verify_faces
from app.config import get_settings
from app.logger import get_logger
from app.models import VerificationResponse, ErrorResponse, LivenessResult, VerificationResult

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


@router.post("/verify_identity", response_model=Optional[VerificationResponse])
async def verify_identity(
    profile_image: UploadFile = File(...),
    live_video: UploadFile = File(...)
) -> dict:
    """
    Verifies user identity through liveness detection and face matching.
    
    Process:
    1. Extract frames from video
    2. Check liveness (center to left head movement)
    3. Verify face match with best center frame
    
    Args:
        profile_image: Reference profile image file
        live_video: Video file for liveness and verification
        
    Returns:
        Dictionary with verification status, liveness result, and face match result
    """
    tmp_profile_path: Optional[str] = None

    try:
        if not profile_image.filename or not live_video.filename:
            raise HTTPException(status_code=400, detail="Missing required files")

        suffix = os.path.splitext(profile_image.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_profile:
            tmp_profile_path = tmp_profile.name
            shutil.copyfileobj(profile_image.file, tmp_profile)

        logger.info(f"Processing profile image: {profile_image.filename}")
        
        frames = await extract_frames_from_video(live_video)
        if not frames:
            logger.error("Could not extract frames from video")
            raise HTTPException(status_code=400, detail="Could not extract frames from video")
            
        logger.info(f"Extracted {len(frames)} frames from video")
        
        is_live, message, details = check_liveness_pose(frames)
        
        if not is_live:
            logger.warning(f"Liveness check failed: {message}")
            return {
                "status": "failed",
                "liveness": {
                    "passed": False,
                    "message": message,
                    "details": details
                },
                "verification": {
                    "verified": False,
                    "distance": 1.0,
                    "threshold": settings.face_detection_threshold,
                    "model": settings.face_model,
                    "message": "Liveness check failed"
                }
            }
        
        logger.info("Liveness check passed")
        
        best_frame = frames[0]
        best_diff = 999.0
        
        for frame in frames:
            r = get_head_pose_yaw(frame)
            if r is not None:
                diff = abs(r - 1.0)
                if diff < best_diff:
                    best_diff = diff
                    best_frame = frame
                    if diff < 0.15:
                        break
        
        if settings.debug_mode:
            debug_dir = settings.debug_dir
            os.makedirs(debug_dir, exist_ok=True)
            shutil.copy(tmp_profile_path, os.path.join(debug_dir, "debug_profile.jpg"))
            cv2.imwrite(os.path.join(debug_dir, "debug_frame.jpg"), cv2.cvtColor(best_frame, cv2.COLOR_RGB2BGR))
        
        logger.info("Performing face verification")
        match_result = verify_faces(tmp_profile_path, best_frame)
        
        final_status = "success" if is_live and match_result["verified"] else "failed"
        
        logger.info(f"Verification completed with status: {final_status}")
        
        return {
            "status": final_status,
            "liveness": {
                "passed": is_live,
                "message": message,
                "details": details
            },
            "verification": match_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "error_code": "VERIFICATION_ERROR"
            }
        )

    finally:
        if tmp_profile_path and os.path.exists(tmp_profile_path):
            try:
                os.remove(tmp_profile_path)
            except Exception as e:
                logger.warning(f"Could not delete temp file: {e}")
