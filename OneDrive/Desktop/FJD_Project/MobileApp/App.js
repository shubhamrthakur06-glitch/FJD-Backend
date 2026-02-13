import React, { useState, useEffect, createContext, useContext } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, TextInput, ScrollView, ActivityIndicator, Alert, Image, Platform, StatusBar } from 'react-native';
import { Ionicons, MaterialIcons, FontAwesome5, Feather } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { NavigationContainer, useNavigation, useRoute, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { LinearGradient } from 'expo-linear-gradient';

// --- CONFIGURATION ---
const API_URL = "https://fjd-brain.onrender.com"; 

// --- THEME DEFINITIONS ---
const PALETTES = {
  light: {
    mode: 'light',
    bg: '#F8F9FA',
    card: '#FFFFFF',
    primary: '#2563EB',
    secondary: '#7C3AED',
    text: '#1F2937',
    textMuted: '#6B7280',
    danger: '#EF4444',
    success: '#10B981',
    warning: '#F59E0B',
    border: '#E5E7EB',
    inputBg: '#F3F4F6',
    heroText: '#FFFFFF',
    heroSub: '#E0E7FF'
  },
  dark: {
    mode: 'dark',
    bg: '#121212',
    card: '#1E1E1E',
    primary: '#3B82F6', // Lighter blue for dark mode
    secondary: '#8B5CF6',
    text: '#F3F4F6',
    textMuted: '#9CA3AF',
    danger: '#F87171',
    success: '#34D399',
    warning: '#FBBF24',
    border: '#374151',
    inputBg: '#374151',
    heroText: '#FFFFFF',
    heroSub: '#E0E7FF'
  }
};

// --- CONTEXT ---
const ThemeContext = createContext();
const useTheme = () => useContext(ThemeContext);

const ThemeProvider = ({ children }) => {
  const [themeMode, setThemeMode] = useState('light');
  const theme = PALETTES[themeMode];

  const toggleTheme = () => {
    setThemeMode(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, isDark: themeMode === 'dark' }}>
      {children}
    </ThemeContext.Provider>
  );
};

const Stack = createNativeStackNavigator();

// ==================== COMPONENTS ====================

const StepProgress = ({ current }) => {
  const { theme } = useTheme();
  return (
    <View style={{ flexDirection: 'row', marginBottom: 20, marginTop: 10 }}>
      {[1, 2, 3].map((step) => (
        <View key={step} style={{ flex: 1, height: 4, backgroundColor: step <= current ? theme.primary : theme.border, marginHorizontal: 2, borderRadius: 2 }} />
      ))}
    </View>
  );
};

// ==================== SCREENS ====================

// 1. HOME SCREEN
function HomeScreen() {
  const navigation = useNavigation();
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <ScrollView style={[styles.container, { backgroundColor: theme.bg }]} contentContainerStyle={{paddingBottom: 40}}>
      <StatusBar barStyle={isDark ? "light-content" : "dark-content"} />
      
      {/* Header */}
      <View style={styles.headerRow}>
        <View>
          <Text style={[styles.appName, { color: theme.text }]}>CheckMyJob</Text>
          <Text style={[styles.appTagline, { color: theme.textMuted }]}>Verify job offers instantly</Text>
        </View>
        <TouchableOpacity style={[styles.iconBtn, { backgroundColor: isDark ? '#333' : theme.primary }]} onPress={toggleTheme}>
           <Ionicons name={isDark ? "sunny" : "moon"} size={22} color="white" />
        </TouchableOpacity>
      </View>

      {/* Hero Action Card */}
      <LinearGradient colors={[theme.primary, theme.secondary]} start={{x: 0, y: 0}} end={{x: 1, y: 1}} style={styles.heroCard}>
        <MaterialIcons name="security" size={48} color="white" style={{marginBottom: 10}} />
        <Text style={styles.heroTitle}>Check Job for Scam</Text>
        <Text style={styles.heroSubtitle}>Analyze screenshots, links, or documents in seconds.</Text>
        
        <TouchableOpacity style={styles.heroButton} onPress={() => navigation.navigate('Step1_Image')}>
           <Text style={[styles.heroButtonText, { color: theme.primary }]}>Start Analysis</Text>
           <Feather name="arrow-right" size={20} color={theme.primary} />
        </TouchableOpacity>
      </LinearGradient>

      {/* Trending Alerts Section */}
      <Text style={[styles.sectionTitle, { color: theme.text }]}>Trending Scam Alerts</Text>

      <View style={[styles.alertCard, { backgroundColor: isDark ? '#2C1A1A' : '#FEF2F2', borderColor: isDark ? '#451a1a' : '#FEE2E2' }]}>
        <View style={{flex:1}}>
           <View style={{flexDirection:'row', alignItems:'center'}}>
             <View style={[styles.dot, {backgroundColor: theme.danger}]} />
             <Text style={[styles.alertTitle, { color: theme.text }]}>Part-time Job Scams</Text>
           </View>
           <Text style={[styles.alertDesc, { color: theme.textMuted }]}>Fake work-from-home tasks asking for deposits.</Text>
        </View>
        <View style={[styles.badge, {backgroundColor: theme.danger}]}>
            <Text style={styles.badgeText}>+15%</Text>
        </View>
      </View>

      <View style={[styles.alertCard, { backgroundColor: isDark ? '#2C2510' : '#FFFBEB', borderColor: isDark ? '#453810' : '#FEF3C7' }]}>
        <View style={{flex:1}}>
           <View style={{flexDirection:'row', alignItems:'center'}}>
             <View style={[styles.dot, {backgroundColor: theme.warning}]} />
             <Text style={[styles.alertTitle, { color: theme.text }]}>Fake Offer Letters</Text>
           </View>
           <Text style={[styles.alertDesc, { color: theme.textMuted }]}>Counterfeit PDFs imitating big tech companies.</Text>
        </View>
        <View style={[styles.badge, {backgroundColor: theme.warning}]}>
            <Text style={styles.badgeText}>+8%</Text>
        </View>
      </View>

      {/* Stats Row */}
      <View style={styles.statsRow}>
          <View style={[styles.statCard, {backgroundColor: isDark ? '#064E3B' : '#ECFDF5'}]}>
             <Text style={[styles.statNum, {color: theme.success}]}>2.3K+</Text>
             <Text style={[styles.statLabel, {color: isDark ? '#A7F3D0' : theme.textMuted}]}>Verified Today</Text>
          </View>
          <View style={[styles.statCard, {backgroundColor: isDark ? '#4C1D95' : '#F3E8FF'}]}>
             <Text style={[styles.statNum, {color: isDark ? '#C4B5FD' : theme.secondary}]}>99%</Text>
             <Text style={[styles.statLabel, {color: isDark ? '#DDD6FE' : theme.textMuted}]}>Accuracy Rate</Text>
          </View>
      </View>

    </ScrollView>
  );
}

// 2. STEP 1: SCREENSHOT PROOF
function Step1ImageScreen() {
  const navigation = useNavigation();
  const { theme } = useTheme();
  const [image, setImage] = useState(null);

  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false,
      quality: 1,
    });
    if (!result.canceled) setImage(result.assets[0]);
  };

  return (
    <View style={[styles.stepContainer, { backgroundColor: theme.bg }]}>
      <StepProgress current={1} />
      <Text style={[styles.stepHeader, { color: theme.secondary }]}>Step 1 of 3</Text>
      <Text style={[styles.stepTitle, { color: theme.text }]}>Job Screenshot or Chat</Text>

      <View style={[styles.uploadBox, { backgroundColor: theme.inputBg, borderColor: theme.border }]}>
         {image ? (
            <View style={{width:'100%', height:'100%', alignItems:'center', justifyContent:'center'}}>
               <Image source={{ uri: image.uri }} style={styles.previewImg} />
               <TouchableOpacity style={styles.removeBtn} onPress={() => setImage(null)}>
                  <Ionicons name="close-circle" size={24} color="white" />
               </TouchableOpacity>
            </View>
         ) : (
            <>
               <View style={[styles.iconCircle, { backgroundColor: theme.primary }]}>
                  <Ionicons name="camera" size={32} color="white" />
               </View>
               <Text style={[styles.uploadPrompt, { color: theme.text }]}>Do you have a screenshot?</Text>
               <Text style={[styles.uploadSub, { color: theme.textMuted }]}>Upload chat proof from WhatsApp or Telegram.</Text>
            </>
         )}
      </View>

      <TouchableOpacity style={[styles.primaryButton, { backgroundColor: theme.primary }]} onPress={pickImage}>
         <Ionicons name="image" size={20} color="white" style={{marginRight: 8}} />
         <Text style={styles.primaryBtnText}>{image ? "Change Screenshot" : "Upload Screenshot"}</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.skipBtn} onPress={() => navigation.navigate('Step2_Link', { evidence: { image } })}>
         <Text style={[styles.skipText, { color: theme.textMuted }]}>{image ? "Next Step" : "Skip"}</Text>
      </TouchableOpacity>
    </View>
  );
}

// 3. STEP 2: LINK PROOF
function Step2LinkScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { theme } = useTheme();
  const currentEvidence = route.params?.evidence || {};
  const [link, setLink] = useState('');

  return (
    <View style={[styles.stepContainer, { backgroundColor: theme.bg }]}>
      <StepProgress current={2} />
      <Text style={[styles.stepHeader, { color: theme.secondary }]}>Step 2 of 3</Text>
      <Text style={[styles.stepTitle, { color: theme.text }]}>Job Link Details</Text>

      <View style={[styles.inputContainer, { backgroundColor: theme.card, shadowColor: theme.text }]}>
         <View style={[styles.iconCircle, {backgroundColor: theme.secondary, marginBottom: 20}]}>
             <Ionicons name="link" size={32} color="white" />
         </View>
         <Text style={[styles.uploadPrompt, { color: theme.text }]}>Have a job link?</Text>
         <Text style={[styles.uploadSub, { color: theme.textMuted }]}>Paste the website or Google Form link to verify.</Text>
         
         <TextInput 
            style={[styles.textInput, { backgroundColor: theme.inputBg, color: theme.text }]} 
            placeholder="Paste https:// link here..." 
            placeholderTextColor={theme.textMuted}
            value={link}
            onChangeText={setLink}
            autoCapitalize="none"
         />
      </View>

      <TouchableOpacity style={[styles.primaryButton, {backgroundColor: theme.secondary}]} onPress={() => navigation.navigate('Step3_File', { evidence: { ...currentEvidence, link } })}>
         <Text style={styles.primaryBtnText}>{link ? "Next Step" : "Add Link & Next"}</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.skipBtn} onPress={() => navigation.navigate('Step3_File', { evidence: { ...currentEvidence, link } })}>
         <Text style={[styles.skipText, { color: theme.textMuted }]}>Skip</Text>
      </TouchableOpacity>
    </View>
  );
}

// 4. STEP 3: DOCUMENT PROOF & ANALYZE
function Step3FileScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { theme, isDark } = useTheme();
  const currentEvidence = route.params?.evidence || {};
  const [doc, setDoc] = useState(null);

  const pickDocument = async () => {
      try {
          const result = await DocumentPicker.getDocumentAsync({
              type: ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/*'], 
              copyToCacheDirectory: true
          });
          if (!result.canceled && result.assets) setDoc(result.assets[0]);
      } catch (err) { Alert.alert("Error", "Could not pick file."); }
  };

  const hasAnyEvidence = currentEvidence.image || currentEvidence.link || doc;

  const handleAnalyze = () => {
      if (!hasAnyEvidence) {
          Alert.alert("Missing Evidence", "We need at least ONE proof (Screenshot, Link, or Document) to analyze.");
          return;
      }
      navigation.navigate('Result', { evidence: { ...currentEvidence, document: doc } });
  };

  // Determine doc box colors based on theme
  const docBoxBg = isDark ? '#064E3B' : '#ECFDF5';
  const docBoxBorder = isDark ? '#065F46' : '#D1FAE5';

  return (
    <View style={[styles.stepContainer, { backgroundColor: theme.bg }]}>
      <StepProgress current={3} />
      <Text style={[styles.stepHeader, { color: theme.secondary }]}>Step 3 of 3</Text>
      <Text style={[styles.stepTitle, { color: theme.text }]}>Offer Letter or Document</Text>

      <View style={[styles.uploadBox, { backgroundColor: docBoxBg, borderColor: docBoxBorder }]}>
         {doc ? (
            <View style={{alignItems:'center'}}>
               <FontAwesome5 name="file-alt" size={40} color={theme.success} />
               <Text style={[styles.uploadPrompt, {marginTop:10, color: theme.text}]}>{doc.name}</Text>
               <TouchableOpacity onPress={() => setDoc(null)}><Text style={{color: theme.danger, marginTop:5}}>Remove</Text></TouchableOpacity>
            </View>
         ) : (
             <>
                <View style={[styles.iconCircle, {backgroundColor: theme.success}]}>
                    <FontAwesome5 name="file-contract" size={24} color="white" />
                </View>
                <Text style={[styles.uploadPrompt, { color: theme.text }]}>Upload offer letter</Text>
                <Text style={[styles.uploadSub, { color: theme.textMuted }]}>PDF, Word, or Image files supported.</Text>
             </>
         )}
      </View>

      <TouchableOpacity style={[styles.primaryButton, {backgroundColor: theme.success}]} onPress={pickDocument}>
         <Ionicons name="cloud-upload" size={20} color="white" style={{marginRight: 8}} />
         <Text style={styles.primaryBtnText}>{doc ? "Change File" : "Upload Document"}</Text>
      </TouchableOpacity>

      {/* Lock Logic Message */}
      {!hasAnyEvidence && (
          <View style={[styles.warningBox, { backgroundColor: isDark ? '#451a03' : '#FFFBEB' }]}>
             <Ionicons name="alert-circle" size={20} color={theme.warning} />
             <Text style={[styles.warningText, { color: theme.warning }]}>At least one proof required to continue.</Text>
          </View>
      )}

      <TouchableOpacity 
         style={[styles.actionBtn, { backgroundColor: theme.text }, !hasAnyEvidence && {opacity: 0.5, backgroundColor: theme.textMuted}]} 
         onPress={handleAnalyze}
         disabled={!hasAnyEvidence}
      >
         <Text style={[styles.actionBtnText, { color: theme.bg }]}>ANALYZE EVIDENCE</Text>
         <MaterialIcons name="search" size={24} color={theme.bg} style={{marginLeft: 5}}/>
      </TouchableOpacity>
    </View>
  );
}

// --- NEW COMPONENT: FORENSIC LOADER ---
const ForensicLoader = ({ evidence }) => {
  const { theme, isDark } = useTheme();
  const [msgIndex, setMsgIndex] = useState(0);

  // 1. Define the Script based on what was uploaded
  const getMessages = () => {
    const msgs = ["🚀 Initializing Forensic AI..."]; // Always start here

    // Image Steps
    if (evidence.image) {
      msgs.push("📷 Scanning screenshot pixels...");
      msgs.push("🔍 Extracting text via OCR...");
      msgs.push("🕵️‍♂️ Analyzing chat patterns...");
    }

    // Link Steps
    if (evidence.link) {
      msgs.push("🌐 Initiating Active Link Recon...");
      msgs.push("📡 Pinging remote server...");
      msgs.push("⏳ Checking domain age & blacklists...");
      msgs.push("🕷️ Crawling website for hidden traps...");
    }

    // Doc Steps
    if (evidence.document) {
      msgs.push("📄 Reading document metadata...");
      msgs.push("📝 Analyzing contract clauses...");
      msgs.push("⚖️ Checking legal terminology...");
    }

    // Combined/Final Steps
    if (evidence.image && evidence.link) msgs.push("🔄 Cross-referencing Link vs Screenshot...");
    msgs.push("🧠 Running Deep Brain prediction...");
    msgs.push("📊 Calculating final risk score...");
    
    return msgs;
  };

  const messages = React.useMemo(() => getMessages(), [evidence]);

  // 2. Cycle through messages every 2.5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex((prev) => (prev + 1) % messages.length);
    }, 2500);
    return () => clearInterval(interval);
  }, [messages]);

  return (
    <View style={[styles.container, {justifyContent:'center', alignItems:'center', backgroundColor: theme.bg, padding: 30}]}>
      {/* Big Animated Icon */}
      <View style={{marginBottom: 40}}>
         <ActivityIndicator size="large" color={theme.primary} style={{transform: [{scale: 2}]}} />
      </View>

      {/* The Dynamic Text */}
      <Text style={{
          fontSize: 18, 
          fontWeight: 'bold', 
          color: theme.primary, 
          textAlign: 'center', 
          marginBottom: 10,
          height: 30 // Fixed height prevents jumping
      }}>
        {messages[msgIndex]}
      </Text>

      {/* Subtext to manage expectations */}
      <Text style={{color: theme.textMuted, fontSize: 13, textAlign: 'center', marginTop: 20}}>
        {msgIndex < 2 ? "Waking up the AI server..." : "This might take up to 30 seconds..."}
      </Text>
    </View>
  );
};


// --- UPDATED RESULT SCREEN ---
function ResultScreen() {
    const navigation = useNavigation();
    const route = useRoute();
    const { theme } = useTheme();
    const evidence = route.params?.evidence;
    const [loading, setLoading] = useState(true);
    const [result, setResult] = useState(null);

    useEffect(() => { performAnalysis(); }, []);

    const performAnalysis = async () => {
        const formData = new FormData();
        let hasData = false;

        if (evidence.image) {
            formData.append('image', {
                uri: Platform.OS === 'ios' ? evidence.image.uri.replace('file://', '') : evidence.image.uri,
                type: 'image/jpeg',
                name: 'screenshot.jpg',
            });
            hasData = true;
        }

        if (evidence.document) {
            formData.append('document', {
                uri: Platform.OS === 'ios' ? evidence.document.uri.replace('file://', '') : evidence.document.uri,
                type: evidence.document.mimeType || 'application/pdf',
                name: evidence.document.name || 'doc.pdf',
            });
            hasData = true;
        }

        if (evidence.link && evidence.link.trim() !== "") {
            formData.append('link', evidence.link);
            hasData = true;
        }

        if (!hasData) { Alert.alert("Error", "No valid data received."); navigation.goBack(); return; }

        try {
            console.log("📡 Uploading Triple-Threat Data...");
            let response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                body: formData,
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            if (!response.ok) throw new Error(`Status: ${response.status}`);
            let json = await response.json();
            setResult(json);
        } catch (error) {
            Alert.alert("Server Error", "Could not analyze. The server might be sleeping. Try again.");
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    // 🛑 USE THE NEW LOADER HERE
    if (loading) {
        return <ForensicLoader evidence={evidence} />;
    }

    if (!result) return null;

    const isHighRisk = result.color === 'RED';
    const isSafe = result.color === 'GREEN';
    const resultColor = isHighRisk ? theme.danger : isSafe ? theme.success : theme.warning;

    return (
      <ScrollView style={[styles.container, { backgroundColor: theme.bg }]} contentContainerStyle={{padding: 20}}>
         
         <View style={[styles.resultCard, { backgroundColor: theme.card, borderLeftColor: resultColor, shadowColor: theme.text }]}>
             <View style={[styles.scoreBadge, {backgroundColor: resultColor}]}>
                 <Text style={styles.scoreBadgeText}>{result.label}</Text>
             </View>
             <Text style={[styles.riskTitle, { color: theme.text }]}>Risk Score: {result.score}%</Text>
             
             <View style={[styles.divider, { backgroundColor: theme.border }]} />
             
             <Text style={[styles.subHeader, { color: theme.textMuted }]}>⚠️ DETECTED THREATS</Text>
             {result.reasons.length > 0 ? (
                 result.reasons.map((r, i) => (
                    <View key={i} style={{flexDirection:'row', marginBottom: 8}}>
                        <Ionicons name="alert-circle" size={18} color={theme.textMuted} style={{marginTop:2}} />
                        <Text style={[styles.reasonText, { color: theme.text }]}>{r}</Text>
                    </View>
                 ))
             ) : (
                 <Text style={[styles.reasonText, { color: theme.text }]}>No obvious threats found in provided evidence.</Text>
             )}

             <View style={[styles.divider, { backgroundColor: theme.border }]} />

             <Text style={[styles.subHeader, { color: theme.textMuted }]}>📄 EXTRACTED CONTEXT</Text>
             <View style={[styles.codeBlock, { backgroundColor: theme.inputBg }]}>
                 <Text style={[styles.codeText, { color: theme.textMuted }]}>{result.extracted_text || "No readable text found."}</Text>
             </View>
         </View>

         <TouchableOpacity style={[styles.primaryButton, { backgroundColor: theme.primary }]} onPress={() => navigation.popToTop()}>
             <Text style={styles.primaryBtnText}>Verify Another Job</Text>
         </TouchableOpacity>
      </ScrollView>
    );
}

// Wrapper to Provide Theme
const MainNavigator = () => {
  const { isDark, theme } = useTheme();
  
  return (
    <NavigationContainer theme={isDark ? DarkTheme : DefaultTheme}>
      <Stack.Navigator screenOptions={{ 
          headerShown: false,
          contentStyle: { backgroundColor: theme.bg }
      }}>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Step1_Image" component={Step1ImageScreen} options={{headerShown:true, title:'', headerTransparent:true, headerTintColor: theme.text}} />
        <Stack.Screen name="Step2_Link" component={Step2LinkScreen} options={{headerShown:true, title:'', headerTransparent:true, headerTintColor: theme.text}} />
        <Stack.Screen name="Step3_File" component={Step3FileScreen} options={{headerShown:true, title:'', headerTransparent:true, headerTintColor: theme.text}} />
        <Stack.Screen name="Result" component={ResultScreen} options={{headerShown:true, title:'Analysis Result', headerTintColor: theme.text, headerStyle:{backgroundColor: theme.bg}}} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <MainNavigator />
    </ThemeProvider>
  );
}

// ==================== STYLES ====================
const styles = StyleSheet.create({
  container: { flex: 1 },
  headerRow: { flexDirection: 'row', justifyContent:'space-between', alignItems:'center', padding: 20, paddingTop: 50 },
  appName: { fontSize: 24, fontWeight: 'bold' },
  appTagline: { fontSize: 14 },
  iconBtn: { padding: 10, borderRadius: 50 },
  
  heroCard: { margin: 20, padding: 25, borderRadius: 20, alignItems: 'flex-start', shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 10, elevation: 5 },
  heroTitle: { fontSize: 22, fontWeight: 'bold', color: 'white', marginTop: 10 },
  heroSubtitle: { fontSize: 14, color: '#E0E7FF', marginVertical: 10, lineHeight: 20 },
  heroButton: { backgroundColor: 'white', paddingVertical: 10, paddingHorizontal: 20, borderRadius: 30, flexDirection: 'row', alignItems: 'center', marginTop: 10 },
  heroButtonText: { fontWeight: 'bold', marginRight: 5 },

  sectionTitle: { fontSize: 18, fontWeight: 'bold', marginLeft: 20, marginBottom: 10 },
  alertCard: { flexDirection: 'row', marginHorizontal: 20, marginBottom: 15, padding: 15, borderRadius: 12, borderWidth: 1, alignItems: 'center' },
  dot: { width: 8, height: 8, borderRadius: 4, marginRight: 8 },
  alertTitle: { fontWeight: 'bold', fontSize: 15 },
  alertDesc: { fontSize: 13, marginTop: 2 },
  badge: { paddingVertical: 4, paddingHorizontal: 8, borderRadius: 8 },
  badgeText: { color: 'white', fontSize: 12, fontWeight: 'bold' },

  statsRow: { flexDirection: 'row', paddingHorizontal: 20, justifyContent: 'space-between' },
  statCard: { flex: 0.48, padding: 15, borderRadius: 12, alignItems: 'center' },
  statNum: { fontSize: 20, fontWeight: 'bold' },
  statLabel: { fontSize: 12 },

  // Steps
  stepContainer: { flex: 1, padding: 20, paddingTop: 100 },
  stepHeader: { fontWeight: 'bold' },
  stepTitle: { fontSize: 26, fontWeight: 'bold', marginBottom: 20 },
  
  uploadBox: { height: 250, borderWidth: 1, borderRadius: 20, borderStyle: 'dashed', alignItems: 'center', justifyContent: 'center', marginBottom: 20 },
  previewImg: { width: '90%', height: '90%', borderRadius: 10, resizeMode: 'contain' },
  iconCircle: { width: 60, height: 60, borderRadius: 30, alignItems: 'center', justifyContent: 'center', marginBottom: 15 },
  uploadPrompt: { fontSize: 18, fontWeight: '600' },
  uploadSub: { fontSize: 13, textAlign: 'center', paddingHorizontal: 40, marginTop: 5 },
  
  primaryButton: { padding: 18, borderRadius: 12, alignItems: 'center', flexDirection: 'row', justifyContent: 'center', marginBottom: 15 },
  primaryBtnText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  
  skipBtn: { alignItems: 'center', padding: 15 },
  skipText: { fontWeight: '600' },
  removeBtn: { position:'absolute', top:10, right:10, backgroundColor:'rgba(0,0,0,0.5)', borderRadius:20 },

  inputContainer: { padding: 20, borderRadius: 20, alignItems: 'center', shadowOpacity: 0.05, shadowRadius: 10, elevation: 2, marginBottom: 30 },
  textInput: { width: '100%', padding: 15, borderRadius: 10, marginTop: 20, fontSize: 16 },

  warningBox: { flexDirection: 'row', alignItems: 'center', padding: 10, borderRadius: 8, marginBottom: 10, justifyContent: 'center' },
  warningText: { marginLeft: 8, fontSize: 12, fontWeight: '600' },
  
  actionBtn: { padding: 18, borderRadius: 12, alignItems: 'center', flexDirection: 'row', justifyContent: 'center', marginTop: 10 },
  actionBtnText: { fontWeight: 'bold', fontSize: 16 },

  // Results
  resultCard: { borderRadius: 15, padding: 20, borderLeftWidth: 6, shadowOpacity:0.1, elevation: 5, marginBottom: 30 },
  scoreBadge: { alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 12, borderRadius: 6, marginBottom: 10 },
  scoreBadgeText: { color: 'white', fontWeight: 'bold', fontSize: 12, textTransform: 'uppercase' },
  riskTitle: { fontSize: 28, fontWeight: 'bold', marginBottom: 15 },
  divider: { height: 1, marginVertical: 15 },
  subHeader: { fontSize: 12, fontWeight: 'bold', marginBottom: 10 },
  reasonText: { fontSize: 15, marginLeft: 8, flex: 1, lineHeight: 22 },
  codeBlock: { padding: 10, borderRadius: 8 },
  codeText: { fontSize: 12, fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace' },
});