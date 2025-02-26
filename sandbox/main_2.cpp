#include <Audio.h>
#include "base64.hpp"


// Définition des pins
#define BUTTON_PIN_SHOOT 9
#define BUTTON_PIN_PAUSE 5
#define POTENTIOMETER_DIVIDER 16
#define POTENTIOMETER_THRESHOLD 17
#define SD_CS_PIN 10

// Création des objets Audio pour Teensy 4.0
AudioPlaySdWav       play_menu, play_background, play_shoot, play_die;
AudioInputI2S        i2s1;
AudioAnalyzeFFT1024  fft;
AudioControlSGTL5000 audioShield;
AudioConnection      patchCord1(i2s1, 0, fft, 0);
AudioConnection      patchCord2(play_background, 0, audioShield, 0);
AudioConnection      patchCord3(play_background, 1, audioShield, 1);
AudioConnection      patchCord4(play_shoot, 0, audioShield, 0);
AudioConnection      patchCord5(play_shoot, 1, audioShield, 1);
AudioConnection      patchCord6(play_die, 0, audioShield, 0);
AudioConnection      patchCord7(play_die, 1, audioShield, 1);
AudioConnection      patchCord8(play_menu, 0, audioShield, 0);
AudioConnection      patchCord9(play_menu, 1, audioShield, 1);

// Déclaration des paramètres de traitement
float amplitude_max = 0.0;
float divider = 1000; // en Hz
float treshold = 0.5;
int button_shoot = 0;
int button_pause = 0;
int potentiometer_threshold = 0;
int potentiometer_divider = 0;

// Variables pour la gestion de la musique
bool was_playing = false;

// Variables pour test d'états 
bool lastShootState = HIGH;
bool lastPauseState = HIGH;

const float MIC_SENSITIVITY = 0.01;  // 10mV/Pa = 0.01V/Pa (exemple pour un micro bas de gamme)
const float REFERENCE_PRESSURE = 0.00002; // 20 µPa = 0.00002 Pa (seuil d'audition humain)

// 📌 Fréquence d'échantillonnage et résolution FFT :
const float SAMPLE_RATE = 44100.0;  // En Hz
const int FFT_SIZE = 1024;          // Nombre de points FFT

void setup() {
    pinMode(BUTTON_PIN_SHOOT, INPUT_PULLDOWN);
    pinMode(BUTTON_PIN_PAUSE, INPUT_PULLDOWN);
    AudioMemory(12); // Allouer de la mémoire audio
    Serial.begin(115200);
    audioShield.enable();
    audioShield.inputSelect(AUDIO_INPUT_MIC); // S'assurer que le micro est bien sélectionné
    audioShield.micGain(20); // Ajuster le gain du micro
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println("SD card initialization failed!");
        return;
    }
    Serial.println("SD card initialized.");
}

void playAudio(const char* filename) {
    
    if (filename == "shoot.wav") {
        if (play_shoot.isPlaying()) {
            play_shoot.stop();
        }
        play_shoot.play(filename);
    } else if (filename == "die.wav") {
        if (play_die.isPlaying()) {
            play_die.stop();
        }
        play_die.play(filename);
    } else if (filename == "main_menu.wav") {
        if (play_menu.isPlaying()) {
            play_menu.stop();
        }
        if (play_background.isPlaying()) {
            play_background.stop();
        }
        play_menu.play(filename);
        was_playing = false;
    } else if (filename == "shout2play.wav") {
        if (play_background.isPlaying()) {
            play_background.stop();
        }
        if (play_menu.isPlaying()) {
            play_menu.stop();
        }
        play_background.play(filename);
        was_playing = true;
    } else if(filename == "pause"){
        if (play_background.isPlaying()) {
            play_background.togglePlayPause();
        }
        if(wasplaying){
            play_menu.play("main_menu.wav");
        }
    } else if(filename == "resume"){
        if (play_menu.isPlaying()) {
            if(was_playing){
                play_menu.stop();
                play_background.togglePlayPause();
            }
        }
    }
}

void loop() {

    // ✅ 1. Lire le moniteur série pour savoir quel son jouer
    if (Serial.available()) {
        String message = Serial.readStringUntil('\n');
        
        // Jouer le son demandé
        playAudio(message.c_str());
    }

    // ✅ 2. Détecter la fréquence dominante avec FFT
    if (fft.available()) {
        float totalAmplitude = 0.0;
        float maxAmplitude = 0.0;
        float dominantFreq = 0.0;

        for (int i = 1; i < (FFT_SIZE / 2) - 1; i++) {
            float magnitude = fft.read(i);
            totalAmplitude += magnitude;

            if (magnitude > maxAmplitude) {
                maxAmplitude = magnitude;
                dominantFreq = i * (SAMPLE_RATE / FFT_SIZE);
            }
        }

        if (dominantFreq > 0) {
            float left = fft.read((int)(dominantFreq / (SAMPLE_RATE / FFT_SIZE)) - 1);
            float right = fft.read((int)(dominantFreq / (SAMPLE_RATE / FFT_SIZE)) + 1);
            if (right > left) {
                float correction = (right - left) / (2 * (2 * maxAmplitude - left - right));
                dominantFreq += correction * (SAMPLE_RATE / FFT_SIZE);
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


