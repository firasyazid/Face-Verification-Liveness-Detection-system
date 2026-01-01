"""Unit tests for configuration module."""
import pytest
from app.config import Settings, get_settings


class TestSettings:
    """Test cases for Settings configuration."""

    def test_settings_default_values(self):
        """Test that settings have correct default values."""
        settings = Settings()
        
        assert settings.app_title == "Face Verification & Liveness API"
        assert settings.app_version == "1.0.0"
        assert settings.face_model == "Facenet512"
        assert settings.face_detector_backend == "opencv"
        assert settings.face_distance_metric == "cosine"

    def test_face_detection_thresholds(self):
        """Test face detection threshold values."""
        settings = Settings()
        
        assert settings.face_detection_threshold == 0.50
        assert settings.face_detection_confidence == 0.3
        assert 0.0 <= settings.face_detection_threshold <= 1.0
        assert 0.0 <= settings.face_detection_confidence <= 1.0

    def test_liveness_configuration(self):
        """Test liveness detection configuration."""
        settings = Settings()
        
        assert settings.liveness_min_valid_frames == 2
        assert settings.liveness_center_ratio_min == 0.5
        assert settings.liveness_center_ratio_max == 2.0
        assert settings.liveness_left_turn_threshold == 0.50
        assert settings.liveness_mirror_threshold == 1.5

    def test_video_configuration(self):
        """Test video processing configuration."""
        settings = Settings()
        
        assert settings.video_num_frames == 4
        assert settings.video_temp_suffix == ".mp4"
        assert settings.video_num_frames > 0

    def test_debug_configuration(self):
        """Test debug mode configuration."""
        settings = Settings()
        
        assert settings.debug_mode is False
        assert settings.debug_dir == "debug_images"
        assert settings.log_level == "INFO"

    def test_get_settings_cached(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2

    def test_settings_immutable_after_creation(self):
        """Test settings behavior."""
        settings = Settings()
        
        assert hasattr(settings, 'face_model')
        assert hasattr(settings, 'app_version')

    def test_custom_settings_override(self):
        """Test that custom values can override defaults."""
        custom_settings = Settings(
            face_detection_threshold=0.60,
            liveness_min_valid_frames=3
        )
        
        assert custom_settings.face_detection_threshold == 0.60
        assert custom_settings.liveness_min_valid_frames == 3
