import React, { useState } from 'react';
import {
    StyleSheet,
    View,
    Text,
    TouchableOpacity,
    Image,
    SafeAreaView,
    Alert, StatusBar
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function RegisterScreen({ onComplete }) {
    const [profileImage, setProfileImage] = useState(null);

    React.useEffect(() => {
        (async () => {
            const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
            if (status !== 'granted') {
                Alert.alert('Permission Denied', 'We need access to your photos to upload a profile picture.');
            }
        })();
    }, []);

    const pickImage = async () => {
        try {
            const result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: 'Images',
                allowsEditing: true,
                aspect: [1, 1],
                quality: 0.8,
            });

            if (!result.canceled) {
                setProfileImage(result.assets[0]);
            }
        } catch (error) {
            Alert.alert("Error", "Could not open gallery: " + error.message);
        }
    };

    const handleNext = () => {
        if (!profileImage) {
            Alert.alert('Photo Required', 'Please upload a profile photo to continue.');
            return;
        }

        onComplete({ profileImage });
    };

    return (
        <SafeAreaView style={styles.container}>
            <StatusBar barStyle="dark-content" />
            <View style={styles.content}>

                {/* Header Section */}
                <View style={styles.header}>
                    <Text style={styles.title}>Identity Verification</Text>
                    <Text style={styles.subtitle}>Upload a clear photo of your face to begin.</Text>
                </View>

                <View style={styles.uploadContainer}>
                    <TouchableOpacity
                        style={[styles.imageContainer, !profileImage && styles.imageContainerEmpty]}
                        onPress={pickImage}
                        activeOpacity={0.7}
                    >
                        {profileImage ? (
                            <Image source={{ uri: profileImage.uri }} style={styles.image} />
                        ) : (
                            <View style={styles.placeholderContainer}>
                                <Text style={styles.plusIcon}>+</Text>
                                <Text style={styles.placeholderText}>Tap to Upload Photo</Text>
                            </View>
                        )}

                        {profileImage && (
                            <View style={styles.editBadge}>
                                <Text style={styles.editIcon}>✎</Text>
                            </View>
                        )}
                    </TouchableOpacity>
                </View>

                {/* Backup Button if circle doesn't work */}
                <TouchableOpacity onPress={pickImage} style={{ padding: 10 }}>
                    <Text style={{ color: '#4CAF50', fontWeight: 'bold' }}>Select Photo</Text>
                </TouchableOpacity>

                {/* Instructions */}
                <View style={styles.infoContainer}>
                    <Text style={styles.infoTitle}>Photo Requirements:</Text>
                    <View style={styles.bulletPoint}>
                        <Text style={styles.bullet}>•</Text>
                        <Text style={styles.infoText}>Good lighting, no shadows</Text>
                    </View>
                    <View style={styles.bulletPoint}>
                        <Text style={styles.bullet}>•</Text>
                        <Text style={styles.infoText}>Face fully visible (no masks/glasses)</Text>
                    </View>
                    <View style={styles.bulletPoint}>
                        <Text style={styles.bullet}>•</Text>
                        <Text style={styles.infoText}>Neutral expression</Text>
                    </View>
                </View>

                <View style={styles.footer}>
                    <TouchableOpacity
                        style={[styles.button, !profileImage && styles.buttonDisabled]}
                        onPress={handleNext}
                        disabled={!profileImage}
                    >
                        <Text style={styles.buttonText}>Continue to Verification</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F8F9FA', // Clean light gray background
    },
    content: {
        flex: 1,
        padding: 24,
        justifyContent: 'space-between',
    },
    header: {
        marginTop: 40,
        alignItems: 'center',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#1A1A1A',
        marginBottom: 8,
        letterSpacing: 0.5,
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        paddingHorizontal: 20,
    },
    uploadContainer: {
        alignItems: 'center',
        marginVertical: 20,
    },
    imageContainer: {
        width: 200,
        height: 200,
        borderRadius: 100, // Circular
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.15,
        shadowRadius: 20,
        elevation: 10,
        backgroundColor: '#fff',
        marginVertical: 40,
    },
    imageContainerEmpty: {
        borderWidth: 2,
        borderColor: '#E0E0E0',
        borderStyle: 'dashed',
        backgroundColor: '#FFFFFF',
    },
    image: {
        width: '100%',
        height: '100%',
        borderRadius: 100,
    },
    placeholderContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    plusIcon: {
        fontSize: 50,
        color: '#4CAF50', // Brand color
        fontWeight: '300',
        marginBottom: 5,
    },
    placeholderText: {
        fontSize: 14,
        color: '#999',
        fontWeight: '600',
    },
    editBadge: {
        position: 'absolute',
        bottom: 10,
        right: 10,
        backgroundColor: '#4CAF50',
        width: 40,
        height: 40,
        borderRadius: 20,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 3,
        borderColor: '#fff',
    },
    editIcon: {
        color: '#fff',
        fontSize: 18,
    },
    infoContainer: {
        backgroundColor: '#fff',
        padding: 20,
        borderRadius: 16,
        marginBottom: 20,
        borderWidth: 1,
        borderColor: '#F0F0F0',
    },
    infoTitle: {
        fontSize: 14,
        fontWeight: '700',
        color: '#333',
        marginBottom: 12,
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    bulletPoint: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    bullet: {
        fontSize: 20,
        color: '#4CAF50',
        marginRight: 10,
        lineHeight: 22,
    },
    infoText: {
        fontSize: 15,
        color: '#555',
    },
    footer: {
        marginBottom: 20,
    },
    button: {
        backgroundColor: '#1A1A1A', // Dark primary button
        paddingVertical: 18,
        borderRadius: 16,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 8,
        elevation: 5,
    },
    buttonDisabled: {
        backgroundColor: '#E0E0E0',
        shadowOpacity: 0,
    },
    buttonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
    },
});
