#include <Audio.h>
#include "base64.hpp"


// Définition des pins
#define BUTTON_PIN_SHOOT 9
#define BUTTON_PIN_PAUSE 5
#define POTENTIOMETER_DIVIDER 16
#define POTENTIOMETER_THRESHOLD 17

// Création des objets Audio pour Teensy 4.1
AudioInputI2S        i2s1;
AudioAnalyzeFFT1024  fft;
AudioAnalyzePeak     peak;
AudioControlSGTL5000 audioShield;
AudioConnection      patchCord1(i2s1, 0, fft, 0);
AudioConnection      patchCord2(i2s1, 0, peak, 0);



float amplitude_max = 0.0;

// Déclaration des variables
float divider = 1000; // en Hz
float treshold = 0.5;
int button_shoot = 0;
int button_pause = 0;
int potentiometer_threshold = 0;
int potentiometer_divider = 0;

// Variables pour test d'états 
bool lastShootState = HIGH;
bool lastPauseState = HIGH;

const float MIC_SENSITIVITY = 0.01;  // 10mV/Pa = 0.01V/Pa (exemple pour un micro bas de gamme)
const float REFERENCE_PRESSURE = 0.00002; // 20 µPa = 0.00002 Pa (seuil d'audition humain)

// 📌 Fréquence d'échantillonnage et résolution FFT :
const float SAMPLE_RATE = 44100.0;  // En Hz
const int FFT_SIZE = 2048;          // Nombre de points FFT

void setup() {
    pinMode(BUTTON_PIN_SHOOT, INPUT_PULLDOWN);
    pinMode(BUTTON_PIN_PAUSE, INPUT_PULLDOWN);
    AudioMemory(12); // Allouer de la mémoire audio
    Serial.begin(115200);
    audioShield.enable();
    audioShield.inputSelect(AUDIO_INPUT_MIC); // S'assurer que le micro est bien sélectionné
    audioShield.micGain(20); // Ajuster le gain du micro
}

void loop() {

    // ✅ 2. Détecter la fréquence dominante avec FFT
    if (fft.available()) {
        float totalAmplitude = 0.0;
        float maxAmplitude = 0.0;
        float dominantFreq = 0.0;

        for (int i = 0; i < (FFT_SIZE / 2); i++) {  // On ne prend que les fréquences utiles (0 - Nyquist)
            float magnitude = fft.read(i);
            totalAmplitude += magnitude;
            
            if (magnitude > maxAmplitude) {
                maxAmplitude = magnitude;
                dominantFreq = i * (SAMPLE_RATE / FFT_SIZE); // Convertir en Hz
            }
        }

        float avgAmplitude = totalAmplitude / (FFT_SIZE / 2);
        float pressure = avgAmplitude / MIC_SENSITIVITY;  // Convertir en Pascals
        float dbSPL = 20.0 * log10(max(pressure, REFERENCE_PRESSURE) / REFERENCE_PRESSURE);

        int divider = 800 + (400 * analogRead(POTENTIOMETER_DIVIDER) / 1023.0);
        int threshold = 30 + (60 * analogRead(POTENTIOMETER_THRESHOLD) / 1023.0);
        
        // Création du message JSON
        String message = "{";
        message += "\"gain\":" + String(dbSPL, 2);
        message += ",\"frequency\":" + String(dominantFreq, 2);
        message += ",\"button_pressed_shoot\":" + String(digitalRead(BUTTON_PIN_SHOOT));
        message += ",\"button_pressed_pause\":" + String(digitalRead(BUTTON_PIN_PAUSE));
        message += ",\"divider\":" + String(divider);
        message += ",\"threshold\":" + String(threshold);
        message += "}";

        // Conversion en tableau de char
        size_t msgLen = message.length();
        char msgBuffer[msgLen + 1];
        message.toCharArray(msgBuffer, msgLen + 1);

        // Encodage Base64
        size_t b64Len = encode_base64_length(msgLen);
        char b64Buffer[b64Len];
        encode_base64(msgBuffer, msgLen, b64Buffer);

        // Envoi du message
        Serial.println(b64Buffer);
    }

    delay(10);  // Petit délai pour éviter une surcharge de l'affichage
}


