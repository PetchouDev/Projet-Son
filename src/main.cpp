#include <Audio.h>
#include "base64.hpp"


// Définition des pins
#define BUTTON_PIN_SHOOT 0
#define BUTTON_PIN_PAUSE 1
#define POTENTIOMETER_PIN 2

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
const int FFT_SIZE = 1024;          // Nombre de points FFT


void check_button() {
  bool currentShootState = digitalRead(BUTTON_PIN_SHOOT);
  bool currentPauseState = digitalRead(BUTTON_PIN_PAUSE);

  if (lastShootState == HIGH && currentShootState == LOW) {
      Serial.println("{\"button_pressed_shoot\":1}");
  }
  if (lastShootState == LOW && currentShootState == HIGH) {
      Serial.println("{\"button_pressed_shoot\":0}");
  }
  
  if (lastPauseState == HIGH && currentPauseState == LOW) {
      Serial.println("{\"button_pressed_pause\":1}");
  }
  if (lastPauseState == LOW && currentPauseState == HIGH) {
      Serial.println("{\"button_pressed_pause\":0}");
  }
  lastShootState = currentShootState;
  lastPauseState = currentPauseState;
}

void send_serial(char *message){
  Serial.println(message);
}

void check_potentiometer_threshold(){
  int potentiometer = analogRead(POTENTIOMETER_PIN);
  treshold = 40 + (20 * potentiometer / 1023.0);
  Serial.println("{\"treshold\":" + String(treshold) + "}");
}

void check_potentiometer_divider(){
int potentiometer = analogRead(POTENTIOMETER_PIN);
divider = 800 + (400 * potentiometer / 1023.0);
Serial.println("{\"divider\":" + String(divider) + "}");
}

void setup() {
    pinMode(BUTTON_PIN_SHOOT, INPUT_PULLUP);
    pinMode(BUTTON_PIN_PAUSE, INPUT_PULLUP);
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
        
        // Création du message JSON
        String message = "{\"gain\":" + String(dbSPL, 2) + ",\"frequency\":" + String(dominantFreq, 2) + "}";

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

    // ✅ 3. Envoyer les états des boutons et des potentiomètres
    check_button();
    check_potentiometer_threshold();
    check_potentiometer_divider();

    delay(10);  // Petit délai pour éviter une surcharge de l'affichage
}


