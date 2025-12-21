# Face Verification & Liveness Detection Backend - Technical Documentation

## Overview

This is a FastAPI-based backend service that verifies user identity through two sequential checks:
1. **Liveness Detection**: Ensures the user is a real person (not a photo/video)
2. **Face Verification**: Confirms the face matches the profile image

## Project Structure

```
app/
├── main.py              # Application entry point & API setup
├── config.py            # Configuration management
├── models.py            # Pydantic request/response schemas
├── logger.py            # Logging configuration
├── routers/
│   └── verify.py        # Identity verification endpoint
└── services/
    ├── face_matcher.py  # FaceNet512 face comparison logic
    ├── liveness.py      # MediaPipe liveness detection
    └── video_utils.py   # Video frame extraction
```

## Core Components

### 1. **main.py** - Application Entry Point

```python
# Initializes FastAPI app with configuration
# Includes error handling and health check endpoints
```

**Key Responsibilities:**
- Creates FastAPI application instance
- Registers routers (API endpoints)
- Sets up global exception handler
- Provides health check endpoint

**Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check

---

### 2. **config.py** - Configuration Management

Centralized configuration using Pydantic Settings. All hardcoded values are defined here:

**Face Detection Settings:**
- `face_model`: "Facenet512" - Neural network model for embedding extraction
- `face_detector_backend`: "opencv" - Face detection algorithm
- `face_distance_metric`: "cosine" - Similarity measurement method
- `face_detection_threshold`: 0.50 - Match threshold (< 0.50 = same person)
- `face_detection_confidence`: 0.3 - Detection confidence minimum

**Liveness Settings:**
- `liveness_min_valid_frames`: 2 - Minimum frames required
- `liveness_center_ratio_min`: 0.5 - Maximum centered position ratio
- `liveness_center_ratio_max`: 2.0 - Maximum off-center position ratio
- `liveness_left_turn_threshold`: 0.50 - Head turn left threshold
- `liveness_mirror_threshold`: 1.5 - Mirror/spoofing detection threshold

**Video Processing:**
- `video_num_frames`: 4 - Frames extracted from video
- `video_temp_suffix`: ".mp4" - Expected video format

Can be overridden via environment variables or `.env` file.

---

### 3. **models.py** - Data Validation Schemas

Pydantic models for request/response validation:

**LivenessResult**
```python
{
    "passed": bool,
    "message": str,
    "details": dict
}
```

**VerificationResult**
```python
{
    "verified": bool,
    "distance": float,          # 0-1 cosine distance
    "threshold": float,
    "model": "Facenet512",
    "error": str (optional),
    "message": str (optional)
}
```

**VerificationResponse**
```python
{
    "status": "success|failed|error",
    "liveness": LivenessResult,
    "verification": VerificationResult
}
```

---

### 4. **logger.py** - Logging Setup

Structured logging configuration for debugging and monitoring.

**Log Levels:**
- DEBUG: Detailed information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages

**Usage:**
```python
logger = get_logger(__name__)
logger.info("User verification started")
logger.error("Face detection failed", exc_info=True)
```

---

## Service Layer

### 5. **services/face_matcher.py** - Face Verification

Compares two face images using FaceNet512 embeddings.

**How it works:**

1. **Model Loading** (at startup)
   ```
   DeepFace.build_model("Facenet512")
   - Downloads model on first run
   - Cached for subsequent requests
   ```

2. **Face Verification Process**
   ```
   Input: Profile image path + Video frame (RGB numpy array)
   
   Step 1: Convert frame from RGB to BGR (OpenCV format)
   Step 2: Extract face embeddings from both images
   Step 3: Calculate cosine distance between embeddings
   Step 4: Compare against threshold (0.50)
   
   Output: {verified: bool, distance: float}
   ```

**Key Parameters:**
- `distance_metric`: "cosine" (0 = identical, 1 = completely different)
- `threshold`: 0.50 (genuine match typically < 0.50)
- `enforce_detection`: False (allows graceful failures)

**Error Handling:**
- ValueError: Face detection issues → returns `verified: False`
- Exception: Unexpected errors → logged and handled gracefully

---

### 6. **services/liveness.py** - Liveness Detection

Prevents spoofing attacks using head pose analysis with MediaPipe.

**How it works:**

1. **Head Pose Estimation**
   ```
   Input: RGB video frame
   
   Uses MediaPipe Face Mesh to detect 468 facial landmarks
   - Landmark 1: Nose tip
   - Landmark 234: Left ear tragion
   - Landmark 454: Right ear tragion
   
   Calculates yaw ratio:
   ratio = distance(nose to left ear) / distance(nose to right ear)
   ```

2. **Yaw Ratio Interpretation**
   ```
   ratio ≈ 1.0  → Face center (looking straight)
   ratio > 1.5  → Face turned far left
   ratio < 0.5  → Face turned right
   ```

3. **Liveness Check Logic**
   ```
   Requirements: Must have at least 2 valid frames
   
   Step 1: Check if face starts in center
          max(ratios) >= 0.5
          
   Step 2: Check for head movement (left turn)
          min(ratio) < 0.50 OR max(ratio) > 1.5
          
   Result: True if both checks pass
   ```

**Anti-Spoofing Features:**
- Requires actual head movement (not static photo)
- Detects mirror/reversed videos (ratio > 1.5)
- Requires adequate frames for validation
- Face must be clearly detected (confidence > 0.3)

**Flow Example:**
```
Frame 1: ratio = 0.95 (center) ✓
Frame 2: ratio = 1.02 (center) ✓
Frame 3: ratio = 0.42 (left turn) ✓
Frame 4: ratio = 0.38 (further left) ✓

Result: Liveness PASSED
```

---

### 7. **services/video_utils.py** - Video Processing

Extracts evenly-spaced frames from uploaded video.

**Process:**

1. **Save to Temp File**
   ```
   Input: UploadFile from FastAPI
   → Save to temporary location
   → OpenCV reads from disk (not in-memory)
   ```

2. **Frame Extraction**
   ```
   Input: Video file, num_frames=4
   
   Step 1: Open video with OpenCV
   Step 2: Get total frame count
   Step 3: Calculate evenly-spaced frame indices
           indices = [0, total/3, 2*total/3, total-2]
   Step 4: Extract frames at each index
   Step 5: Auto-rotate if landscape (mobile videos)
   Step 6: Convert BGR → RGB (for MediaPipe/DeepFace)
   ```

3. **Auto-Rotation**
   ```
   Most mobile videos lose rotation metadata
   If width > height (landscape):
   → Rotate 90° clockwise to portrait
   ```

4. **Cleanup**
   ```
   Temporary video file deleted after processing
   ```

**Output:** List of RGB numpy arrays ready for processing

---

## Router Layer

### 8. **routers/verify.py** - API Endpoint

Main endpoint handling the complete verification flow.

**Endpoint: `POST /verify_identity`**

```
Input (multipart/form-data):
- profile_image: JPEG image file
- live_video: MP4 video file

Output (JSON):
{
  "status": "success|failed|error",
  "liveness": {...},
  "verification": {...}
}
```

**Complete Flow:**

```
1. INPUT VALIDATION
   ├─ Check files are provided
   └─ Create temporary profile image

2. VIDEO PROCESSING
   ├─ Extract 4 frames from video
   └─ Validate frames extracted successfully

3. LIVENESS DETECTION
   ├─ Analyze head movement in frames
   ├─ If FAILED → Return early with failure
   └─ If PASSED → Continue to verification

4. FIND BEST FRAME
   ├─ For each frame, calculate head pose ratio
   ├─ Find frame closest to ratio 1.0 (centered)
   └─ Early exit if ratio < 0.15

5. FACE VERIFICATION
   ├─ Compare profile image with best frame
   └─ Get match distance and threshold

6. FINAL RESULT
   ├─ status = "success" if liveness AND verified
   ├─ status = "failed" if either check fails
   └─ status = "error" if exception occurs

7. CLEANUP
   └─ Delete temporary profile image
```

**Response Examples:**

Success:
```json
{
  "status": "success",
  "liveness": {
    "passed": true,
    "message": "Liveness verified (Center -> Left).",
    "details": {
      "min_ratio": 0.38,
      "max_ratio": 1.05,
      "ratios": [0.95, 1.02, 0.42, 0.38]
    }
  },
  "verification": {
    "verified": true,
    "distance": 0.35,
    "threshold": 0.50,
    "model": "Facenet512"
  }
}
```

Failed (Liveness):
```json
{
  "status": "failed",
  "liveness": {
    "passed": false,
    "message": "Head turn LEFT not detected.",
    "details": {
      "min_ratio": 0.98,
      "max_ratio": 1.05,
      "ratios": [0.95, 1.02, 0.98, 1.05]
    }
  },
  "verification": {
    "verified": false,
    "distance": 1.0,
    "threshold": 0.50,
    "model": "Facenet512",
    "message": "Liveness check failed"
  }
}
```

---

## Data Flow Diagram

```
CLIENT REQUEST
    ↓
[POST /verify_identity]
    ├─ profile_image (JPEG)
    └─ live_video (MP4)
    ↓
ROUTE HANDLER (verify.py)
    ↓
[VIDEO PROCESSING]
→ video_utils.py: Extract 4 RGB frames
    ↓
[LIVENESS CHECK]
→ liveness.py: Analyze head movement
    │
    ├─ If FAILED → Return failure response
    │
    └─ If PASSED → Continue
    ↓
[FIND BEST FRAME]
→ liveness.py: Find most centered frame
    ↓
[FACE VERIFICATION]
→ face_matcher.py: Compare embeddings
    ↓
[BUILD RESPONSE]
→ Combine liveness + verification results
    ↓
CLIENT RESPONSE (JSON)
```

---

## Technology Stack

**Framework:**
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server

**Computer Vision:**
- **DeepFace** - Face recognition library
  - Uses FaceNet512 model
  - Handles face detection & embedding
- **MediaPipe** - Real-time perception framework
  - Face mesh detection
  - 468 facial landmarks

**Image Processing:**
- **OpenCV** - Video frame extraction and color space conversion
- **NumPy** - Array operations and image manipulation

**Data Validation:**
- **Pydantic** - Request/response validation
- **Pydantic Settings** - Environment configuration

---

## Workflow Example: Successful Verification

```
1. User uploads:
   - Profile image: clear frontal face photo
   - Liveness video: 4-second video, head movement from center to left

2. Video Processing:
   Frame 1 (0s):   ratio = 0.98 (center)
   Frame 2 (1.3s): ratio = 1.01 (center)
   Frame 3 (2.7s): ratio = 0.45 (left turn)
   Frame 4 (4s):   ratio = 0.38 (far left)

3. Liveness Check:
   ✓ min(ratios) = 0.38 < 0.50 (LEFT TURN DETECTED)
   ✓ max(ratios) = 1.01 > 0.5 (STARTED IN CENTER)
   Result: PASSED

4. Best Frame Selection:
   Frame 1 diff = 0.02 (BEST - closest to 1.0) ← Selected
   Frame 2 diff = 0.01
   Frame 3 diff = 0.55
   Frame 4 diff = 0.62

5. Face Verification:
   Profile embedding ──┐
                       → Cosine distance = 0.35
   Frame 1 embedding ─┘
   
   0.35 < 0.50 (threshold) → MATCH ✓

6. Final Response:
   {
     "status": "success",
     "liveness": { "passed": true, ... },
     "verification": { "verified": true, "distance": 0.35 }
   }
```

---

## Error Scenarios

### Scenario 1: Liveness Check Fails
```
User records video without moving head

Frame ratios: [0.98, 0.99, 0.98, 0.99]
min = 0.98, max = 0.99

min(0.98) > 0.50? NO → No left turn detected
Result: LIVENESS FAILED
```

### Scenario 2: Face Not Detected
```
Profile image is blurry/face not clear

DeepFace throws ValueError
→ Caught and logged
→ Returns: verified = False, error message
```

### Scenario 3: Video File Issues
```
Video file is corrupted/not readable

OpenCV.VideoCapture fails
→ return [] (empty frames)
→ Caught in verify.py
→ Returns HTTP 400 error
```

---

## Performance Optimizations

1. **Model Pre-loading**
   - FaceNet512 loaded at startup
   - Avoids download delay on first request

2. **Frame Selection**
   - Extracts only 4 frames (not entire video)
   - Early exit if perfect center frame found

3. **Efficient Processing**
   - NumPy arrays for fast computation
   - Cosine distance is O(n) operation

4. **Temporary File Management**
   - Video saved temporarily (not in memory)
   - Cleaned up immediately after processing

---

## Security Considerations

1. **Input Validation**
   - File type checking
   - Size limits recommended

2. **Temporary File Safety**
   - Files deleted in finally block
   - Even if errors occur

3. **Liveness Detection**
   - Prevents static photo attacks
   - Detects mirror/reversed videos
   - Requires actual movement

4. **Error Messages**
   - Don't expose system details
   - User-friendly error responses

---

## Configuration & Deployment

**Environment Variables (.env):**
```
DEBUG_MODE=false
LOG_LEVEL=INFO
FACE_DETECTION_THRESHOLD=0.50
LIVENESS_MIN_VALID_FRAMES=2
```

**Running the Server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Dependencies

See `requirements.txt` for complete list:
- fastapi
- uvicorn
- tensorflow
- deepface
- mediapipe
- opencv-python
- numpy
- pydantic-settings

---

## Troubleshooting

**Issue: Model download fails**
- Solution: Check internet connection, ensure sufficient disk space

**Issue: Face not detected**
- Solution: Ensure good lighting, face clearly visible

**Issue: Liveness always fails**
- Solution: Adjust thresholds in config.py

**Issue: High false rejection rate**
- Solution: Lower `face_detection_threshold` (e.g., 0.55)

**Issue: High false acceptance rate**
- Solution: Raise `face_detection_threshold` (e.g., 0.45)

---

## Future Enhancements

- [ ] Multi-face detection
- [ ] Anti-spoofing detection (liveness confidence score)
- [ ] Batch verification API
- [ ] Database integration for profile storage
- [ ] Face enrollment/registration endpoint
- [ ] Document verification
- [ ] Iris/fingerprint addition
