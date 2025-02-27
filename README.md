# Shout2Play

## Introduction

Ce dépôt constitue notre proposition pour le projet SON dans le cadre de notre formation en 3ème année à l’INSA Lyon, au sein du département Télécommunications, Services & Usages. 

Shout2Play est un jeu de plateforme de type runner, dans lequel le joueur incarne un canard et doit crier afin de le faire progresser dans un monde généré aléatoirement. 

Nous avons fait de notre mieux pour proposer au joueur une expérience à la fois ludique et scientifique, tout en mettant à profit les savoir-faire acquis lors de notre formation. 

## Contenu du dépôt

Ce dépôt est divisé en deux parties principales :
- `src`: le code embarqué sur le Teensy
- `Shout2Play`: le code du jeu (basé sur Python3 et PyGame)

Ainsi que de `lib` et `include`, qui rassemblent les dépendances du programme embarqué.

## Vidéo démonstrative

<iframe width="681" height="511" src="https://www.youtube.com/embed/QVXOtM6kn_g" title="Shout2Play - Hurler, c’est gagner ! - Présentation du projet SON par @nocturios et @petchoudev" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Si la vidéo ne s'affiche pas, elle reste disponible [ici](https://www.youtube.com/watch?v=QVXOtM6kn_g)

## Comment jouer ?

1. Réaliser le montage suivant sur le bloc Teensy + AudioShield

![](assets/shout2play.drawio.svg)

2. Brancher microphone et casque audio sur les ports prévus à cet effet (peut requérir de souder le port microphone).

3. Cloner ce repo et l'ouvrir dans VS Code
4. Télécharger l'extension PlatformIO et l'Arduino IDE et ajouter le manifeste [TeensyDuino](https://www.pjrc.com/teensy/td_download.html)
5. Compiler et uploader le projet vers la carte (PlatformIO devrait la détecter automatiquement)
6. Installer les dépendances python `pip install -r requirements.txt`
7. Executer le script `python3 Shout2Play/main.py`
8. Crier

## Extras

- [Poster scientifique du projet](assets/Shout%202%20Play%20V2.pdf)
- [BO du jeu](assets/Shout2Play.wav)

## Remerciements

Merci à :
- Romain Michon, pour son cours et son support tout au long du projet
- Toute l'équipe pédagogique, pour leur aide et leurs précieux conseils
- Lise et Amina, pour leur aide pour la lecture de médias (et leur patience)
- La classe de 3TCA, pour le climat d'entraide et la bonne humeur au quotidien
  


<br><br>
> Willam et Mathéo
