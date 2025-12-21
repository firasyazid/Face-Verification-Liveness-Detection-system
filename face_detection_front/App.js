import { useState } from 'react';
import { StyleSheet, View } from 'react-native';
import RegisterScreen from './screens/RegisterScreen';
import LivenessScreen from './screens/LivenessScreen';
import ResultScreen from './screens/ResultScreen';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('register');  
  const [userData, setUserData] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);

  const handleRegistrationComplete = (data) => {
    setUserData(data);
    setCurrentScreen('liveness');
  };

  const handleLivenessComplete = (result) => {
    setVerificationResult(result);
    setCurrentScreen('result');
  };

  const resetFlow = () => {
    setCurrentScreen('register');
    setUserData(null);
    setVerificationResult(null);
  };

  return (
    <View style={styles.container}>
      {currentScreen === 'register' && (
        <RegisterScreen onComplete={handleRegistrationComplete} />
      )}
      {currentScreen === 'liveness' && (
        <LivenessScreen
          userData={userData}
          onComplete={handleLivenessComplete}
        />
      )}
      {currentScreen === 'result' && (
        <ResultScreen
          result={verificationResult}
          onReset={resetFlow}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});
