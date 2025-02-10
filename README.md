https://docs.platformio.org/en/latest/platforms/teensy.html
https://inria-emeraude.github.io/son/
https://github.com/inria-emeraude/son

TEENSY : 
1. Enregistrer du son en direct
    1. Echantillonner
2. Convertir un son en vecteur (puissance, fréquence)
3. Enregistrer consigne bouton
4. Enregistrer consigne potentiometre

PYTHON : 
1. Pygame création fenêtre
2. Physique sol, personnages
    1. Mouvements généraux
3. Pause, score
    1. Distance parcourue +kills = score
    2. Pause = appui bouton
4. Fonction de tir
    1. Barre de charge
    2. Balle (vitesse)
    3. Kill/Destroy
5. Affichage sprites (perso, fond, ennemis, balle)
    1. Fond + nuage aléatoire + montagnes
    2. Mouvement perspectives
6. Musique de fond
    1. Réglage volume par consigne potentiomètre
    2. Envoi consignes de play soundboard on event

FONCTIONNEMENT MOUVEMENT : 
Voix -> gain ==> DGAIN = gain_voix-gain_voix_recorded_max   >0
Y_vector = DGAIN x facteur_puissance - GRAVITY x TIME_IN_AIR
LOAD += Voix -> freq/5(ou+)(+1 mode femme)
Vitesse défilement (potentiometre)



Homme : ≈ 80 Hz (basse) à 1 100 Hz (~C6, ténor aigu)
Femme : ≈ 165 Hz (alto) à 1 300 Hz (~E6, soprano aigu)