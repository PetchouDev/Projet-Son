/**
 * @file main.cpp
 * @brief Programme de gestion audio pour un projet utilisant un micro et une carte SD.
 * 
 * Ce fichier contient le code pour gérer la lecture de fichiers audio depuis une carte SD,
 * analyser les fréquences audio avec une FFT, et envoyer des données au moniteur série.
 * 
 * @details
 * - Les pins pour les boutons et potentiomètres sont définis.
 * - Les objets pour la lecture audio, le mélangeur, les entrées/sorties audio, et l'analyseur FFT sont déclarés.
 * - Les connexions audio sont établies entre les différents composants.
 * - Les paramètres de traitement audio sont initialisés.
 * - Les fonctions setup() et loop() gèrent l'initialisation et la boucle principale du programme.
 * - La fonction playAudio() permet de jouer, arrêter ou mettre en pause des fichiers audio spécifiques.
 * - La boucle principale lit les commandes du moniteur série, détecte les fréquences dominantes avec la FFT,
 *   et envoie les données encodées en Base64 au moniteur série.
 * 
 * @note
 * - Assurez-vous que la carte SD est correctement insérée et initialisée.
 * - Les fichiers audio doivent être présents sur la carte SD avec les noms corrects.
 * - Les potentiomètres et boutons doivent être connectés aux pins définis.
 * 
 * @author
 * - Développeur : Nocturios & PetchouDev
 * 
 * @date
 * - Date de création : 2024-02-16
 * 
 * @version
 * - Version : 1.0
 */
#include <Audio.h>
#include "base64.hpp"
#include <SD.h>

// Définition des pins
#define BUTTON_PIN_SHOOT 9
#define BUTTON_PIN_PAUSE 5
#define POTENTIOMETER_DIVIDER 16
#define POTENTIOMETER_THRESHOLD 17
#define SD_CS_PIN 10

// Déclaration des pistes de lecture audio
AudioPlaySdWav       play_menu; 
AudioPlaySdWav       play_background;
AudioPlaySdWav       play_shoot;
AudioPlaySdWav       play_die;

// Déclaration du mélangeur audio
AudioMixer4          mixer; 

// Déclaration des entrées/sorties audio
AudioInputI2S        i2s1;
AudioOutputI2S       i2s2;

// Déclaration de l'analyseur FFT
AudioAnalyzeFFT1024  fft;

// Déclaration du shield audio
AudioControlSGTL5000 audioShield;

// Connexions audio
AudioConnection      patchCord1(i2s1, 0, fft, 0);               // Connecter l'entrée audio à l'analyseur FFT

AudioConnection      patchCord2(play_background, 0, mixer, 0);  // Connecter les pistes audio au mélangeur
AudioConnection      patchCord4(play_shoot, 0, mixer, 1);       // Connecter les pistes audio au mélangeur
AudioConnection      patchCord6(play_die, 0, mixer, 2);         // Connecter les pistes audio au mélangeur
AudioConnection      patchCord8(play_menu, 0, mixer, 3);        // Connecter les pistes audio au mélangeur

AudioConnection      patchCord10(mixer, 0, i2s2, 0);            // Connecter le mélangeur à la sortie audio (canal gauche)
AudioConnection      patchCord11(mixer, 0, i2s2, 1);            // Connecter le mélangeur à la sortie audio (canal droit)

// Déclaration des paramètres de traitement
float amplitude_max = 0.0;
float divider = 1000;
float treshold = 0.5;
int button_shoot = 0;
int button_pause = 0;
int potentiometer_threshold = 0;
int potentiometer_divider = 0;

// Variables pour la gestion de la musique
bool was_playing = false;
bool is_paused   = false;

// Variables pour test d'états 
bool lastShootState = HIGH;
bool lastPauseState = HIGH;

const float MIC_SENSITIVITY = 0.01;       // 10mV/Pa = 0.01V/Pa (exemple pour un micro bas de gamme)
const float REFERENCE_PRESSURE = 0.00002; // 20 µPa = 0.00002 Pa (seuil d'audition humain)

// Fréquence d'échantillonnage et résolution FFT :
const float SAMPLE_RATE = 44100.0;  // En Hz
const int FFT_SIZE = 1024;          // Nombre de points FFT



/**
 * @brief Configuration initiale du système.
 * 
 * Cette fonction configure les broches des boutons, initialise la mémoire audio,
 * configure le port série, active le bouclier audio, sélectionne l'entrée audio,
 * ajuste le volume et le gain du micro, initialise la carte SD et configure les gains du mixeur.
 * 
 * @details
 * - Configure les broches des boutons avec une résistance de tirage vers le bas.
 * - Alloue 40 blocs de mémoire pour l'audio.
 * - Initialise la communication série à 115200 bauds.
 * - Active le bouclier audio et sélectionne le micro comme entrée audio.
 * - Ajuste le volume du bouclier audio à 60%.
 * - Ajuste le gain du micro à 20 dB.
 * - Initialise la carte SD et vérifie si l'initialisation a réussi.
 * - Configure les gains des quatre canaux du mixeur.
 * 
 * @note Si l'initialisation de la carte SD échoue, un message d'erreur est affiché et la fonction retourne.
 */
void setup() {

    // Configuration des broches
    pinMode(BUTTON_PIN_SHOOT, INPUT_PULLDOWN);
    pinMode(BUTTON_PIN_PAUSE, INPUT_PULLDOWN);

    // Initialisation de la mémoire audio
    AudioMemory(40);

    // Initialisation de la communication série
    Serial.begin(115200);

    // Activation de l'audio shield
    audioShield.enable();
    audioShield.volume(0.6);                    // Ajuster le volume
    audioShield.inputSelect(AUDIO_INPUT_MIC);   // S'assurer que le micro est bien sélectionné
    audioShield.micGain(20);                    // Ajuster le gain du micro

    // Initialisation de la carte SD
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println("SD card initialization failed!");
        return;
    }

    // Configuration des gains du mixeur (musiques d'arrière plan et effets sonores)
    mixer.gain(0, 0.5);
    mixer.gain(1, 1.0);
    mixer.gain(2, 1.0);
    mixer.gain(3, 0.5);
    Serial.println("SD card initialized.");
}

/**
 * @brief Joue un fichier audio en fonction du nom de fichier fourni.
 * 
 * Cette fonction gère la lecture de différents sons en fonction du nom de fichier
 * passé en paramètre. Elle peut jouer des sons spécifiques, mettre en pause, 
 * reprendre ou arrêter la musique de fond, et jouer le son du menu principal.
 * 
 * @param filename_str Le nom du fichier audio à jouer ou une commande spéciale 
 *                     comme "init", "pause", "resume" ou "stop".
 * 
 * Commandes spéciales :
 * - "init" : Arrête tous les sons et joue le son du menu principal.
 * - "shoot.wav" : Joue le son de tir.
 * - "die.wav" : Joue le son de mort.
 * - "pause" : Met en pause la musique de fond et joue le son du menu principal.
 * - "resume" : Reprend la musique de fond ou joue un son spécifique si aucun son n'était en pause.
 * - "stop" : Arrête tous les sons.
 */
void playAudio(String filename_str) {

    // Conversion de la chaîne en tableau de caractères (nécessaire pour appeler play())
    const char* filename = filename_str.c_str();

    // Initialisation du jeu
    if (filename_str == "init") {

        // Stopper tous les sons
        play_menu.stop();
        play_background.stop();
        play_shoot.stop();
        play_die.stop();

        // Réinitialiser les variables
        was_playing = false;

        // Petit délai pour éviter les interférences
        delay(10);

        // Jouer le son de démarrage
        play_menu.play("main_menu.wav");

        // Logger le message
        Serial.println("Playing main_menu.wav");

    // Son de tir
    } if (filename_str == "shoot.wav") {

        play_shoot.play(filename);
        Serial.println("Playing shoot.wav");
    
    // Son de mort
    } else if (filename_str == "die.wav") {
        
        play_die.play(filename);
        Serial.println("Playing die.wav");

    // Pause de la musique de fond (avec sauvegarde du progrès dans play_background)
    } else if(filename_str == "pause"){

        // Si la musique de fond est en cours de lecture
        if (play_background.isPlaying()) {

            // Mettre en pause la musique de fond
            play_background.togglePlayPause();

            // Se souvenir que la musique était en cours de lecture
            was_playing = true;

            Serial.println("Pausing background music");

            // Jouer le son du menu principal
            play_menu.play("main_menu.wav");

            Serial.println("Playing main_menu.wav");
        }
        
    // Reprendre la musique de fond
    } else if(filename_str == "resume"){

        // Si on était en pause,, on stoppe le son du menu principal
        if (play_menu.isPlaying()) {

            play_menu.stop();
            Serial.println("Stopping main_menu.wav");

        }

        // Si la musique de fond était en pause, on la reprend
        if(was_playing){

            play_background.togglePlayPause();
            Serial.println("Resuming background music");

        // Sinon, on la joue depuis le début
        } else {

            play_background.play("shout2play.wav");
            Serial.println("Playing shout2play.wav");

        }
        
        // On réinitialise la variable
        was_playing = false;

    // Arrêter tous les sons
    } else if (filename_str == "stop") {

        if (play_background.isPlaying()) {

            play_background.stop();
            Serial.println("Stopping background music");

        }
        if (play_menu.isPlaying()) {

            play_menu.stop();
            Serial.println("Stopping main_menu.wav");

        }
        
        // Réinitialiser les variables
        was_playing = false;
    }
}

/**
 * Boucle principale du programme.
 * 
 * 1. Lit le moniteur série pour savoir quel son jouer.
 *    - Si des données sont disponibles sur le port série, lit le message et joue le son correspondant.
 * 
 * 2. Détecte la fréquence dominante avec FFT.
 *    - Si des données FFT sont disponibles, calcule l'amplitude totale et la fréquence dominante.
 *    - Ajuste la fréquence dominante détectée en fonction des amplitudes voisines.
 * 
 * 3. Calcule la pression acoustique en dB SPL.
 *    - Calcule l'amplitude moyenne et la convertit en pression acoustique.
 *    - Convertit la pression acoustique en dB SPL.
 * 
 * 4. Lit les valeurs des potentiomètres et des boutons.
 *    - Lit les valeurs des potentiomètres pour le diviseur et le seuil.
 *    - Lit l'état des boutons de tir et de pause.
 * 
 * 5. Crée un message JSON avec les données collectées.
 *    - Formate les données en une chaîne JSON.
 * 
 * 6. Convertit le message JSON en tableau de caractères.
 *    - Convertit la chaîne JSON en un tableau de caractères.
 * 
 * 7. Encode le message en Base64.
 *    - Encode le tableau de caractères en Base64.
 * 
 * 8. Envoie le message encodé sur le port série.
 *    - Envoie le message encodé en Base64 sur le port série.
 * 
 * Attente de 10 ms pour éviter les interférences et la surcharge du processeur.
 */
void loop() {

    // 1. Lire le moniteur série pour savoir quel son jouer
    if (Serial.available()) {
        String message = Serial.readStringUntil('\n');
        
        // Jouer le son demandé
        playAudio(message.c_str());
    }

    // 2. Détecter la fréquence dominante avec FFT
    if (fft.available()) {
        float totalAmplitude = 0.0;
        float maxAmplitude = 0.0;
        float dominantFreq = 0.0;
        
        // Parcours des fréquences détectées
        for (int i = 1; i < (FFT_SIZE / 2) - 1; i++) {
            float magnitude = fft.read(i);
            totalAmplitude += magnitude;

            if (magnitude > maxAmplitude) {
                maxAmplitude = magnitude;
                dominantFreq = i * (SAMPLE_RATE / FFT_SIZE);
            }
        }
        
        // Si la fréquence dominante est détectée, ajuster la fréquence
        if (dominantFreq > 0) {
            float left = fft.read((int)(dominantFreq / (SAMPLE_RATE / FFT_SIZE)) - 1);
            float right = fft.read((int)(dominantFreq / (SAMPLE_RATE / FFT_SIZE)) + 1);
            if (right > left) {
                float correction = (right - left) / (2 * (2 * maxAmplitude - left - right));
                dominantFreq += correction * (SAMPLE_RATE / FFT_SIZE);
            }
        }

        // 3. Calcul de la pression acoustique en dB SPL
        float avgAmplitude = totalAmplitude / (FFT_SIZE / 2);
        float pressure = avgAmplitude / MIC_SENSITIVITY;  // Convertir en Pascals
        float dbSPL = 20.0 * log10(max(pressure, REFERENCE_PRESSURE) / REFERENCE_PRESSURE);

        // 4. Lire les valeurs des potentiomètres et des boutons
        int divider = 800 + (400 * analogRead(POTENTIOMETER_DIVIDER) / 1023.0);
        int threshold = 30 + (60 * analogRead(POTENTIOMETER_THRESHOLD) / 1023.0);
        
        // 5. Création du message JSON
        String message = "{";
        message += "\"gain\":" + String(dbSPL, 2);
        message += ",\"frequency\":" + String(dominantFreq, 2);
        message += ",\"button_pressed_shoot\":" + String(digitalRead(BUTTON_PIN_SHOOT));
        message += ",\"button_pressed_pause\":" + String(digitalRead(BUTTON_PIN_PAUSE));
        message += ",\"divider\":" + String(divider);
        message += ",\"threshold\":" + String(threshold);
        message += "}";

        // 6. Conversion en tableau de char
        size_t msgLen = message.length();
        char msgBuffer[msgLen + 1];
        message.toCharArray(msgBuffer, msgLen + 1);

        // 7. Encodage Base64
        size_t b64Len = encode_base64_length(msgLen);
        char b64Buffer[b64Len];
        encode_base64(msgBuffer, msgLen, b64Buffer);

        // 8. Envoi du message
        Serial.println(b64Buffer);
    }

    // Attendre un peu pour éviter les interférences et la surcharge du processeur
    delay(10); 
}
