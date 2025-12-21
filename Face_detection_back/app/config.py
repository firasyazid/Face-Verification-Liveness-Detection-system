from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_title: str = "Face Verification & Liveness API"
    app_description: str = "API for verifying identity using FaceNet and MediaPipe Liveness Detection"
    app_version: str = "1.0.0"
    
    face_model: str = "Facenet512"
    face_detector_backend: str = "opencv"
    face_distance_metric: str = "cosine"
    face_detection_threshold: float = 0.50
    face_detection_confidence: float = 0.3
    
    liveness_min_valid_frames: int = 2
    liveness_center_ratio_min: float = 0.5
    liveness_center_ratio_max: float = 2.0
    liveness_left_turn_threshold: float = 0.50
    liveness_mirror_threshold: float = 1.5
    
    video_num_frames: int = 4
    video_temp_suffix: str = ".mp4"
    
    debug_mode: bool = False
    debug_dir: str = "debug_images"
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
