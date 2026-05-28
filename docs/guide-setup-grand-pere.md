# Guide d'installation — Mine Dérien

Ce guide explique comment installer tous les outils nécessaires pour travailler
sur le projet Mine Dérien. Le projet comporte deux parties :

- Un programme Python (sur l'ordinateur) qui sert d'interface de contrôle
- Un programme C++ (sur la carte Arduino) qui commande directement les trains

---

# Python et PyCharm

## C'est quoi Python?

Python est un langage de programmation. Concrètement, c'est une façon d'écrire
des instructions que l'ordinateur peut comprendre et exécuter.

Python est particulièrement populaire parce qu'il est facile à lire — sa syntaxe
ressemble presque à de l'anglais courant. C'est souvent le premier langage qu'on
apprend, et c'est aussi utilisé professionnellement dans des domaines comme la
science des données, les sites web, et l'automatisation.

Dans notre projet, Python sert à l'interface graphique : le panneau de contrôle
qui permet de surveiller les 37 sections du réseau et de démarrer le cycle
automatique des trains.

## Installer Python

1. Va sur le site officiel : https://www.python.org/downloads/
2. Clique sur le gros bouton jaune « Download Python » (prend la dernière version)
3. Lance l'installateur
4. **Important** : coche la case « Add Python to PATH » avant de cliquer sur
   « Install Now » — sans ça, l'ordinateur ne saura pas où trouver Python

Pour vérifier que l'installation a fonctionné, ouvre une invite de commandes
(cherche « cmd » dans le menu Démarrer) et tape :

```
python --version
```

Tu devrais voir quelque chose comme `Python 3.12.x`. Si oui, c'est bon.

## C'est quoi PyCharm?

PyCharm est un éditeur de code conçu spécialement pour Python. On l'appelle
un IDE (Integrated Development Environment — environnement de développement
intégré). Concrètement, c'est bien plus qu'un simple éditeur de texte :

- Il comprend le code Python et souligne les erreurs en temps réel
- Il complète automatiquement le code au fur et à mesure qu'on écrit
- Il intègre un terminal, un débogueur, et la gestion des bibliothèques
- Il est gratuit (version Community)

PyCharm est fait par la compagnie JetBrains. Cette même compagnie fait aussi
CLion (pour le code Arduino) — les deux outils ont exactement la même interface,
ce qui évite d'apprendre deux environnements différents.

## Installer PyCharm

1. Va sur https://www.jetbrains.com/pycharm/download/
2. Choisis **PyCharm Community Edition** (gratuit, colonne de droite)
3. Télécharge et lance l'installateur
4. Garde toutes les options par défaut, clique « Next » jusqu'à la fin

## Ouvrir le projet dans PyCharm

1. Lance PyCharm
2. Sur l'écran d'accueil, clique **Open**
3. Navigue jusqu'au dossier du projet `mine-derien` et clique **OK**
4. PyCharm va analyser le projet quelques secondes

Le projet contient un dossier `python/` avec tous les fichiers Python :

- `control_panel.py` — le panneau de contrôle graphique (c'est lui qu'on lance)
- `gpio_test.py` — un outil console pour envoyer des commandes manuelles
- `handshake.py` — vérifie que la connexion avec la carte fonctionne
- `serial_link.py` — la « plomberie » de la communication série (ne pas toucher)

## Créer l'environnement virtuel et installer les dépendances

Un **environnement virtuel** (venv) est un espace isolé où on installe les
bibliothèques Python du projet, sans mélanger avec le reste de l'ordinateur.
C'est une bonne pratique standard en Python.

**Étape 1 — Créer le venv**

Dans PyCharm, ouvre le terminal intégré (menu **View > Tool Windows > Terminal**)
et tape :

```
python -m venv python/.venv
```

Cela crée un dossier `.venv` dans le dossier `python/`.

**Étape 2 — Configurer PyCharm pour utiliser ce venv**

1. Va dans **File > Settings > Project > Python Interpreter**
2. Clique sur l'engrenage puis **Add Interpreter > Add Local Interpreter**
3. Choisis **Existing environment** et pointe vers `python/.venv/Scripts/python.exe`
4. Clique **OK**

**Étape 3 — Installer les dépendances**

Dans le terminal intégré :

```
python/.venv/Scripts/pip install -r python/requirements.txt
```

Cette commande lit le fichier `requirements.txt` (la liste des bibliothèques
nécessaires) et les installe automatiquement.

## Lancer le panneau de contrôle

Branche la carte Arduino Mega en USB, puis dans le terminal PyCharm :

```
python python/control_panel.py
```

Le panneau de contrôle s'ouvre. Si la carte n'est pas branchée, un message
d'erreur apparaît — c'est normal, branche-la d'abord.

---

# ATmega2560 et Arduino

## C'est quoi un microcontrôleur?

Un **microcontrôleur** est un tout petit ordinateur complet sur une seule puce
électronique. Il contient :

- Un processeur (qui exécute les instructions)
- De la mémoire (pour stocker le programme et les données)
- Des entrées/sorties numériques (des « pattes » qu'on peut piloter)

La grande différence avec un ordinateur ordinaire : un microcontrôleur est conçu
pour **contrôler du matériel électronique** en temps réel. Il n'a pas de système
d'exploitation, pas d'écran, pas de clavier. Il exécute un seul programme en
boucle, du moment où on l'allume jusqu'au moment où on l'éteint.

C'est pour ça qu'on en trouve partout dans les appareils du quotidien : four à
micro-ondes, machine à laver, télécommande, voiture, etc.

## C'est quoi un Arduino?

**Arduino** est une carte électronique qui contient un microcontrôleur, entourée
de tout ce qu'il faut pour le rendre facile à utiliser :

- Des connecteurs bien espacés pour brancher des fils facilement
- Un port USB pour le programmer depuis l'ordinateur
- Une petite LED et quelques boutons de base
- Un régulateur de tension (on peut l'alimenter avec n'importe quel câble USB)

Arduino est un projet **open-source** : les plans de la carte sont publics, et
n'importe qui peut en fabriquer. C'est devenu le standard pour les projets
électroniques d'amateurs et d'étudiants, justement parce que c'est simple
d'accès et bien documenté.

Il existe plusieurs modèles d'Arduino. Le plus courant est l'Arduino Uno. Nous,
on utilise l'**Arduino Mega 2560**.

## C'est quoi l'ATmega2560 — et pourquoi on l'utilise?

L'**ATmega2560** est la puce microcontrôleur qui se trouve sur la carte Arduino
Mega. C'est un composant fabriqué par Microchip Technology. Sa particularité :
il a **54 entrées/sorties numériques**, ce qui est beaucoup plus que l'Arduino
Uno (qui en a 14).

Pourquoi est-ce important pour notre projet? Le réseau Mine Dérien a **37
sections** électriques indépendantes, plus un bus de données de 8 fils, plus des
lignes de contrôle. On a besoin de beaucoup de pattes pour tout brancher. Un
Arduino Uno ne suffirait pas — la carte Mega, elle, a largement assez.

En pratique, quand on parle de « l'Arduino » dans ce projet, on parle de la
carte **Arduino Mega 2560**, qui contient la puce ATmega2560. Les deux noms
désignent souvent la même chose.

## C'est quoi PlatformIO — et pourquoi c'est mieux que l'IDE Arduino?

**L'IDE Arduino** est l'outil officiel fourni par Arduino pour écrire et
téléverser des programmes sur les cartes Arduino. C'est simple à installer,
mais il est assez limité : éditeur de code basique, peu d'aide à l'écriture,
interface vieillotte.

**PlatformIO** est un outil professionnel qui remplace l'IDE Arduino. Il fait
exactement la même chose (compiler et téléverser le firmware), mais en mieux :

- Il s'intègre directement dans CLion (et PyCharm) — même interface que pour
  Python, pas besoin d'apprendre un deuxième outil
- Autocomplétion du code beaucoup plus intelligente
- Gestion automatique des bibliothèques
- Support de centaines de cartes différentes (pas juste Arduino)
- Messages d'erreur plus clairs

C'est le choix standard dans les projets professionnels avec microcontrôleurs.

## Installer CLion

**CLion** est l'IDE de JetBrains pour le langage C/C++ — le même langage utilisé
pour programmer l'Arduino. Comme PyCharm (même compagnie), l'interface est
identique : si tu t'es habitué à PyCharm, CLion ne sera pas dépaysant.

1. Va sur https://www.jetbrains.com/clion/download/
2. Télécharge CLion (la version d'essai est gratuite 30 jours ; après, il faut
   une licence — vérifie avec Louis s'il y a une licence disponible)
3. Lance l'installateur, garde les options par défaut

## Installer le plugin PlatformIO dans CLion

1. Ouvre CLion
2. Va dans **File > Settings** (ou **CLion > Preferences** sur Mac)
3. Dans le menu de gauche, clique sur **Plugins**
4. Dans la barre de recherche, tape `PlatformIO`
5. Clique **Install** sur le plugin « PlatformIO for CLion »
6. Redémarre CLion quand il le demande

Au premier lancement après l'installation, CLion va proposer d'installer
PlatformIO Core (l'outil en ligne de commande). Accepte — il s'installe
automatiquement.

## Ouvrir le projet Arduino dans CLion

1. Lance CLion
2. Sur l'écran d'accueil, clique **Open**
3. Navigue jusqu'au dossier `mine-derien/arduino/` et clique **OK**
4. CLion lit le fichier `platformio.ini` (la configuration du projet) et
   configure tout automatiquement : carte, compilateur, bibliothèques

Le fichier `platformio.ini` indique à PlatformIO qu'on utilise un
`megaatmega2560` — il sait donc exactement comment compiler et téléverser
pour cette carte.

Les fichiers source sont dans le dossier `src/` :

- `main.cpp` — le point d'entrée du programme
- `track_controller.*` — la communication bas niveau avec le module des trains
- `sections.*`, `gating.*`, `cycle.*` — la logique de contrôle des sections
- `serial_commands.*` — les commandes reçues depuis le PC en Python
- `pins.h` — la liste des branchements

## Compiler et téléverser le firmware

**Brancher la carte** : connecte l'Arduino Mega au PC avec le câble USB.

**Compiler** (vérifier que le code est correct sans envoyer sur la carte) :
Dans CLion, clique sur le bouton **Build** (icône marteau) ou utilise
**Build > Build Project**.

**Téléverser** (envoyer le programme sur la carte) :
Dans la barre d'outils PlatformIO en haut de CLion, clique sur la flèche
**Upload** (►). CLion compile puis transfère le programme sur la carte.

Si le téléversement échoue avec une erreur de port, vérifie que :
1. La carte est bien branchée en USB
2. Aucun autre programme n'utilise le port (ferme le panneau Python d'abord)
3. Le port dans `platformio.ini` correspond au bon port COM (sur Windows,
   vérifiable dans le Gestionnaire de périphériques)
