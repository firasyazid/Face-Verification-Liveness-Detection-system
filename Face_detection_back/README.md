# Face Verification & Liveness Detection System

A complete identity verification solution combining facial recognition and liveness detection to prevent spoofing attacks. Built with FastAPI backend and React Native mobile app.

## 🎯 Features

### Core Functionality
- **Face Verification**: Compares profile photo against video frame using FaceNet512
- **Liveness Detection**: Validates user presence through head movement analysis
- **Anti-Spoofing**: Detects and blocks photo/video replay attacks
- **Real-time Processing**: Immediate verification results with detailed metrics

### Technical Features
- **FaceNet512 Embeddings**: Advanced face recognition model
- **MediaPipe Analysis**: 468-point facial landmark detection
- **Configurable Thresholds**: Fine-tune security vs usability
- **Comprehensive Logging**: Full audit trail and debugging
- **Type-Safe**: Full type hints throughout codebase
- **Clean Architecture**: Separated services, routers, and configuration

## 📦 Project Structure

```
Face_detection/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic schemas
│   ├── logger.py            # Logging setup
│   ├── routers/
│   │   └── verify.py        # Verification endpoint
│   └── services/
│       ├── face_matcher.py  # FaceNet face comparison
│       ├── liveness.py      # MediaPipe liveness detection
│       └── video_utils.py   # OpenCV frame extraction
├── requirements.txt         # Python dependencies
├── .env.example            # Configuration template
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── BACKEND_DOCUMENTATION.md # Detailed technical docs

face_detection_front/
├── screens/
│   ├── RegisterScreen.js    # Profile photo upload
│   ├── LivenessScreen.js    # Video recording & verification
│   └── ResultScreen.js      # Verification results
├── config.js               # API configuration
├── App.js                  # Main navigation
├── app.json                # Expo configuration
├── package.json            # Dependencies
├── README.md               # Frontend setup guide
└── .gitignore              # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.9+, pip
- **Frontend**: Node.js 14+, Expo CLI
- **System**: ffmpeg (for video processing)

### Backend Setup (5 minutes)

1. **Navigate to backend directory**
```bash
cd Face_detection
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure (Optional)**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend Setup (5 minutes)

1. **Navigate to frontend directory**
```bash
cd face_detection_front
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure backend URL**

Edit `app.json`:
```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://YOUR_BACKEND_IP:8000/verify_identity"
    }
  }
}
```

4. **Run app**
```bash
npx expo start
```

Scan QR code with Expo Go app on your device.

## 📋 API Documentation

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Identity Verification

```http
POST /verify_identity
Content-Type: multipart/form-data
```

**Request Parameters:**
- `profile_image` (file): JPEG photo of user's face
- `live_video` (file): MP4 video of user with head movement

**Response:**
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

## 🔄 Verification Workflow

### Step-by-Step Process

```
1. USER REGISTRATION
   ├─ Upload clear profile photo
   └─ Photo validated for quality

2. LIVENESS VIDEO RECORDING
   ├─ 3-second countdown
   ├─ Record 4-second video
   ├─ Perform head movement (center → left)
   └─ Video uploaded

3. BACKEND PROCESSING
   ├─ Extract 4 frames from video
   ├─ Analyze head movement (MediaPipe)
   │  └─ Calculate 2D head pose ratios
   ├─ Validate liveness requirements
   │  └─ Ensure center-to-left movement
   ├─ Select best centered frame
   └─ Compare with profile (FaceNet512)

4. FACE VERIFICATION
   ├─ Extract embeddings from both images
   ├─ Calculate cosine distance
   └─ Compare against threshold (0.50)

5. RESULT
   ├─ Success: status = "success"
   ├─ Failed: status = "failed" (with reason)
   └─ Error: status = "error" (technical issue)
```

## ⚙️ Configuration

### Backend Configuration (app/config.py)

**Face Detection:**
```python
face_model = "Facenet512"              # Recognition model
face_detector_backend = "opencv"       # Detection method
face_distance_metric = "cosine"        # Similarity metric
face_detection_threshold = 0.50        # Match threshold
face_detection_confidence = 0.3        # Detection confidence
```

**Liveness Detection:**
```python
liveness_min_valid_frames = 2          # Min frames required
liveness_center_ratio_min = 0.5        # Center check
liveness_center_ratio_max = 2.0        # Center check
liveness_left_turn_threshold = 0.50    # Left turn threshold
liveness_mirror_threshold = 1.5        # Mirror detection
```

**Video Processing:**
```python
video_num_frames = 4                   # Frames to extract
video_temp_suffix = ".mp4"             # Video format
debug_mode = false                     # Debug image saving
```

### Environment Variables (.env)

```env
DEBUG_MODE=false
LOG_LEVEL=INFO
FACE_DETECTION_THRESHOLD=0.50
LIVENESS_MIN_VALID_FRAMES=2
```

### Frontend Configuration (app.json)

```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://192.168.1.105:8000/verify_identity"
    }
  }
}
```

## 📊 How It Works

### Liveness Detection Algorithm

**Head Pose Estimation using MediaPipe:**

The system calculates a "yaw ratio" to determine head position:

```
ratio = distance(nose to left ear) / distance(nose to right ear)

ratio ≈ 1.0  → Face center (looking straight)
ratio > 1.5  → Face turned far left
ratio < 0.5  → Face turned right
```

**Liveness Check:**
1. Requires at least 2 valid frames
2. Face must start in center (ratio >= 0.5)
3. Must show movement to left (min_ratio < 0.50)
4. Detects mirrored attacks (ratio > 1.5)

### Face Verification

**FaceNet512 Embedding Comparison:**

1. Extract 512-dimensional vector from profile image
2. Extract 512-dimensional vector from video frame
3. Calculate cosine distance between vectors
4. Compare against threshold:
   - Distance < 0.50 → **MATCH** ✓
   - Distance >= 0.50 → **NO MATCH** ✗

## 🔒 Security Features

### Anti-Spoofing Measures
- **Liveness Detection**: Requires actual head movement
- **Mirror Detection**: Detects reversed videos
- **Real-time Processing**: No pre-recorded videos allowed
- **Movement Validation**: Specific head movement pattern required

### Input Validation
- File type validation (JPEG, MP4)
- Size limits on uploads
- Frame extraction validation
- Error handling without exposing internals

### Data Privacy
- Temporary files immediately deleted
- No face storage between requests
- Logs don't contain sensitive data
- HTTPS recommended for production

## 🛠️ Development

### Adding New Features

**Add Configuration:**
1. Edit `app/config.py`
2. Add to Settings class
3. Access via `settings.your_config`

**Add Logging:**
```python
from app.logger import get_logger

logger = get_logger(__name__)
logger.info("Your message")
```

**Add Type Hints:**
```python
def verify_faces(path: str, frame: np.ndarray) -> dict:
    pass
```

### Testing the API

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/verify_identity" \
  -F "profile_image=@profile.jpg" \
  -F "live_video=@video.mp4"
```

**Using Python:**
```python
import requests

files = {
    'profile_image': open('profile.jpg', 'rb'),
    'live_video': open('video.mp4', 'rb')
}
response = requests.post(
    'http://localhost:8000/verify_identity',
    files=files
)
print(response.json())
```

## 🐛 Troubleshooting

### Backend Issues

**Model Download Fails**
- Check internet connection
- Ensure sufficient disk space (2GB+)
- Check TensorFlow compatibility

**Face Not Detected**
- Ensure good lighting
- Face should be fully visible
- Try with different angle/distance
- Check `face_detection_confidence` setting

**Liveness Always Fails**
- Move head slowly (avoid jerky movement)
- Ensure face stays visible
- Complete center-to-left movement
- Try adjusting `liveness_left_turn_threshold`

**High False Rejection**
- Lower `face_detection_threshold` (e.g., 0.55)
- Improve lighting conditions
- Use clear, frontal photo

**High False Acceptance**
- Raise `face_detection_threshold` (e.g., 0.45)
- Require clearer liveness movement

### Frontend Issues

**Camera Not Working**
- Grant permissions when prompted
- Test with physical device (not emulator)
- Check device has camera hardware

**Connection Failed**
- Verify backend server is running
- Check IP address in `app.json`
- Ensure same network connection
- Check firewall settings

**Video Upload Timeout**
- Check network speed
- Reduce video size
- Increase timeout in LivenessScreen.js

**Liveness Check Fails**
- Move head slowly
- Keep face visible throughout
- Avoid side angles
- Ensure good lighting

## 📚 Documentation

- **BACKEND_DOCUMENTATION.md** - Detailed technical explanation of all services
- **Backend README.md** - Backend-specific setup
- **Frontend README.md** - Frontend-specific setup

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI, Uvicorn
- **Face Recognition**: DeepFace (FaceNet512)
- **Pose Detection**: MediaPipe
- **Video Processing**: OpenCV, NumPy
- **Data Validation**: Pydantic, Pydantic Settings
- **Logging**: Python logging module

### Frontend
- **Framework**: React Native, Expo
- **HTTP Client**: Axios
- **Camera**: Expo Camera
- **Image Picker**: Expo Image Picker
- **State Management**: React Hooks

## 📈 Performance

- **Model Preload**: ~5 seconds startup
- **Verification**: ~3-5 seconds per request
- **Frame Extraction**: ~1 second for 4 frames
- **Memory Usage**: ~500MB (includes TensorFlow)

## 🚀 Deployment

### Docker (Backend)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t face-detection .
docker run -p 8000:8000 face-detection
```

### Production Checklist

- [ ] Set `DEBUG_MODE=false`
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/TLS
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Use proper database for profile storage
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation
- [ ] Test with real devices
- [ ] Set up CI/CD pipeline

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check BACKEND_DOCUMENTATION.md for detailed explanations
2. Review troubleshooting section
3. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - System information
   - Logs

## 🎓 Learning Resources

- [FaceNet Paper](https://arxiv.org/abs/1503.03832)
- [MediaPipe Face Detection](https://mediapipe.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Native Docs](https://reactnative.dev/)

## 🔄 Project Status

- ✅ Core verification working
- ✅ Liveness detection stable
- ✅ Frontend mobile app functional
- ✅ Full documentation
- 🔄 Production deployment testing
- 📋 Multi-face detection (planned)
- 📋 Database integration (planned)
- 📋 Batch verification (planned)

---

**Last Updated**: December 2025
**Version**: 1.0.0
