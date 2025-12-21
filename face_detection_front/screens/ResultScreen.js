import {
    StyleSheet,
    View,
    Text,
    TouchableOpacity,
    SafeAreaView,
    ScrollView,
} from 'react-native';

export default function ResultScreen({ result, onReset }) {
    const isSuccess = result?.status === 'success' && (result?.verification?.verified || result?.status === 'success');

    // Status color
    const statusColor = isSuccess ? '#4CAF50' : '#FF5252';
    const statusIcon = isSuccess ? '✓' : '✕';

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.content}>

                {/* Result Card */}
                <View style={[styles.card, { shadowColor: statusColor }]}>
                    <View style={[styles.iconContainer, { backgroundColor: statusColor }]}>
                        <Text style={styles.iconText}>{statusIcon}</Text>
                    </View>

                    <Text style={styles.title}>
                        {isSuccess ? 'Verification Passed' : 'Verification Failed'}
                    </Text>

                    <Text style={styles.message}>
                        {isSuccess
                            ? 'Identity verified successfully. You may now proceed.'
                            : result?.liveness?.message || result?.verification?.error || 'We could not verify your identity. Please try again.'}
                    </Text>

                    <View style={styles.ticket}>
                        {/* Match Confidence */}
                        <View style={styles.ticketRow}>
                            <Text style={styles.ticketLabel}>Match Confidence</Text>
                            <View style={styles.ticketValueContainer}>
                                <Text style={[styles.ticketValue, { color: statusColor }]}>
                                    {isSuccess ? 'High' : 'Low'}
                                </Text>
                            </View>
                        </View>

                        {/* Liveness Status */}
                        <View style={styles.ticketRow}>
                            <Text style={styles.ticketLabel}>Liveness Check</Text>
                            <Text style={styles.ticketValue}>
                                {result?.liveness?.passed ? 'Passed' : 'Failed'}
                            </Text>
                        </View>

                        {result?.verification?.distance !== undefined && (
                            <View style={styles.ticketRow}>
                                <Text style={styles.ticketLabel}>Distance Metric</Text>
                                <Text style={styles.ticketValue}>
                                    {result.verification.distance.toFixed(3)}
                                </Text>
                            </View>
                        )}
                    </View>
                </View>

                <TouchableOpacity
                    style={[styles.button, { backgroundColor: isSuccess ? '#1A1A1A' : statusColor }]}
                    onPress={onReset}
                    activeOpacity={0.8}
                >
                    <Text style={styles.buttonText}>
                        {isSuccess ? 'Done' : 'Try Again'}
                    </Text>
                </TouchableOpacity>

            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F8F9FA',
    },
    content: {
        flexGrow: 1,
        padding: 24,
        alignItems: 'center',
        justifyContent: 'center',
    },
    card: {
        backgroundColor: '#fff',
        width: '100%',
        borderRadius: 24,
        padding: 32,
        alignItems: 'center',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.15,
        shadowRadius: 20,
        elevation: 10,
        marginBottom: 40,
    },
    iconContainer: {
        width: 100,
        height: 100,
        borderRadius: 50,
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 5 },
        shadowOpacity: 0.2,
        shadowRadius: 10,
        elevation: 5,
    },
    iconText: {
        fontSize: 50,
        color: '#fff',
        fontWeight: 'bold',
    },
    title: {
        fontSize: 26,
        fontWeight: '800',
        color: '#1A1A1A',
        marginBottom: 12,
        textAlign: 'center',
    },
    message: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        marginBottom: 32,
        lineHeight: 24,
    },
    ticket: {
        width: '100%',
        backgroundColor: '#F9FAFB',
        borderRadius: 16,
        padding: 20,
        borderWidth: 1,
        borderColor: '#EFEFEF',
    },
    ticketRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#F0F0F0',
    },
    ticketLabel: {
        fontSize: 15,
        color: '#888',
        fontWeight: '500',
    },
    ticketValue: {
        fontSize: 16,
        color: '#1A1A1A',
        fontWeight: '700',
    },
    button: {
        width: '100%',
        paddingVertical: 18,
        borderRadius: 16,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 8,
        elevation: 5,
    },
    buttonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
        letterSpacing: 0.5,
    },
});
