import React from 'react';
import { SafeAreaView, StyleSheet, Platform } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { WebView } from 'react-native-webview';

export default function App() {
  return (
    <>
      <StatusBar style="dark" />
      <SafeAreaView style={styles.container}>
        <WebView
          source={{ uri: 'http://YOUR_MACHINE_IP:8000' }}
          style={styles.webview}
          startInLoadingState={true}
          originWhitelist={['*']}
        />
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginTop: Platform.OS === 'android' ? StatusBar.currentHeight || 25 : 0,
  },
  webview: {
    flex: 1,
  },
});

