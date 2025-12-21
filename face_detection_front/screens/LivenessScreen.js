import { useState, useRef } from 'react';
import {
    StyleSheet,
    View,
    Text,
    TouchableOpacity,
    Alert,
    SafeAreaView,
    ActivityIndicator,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import axios from 'axios';
import API_URL from '../config';

export default function LivenessScreen({ userData, onComplete }) {
    const [permission, requestPermission] = useCameraPermissions();
    const [phase, setPhase] = useState('ready');
    const [countdown, setCountdown] = useState(3);
    const [isCameraReady, setIsCameraReady] = useState(false);
    const cameraRef = useRef(null);

    const startRecording = async () => {
        if (!isCameraReady || !cameraRef.current) {
            Alert.alert('Please wait', 'Camera is initializing...');
            return;
        }
        setPhase('countdown');
        let count = 3;
        setCountdown(count);

        const interval = setInterval(() => {
            count--;
            setCountdown(count);
            if (count === 0) {
                clearInterval(interval);
                beginRecording();
            }
        }, 1000);
    };

    const beginRecording = async () => {
        setPhase('recording');

        try {
            if (!cameraRef.current) {
                throw new Error('Camera not ready');
            }

            const video = await cameraRef.current.recordAsync({ maxDuration: 4 });
            
            if (!video || !video.uri) {
                throw new Error('Video recording failed - no output file');
            }
            
            await uploadVideo(video.uri);
        } catch (error) {
            console.error('Recording error:', error.message);
            Alert.alert(
                'Recording Failed',
                error.message || 'Failed to record video. Please try again.',
                [{ text: 'Retry', onPress: () => setPhase('ready') }]
            );
            setPhase('ready');
        }
    };

    const uploadVideo = async (videoUri) => {
        setPhase('uploading');

        try {
            const formData = new FormData();

            formData.append('profile_image', {
                uri: userData.profileImage.uri,
                type: 'image/jpeg',
                name: 'profile.jpg',
            });

            formData.append('live_video', {
                uri: videoUri,
                type: 'video/mp4',
                name: 'liveness.mp4',
            });

            const response = await axios.post(API_URL, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 120000,
            });

            console.log('Verification Response:', JSON.stringify(response.data, null, 2));

            onComplete(response.data);
        } catch (error) {
            console.error('Upload Error:', error);
            Alert.alert(
                'Verification Failed',
                error.response?.data?.message || error.message,
                [{ text: 'Retry', onPress: () => setPhase('ready') }]
            );
        }
    };

    if (!permission) {
        return (
            <View style={styles.container}>
                <Text>Requesting camera permissions...</Text>
            </View>
        );
    }

    if (!permission.granted) {
        return (
            <View style={styles.container}>
                <Text style={styles.errorText}>Camera and microphone permissions are required</Text>
                <TouchableOpacity 
                    onPress={requestPermission} 
                    style={styles.startButton}
                >
                    <Text style={styles.startButtonText}>Grant Permissions</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <CameraView
                style={styles.camera}
                facing="front"
                mode="video"
                ref={cameraRef}
                onCameraReady={() => setIsCameraReady(true)}
            />

            <View style={styles.overlayContainer}>
                {phase === 'instructions' && (
                    <View style={styles.instructionsBox}>
                        <Text style={styles.instructionsTitle}>Liveness Check</Text>
                        <Text style={styles.instructionsText}>
                            To verify you're a real person (not a photo or video), we need you to:
                        </Text>
                        <View style={styles.stepContainer}>
                            <View style={styles.step}>
                                <Text style={styles.stepNumber}>1</Text>
                                <Text style={styles.stepText}>Look straight at the camera</Text>
                            </View>
                            <View style={styles.step}>
                                <Text style={styles.stepNumber}>2</Text>
                                <Text style={styles.stepText}>Slowly turn your head LEFT</Text>
                            </View>
                        </View>
                        <Text style={styles.securityNote}>
                            🔒 This prevents spoofing attacks
                        </Text>
                    </View>
                )}

                {phase === 'countdown' && (
                    <View style={styles.countdownBox}>
                        <Text style={styles.countdownText}>{countdown}</Text>
                    </View>
                )}

                {phase === 'recording' && (
                    <View style={styles.recordingBox}>
                        <ActivityIndicator color="#fff" />
                        <Text style={styles.recordingText}>Recording... Turn Left</Text>
                    </View>
                )}

                {phase === 'uploading' && (
                    <View style={styles.uploadingBox}>
                        <ActivityIndicator size="large" color="#4CAF50" />
                        <Text style={styles.uploadingText}>Verifying...</Text>
                    </View>
                )}
            </View>

            {phase === 'ready' && (
                <TouchableOpacity
                    style={[styles.startButton, !isCameraReady && { opacity: 0.5 }]}
                    onPress={startRecording}
                    disabled={!isCameraReady}
                >
                    <Text style={styles.startButtonText}>
                        {isCameraReady ? 'Start Verification' : 'Initializing...'}
                    </Text>
                </TouchableOpacity>
            )}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#000',
    },
    camera: {
        flex: 1,
        width: '100%',
    },
    overlayContainer: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: 'transparent',
    },
    overlay: {
        flex: 1,
        backgroundColor: 'transparent',
        justifyContent: 'center',
        alignItems: 'center',
    },
    instructionsBox: {
        backgroundColor: 'rgba(0, 0, 0, 0.6)', // Darker blur
        paddingHorizontal: 30,
        paddingVertical: 40,
        borderRadius: 24,
        marginHorizontal: 32,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)',
    },
    instructionsTitle: {
        color: '#fff',
        fontSize: 28,
        fontWeight: '800', // Extra bold
        marginBottom: 20,
        textAlign: 'center',
        letterSpacing: 0.5,
    },
    instructionsText: {
        color: 'rgba(255,255,255,0.9)',
        fontSize: 16,
        lineHeight: 24,
        textAlign: 'center',
        fontWeight: '500',
        marginBottom: 20,
    },
    stepContainer: {
        width: '100%',
        marginTop: 10,
    },
    step: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255,255,255,0.1)',
        padding: 16,
        borderRadius: 12,
        marginBottom: 12,
    },
    stepNumber: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: '#4CAF50',
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
        textAlign: 'center',
        lineHeight: 36,
        marginRight: 16,
    },
    stepText: {
        flex: 1,
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    securityNote: {
        color: 'rgba(255,255,255,0.7)',
        fontSize: 14,
        textAlign: 'center',
        marginTop: 16,
        fontStyle: 'italic',
    },
    // Countdown
    countdownBox: {
        backgroundColor: 'rgba(255, 255, 255, 0.2)', // Glass effect
        width: 160,
        height: 160,
        borderRadius: 80,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 4,
        borderColor: '#fff',
    },
    countdownText: {
        color: '#fff',
        fontSize: 100,
        fontWeight: '900',
    },
    // Recording
    recordingBox: {
        position: 'absolute',
        top: 60,
        backgroundColor: 'rgba(255, 59, 48, 0.9)', // Vibrant Red
        paddingHorizontal: 24,
        paddingVertical: 12,
        borderRadius: 30,
        flexDirection: 'row',
        alignItems: 'center',
        shadowColor: '#f00',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.5,
        shadowRadius: 10,
    },
    recordingText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: '700',
        marginLeft: 8,
        textTransform: 'uppercase',
        letterSpacing: 1,
    },
    // Uploading
    uploadingBox: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        padding: 40,
        borderRadius: 24,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.2,
        shadowRadius: 20,
    },
    uploadingText: {
        fontSize: 20,
        fontWeight: '700',
        marginTop: 20,
        color: '#1A1A1A',
    },
    // Footer Button
    startButton: {
        position: 'absolute',
        bottom: 50,
        alignSelf: 'center',
        backgroundColor: '#4CAF50', // Success Green
        paddingHorizontal: 40,
        paddingVertical: 20,
        borderRadius: 40,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 5 },
        shadowOpacity: 0.3,
        shadowRadius: 10,
        elevation: 8,
        minWidth: 250,
        alignItems: 'center',
    },
    startButtonText: {
        color: '#fff',
        fontSize: 20,
        fontWeight: 'bold',
        letterSpacing: 0.5,
    },
    errorText: {
        color: '#FF5252',
        fontSize: 16,
        textAlign: 'center',
        marginBottom: 20,
        fontWeight: '600',
    },
});
