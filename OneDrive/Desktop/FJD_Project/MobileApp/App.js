import React, { useState, useRef } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  Image, 
  ActivityIndicator, 
  ScrollView, 
  Alert,
  SafeAreaView,
  StatusBar,
  Platform
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

// ⚠️ REPLACE WITH YOUR RENDER URL
const API_URL = "https://fjd-brain.onrender.com/analyze";

export default function App() {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const scrollViewRef = useRef();

  // 1. Pick Image (Simplified - No Cropping for now to fix flow)
  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false, // 🔴 DISABLED CROP STEP to fix the "White Screen" and "Missing Button" confusion
      quality: 1,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      setResult(null); // Clear previous results
    }
  };

  // 2. Send to Backend
  const analyzeImage = async () => {
    if (!image) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', {
      uri: image,
      name: 'scan.jpg',
      type: 'image/jpeg',
    });

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = await response.json();
      
      if (data.score !== undefined) {
        setResult(data);
        setTimeout(() => {
          scrollViewRef.current?.scrollToEnd({ animated: true });
        }, 500);
      } else {
        Alert.alert("Error", "Server returned invalid data.");
      }
    } catch (error) {
      Alert.alert("Connection Failed", "Could not reach the server.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (color) => {
    if (color === 'RED') return '#FF3B30';
    if (color === 'YELLOW') return '#FFCC00';
    return '#34C759';
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor="#F8F9FA" />
      
      <View style={styles.headerContainer}>
         <Text style={styles.headerTitle}>🛡️ Check My Job</Text>
         <Text style={styles.headerSubtitle}>Forensic Scam Detector</Text>
      </View>

      <ScrollView 
        ref={scrollViewRef}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* IMAGE PREVIEW AREA */}
        <View style={styles.cardContainer}>
          {image ? (
            <View style={styles.imageWrapper}>
              <Image source={{ uri: image }} style={styles.previewImage} />
              <TouchableOpacity style={styles.changeButton} onPress={pickImage}>
                <Text style={styles.changeButtonText}>Change Image</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity style={styles.uploadPlaceholder} onPress={pickImage}>
              <Text style={styles.uploadIcon}>📷</Text>
              <Text style={styles.uploadText}>Tap to Upload Screenshot</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* RESULTS AREA */}
        {result && (
          <View style={[styles.resultCard, { borderLeftColor: getStatusColor(result.color) }]}>
            <View style={[styles.verdictBadge, { backgroundColor: getStatusColor(result.color) }]}>
              <Text style={styles.verdictText}>{result.label}</Text>
            </View>
            
            <Text style={styles.riskScore}>Risk Score: {result.score}%</Text>

            <View style={styles.divider} />

            <Text style={styles.sectionTitle}>⚠️ DETECTED THREATS</Text>
            {result.reasons && result.reasons.length > 0 ? (
              result.reasons.map((r, i) => (
                <Text key={i} style={styles.reasonText}>• {r}</Text>
              ))
            ) : (
               <Text style={styles.reasonText}>No specific threats flagged.</Text>
            )}

            <Text style={[styles.sectionTitle, { marginTop: 15 }]}>📄 EXTRACTED CONTENT</Text>
            <View style={styles.codeBlock}>
              <Text style={styles.extractedText} numberOfLines={5}>
                {result.extracted_text || "No text found."}
              </Text>
            </View>
          </View>
        )}

        {/* Spacer for bottom button */}
        <View style={{ height: 100 }} />
      </ScrollView>

      {/* FIXED BOTTOM BUTTON */}
      <View style={styles.footer}>
        {image ? (
          <TouchableOpacity 
            style={[styles.actionButton, loading && styles.disabledButton]} 
            onPress={analyzeImage}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={styles.actionButtonText}>ANALYZE EVIDENCE 🔍</Text>
            )}
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={[styles.actionButton, styles.inactiveButton]} onPress={pickImage}>
            <Text style={[styles.actionButtonText, styles.inactiveText]}>Select Image</Text>
          </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight + 10 : 0,
  },
  headerContainer: {
    paddingHorizontal: 20,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#EEE',
    backgroundColor: '#F8F9FA',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#333',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  scrollContent: {
    padding: 20,
  },
  cardContainer: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    overflow: 'hidden',
    minHeight: 300,
  },
  uploadPlaceholder: {
    height: 300,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFF',
  },
  uploadIcon: {
    fontSize: 50,
    marginBottom: 10,
    opacity: 0.5,
  },
  uploadText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#555',
  },
  imageWrapper: {
    width: '100%',
    height: 350, // Fixed height to prevent "White Blank"
    backgroundColor: '#000',
  },
  previewImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'contain',
  },
  changeButton: {
    position: 'absolute',
    top: 15,
    right: 15,
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  changeButtonText: {
    color: '#FFF',
    fontWeight: '600',
    fontSize: 12,
  },
  // Result Card
  resultCard: {
    marginTop: 25,
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 20,
    borderLeftWidth: 6,
    elevation: 3,
  },
  verdictBadge: {
    alignSelf: 'flex-start',
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 6,
    marginBottom: 10,
  },
  verdictText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 12,
    textTransform: 'uppercase',
  },
  riskScore: {
    fontSize: 22,
    fontWeight: '800',
    color: '#333',
  },
  divider: {
    height: 1,
    backgroundColor: '#EEE',
    marginVertical: 15,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#999',
    marginBottom: 8,
  },
  reasonText: {
    fontSize: 15,
    color: '#444',
    marginBottom: 6,
    lineHeight: 22,
  },
  codeBlock: {
    backgroundColor: '#F5F5F5',
    padding: 12,
    borderRadius: 8,
  },
  extractedText: {
    fontSize: 12,
    fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    color: '#666',
  },
  // Footer Button
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#FFF',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#EEE',
  },
  actionButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  inactiveButton: {
    backgroundColor: '#E0E0E0',
  },
  disabledButton: {
    opacity: 0.7,
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFF',
  },
  inactiveText: {
    color: '#999',
  },
});