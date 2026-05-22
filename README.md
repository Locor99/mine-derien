# Mine Derien — Système de commande de trains miniatures

Réseau de trains miniatures « Mine Derien et Port Rienafer » (réf. `MD0809023`),
conçu en 2008–2009 par un ingénieur électrique. Le réseau était piloté par un PC
sous QBasic via le port parallèle ; ce PC est aujourd'hui hors d'usage.

Ce projet remplace le PC par un **Arduino Mega 2560** qui pilote directement le
module électronique des trains, observé et configuré depuis une **UI Python** par
liaison série USB. Le matériel des trains (module, voie, câblage) reste inchangé.

**État courant : phase A terminée.** Le firmware reproduit toute la logique du
programme d'origine et a été développé par étapes testables sur breadboard.
Reste à valider sur le vrai module (voir *Plan de test*).

---

## Le réseau et son module

La voie utilise deux rails :

| Rail | Rôle |
|------|------|
| A | 12 V constant (alimentation des moteurs) |
| B | relié au module électronique (contrôle PWM) |

La voie est divisée en **37 sections** (indices 0–36) électriquement isolées,
alimentées individuellement. Quand un train occupe une section, son moteur crée
un chemin de retour du courant vers le rail B ; le module détecte cette présence
et la rapporte sous forme d'un bit par section.

Le **module électronique** de Roger est conservé tel quel. On ne remplace que
l'ordinateur qui le pilotait.

---

## L'interface de commande

Le module attend les mêmes signaux que lui fournissait le port parallèle. Le Mega
les reproduit sur ses broches. Câblage complet dans `pin_mapping.csv`.

| Broche Mega | Signal | Rôle |
|-------------|--------|------|
| D22–D29 | bus d'adresse (8 bits) | sélectionne une section ; le bit 7 (D29) distingue *lecture* (0) et *alimentation* (1) |
| D30 | verrou | valide l'adresse et déclenche l'action du module — **actif à l'état bas** |
| D31 | fin de transaction | clôt une transaction — **actif à l'état bas** |
| D32 | capteur | entrée : présence d'un train dans la section sélectionnée |

Une transaction = poser une adresse sur le bus, pulser le verrou, puis lire le
capteur (scan) ou laisser le module alimenter la section (énergisation).

---

## Le firmware Arduino

Dans `arduino/mine_derien/`, en couches :

| Fichier | Rôle |
|---------|------|
| `track_controller.*` | interface bas niveau au module ; encapsule les broches et les polarités |
| `sections.*` | opérations par section : scan, énergiser, désénergiser, overdrive |
| `gating.*` | règles décidant quelles sections alimenter |
| `cycle.*` | boucle PWM automatique non bloquante |
| `timing.*` | conversion fréquence/duty → délais ON/OFF |
| `serial_commands.*` | protocole ASCII sur USB |
| `pins.h` | constantes de câblage |

### La logique de contrôle

Le cycle automatique répète, sans bloquer la liaison série (machine à états sur
`micros()`) :

1. **Scan** des 37 sections → mise à jour de l'état de présence
2. **Gating** : décider quelles sections alimenter
3. **Énergisation** des sections permises, puis délai ON
4. **Coupure** de toutes les sections, puis délai OFF
5. **Overdrive** : brèves impulsions par groupe

**Gating** — deux familles de règles :
- *Zones lentes* : les sections 0, 1, 2, 7, 14 sont sautées un cycle sur neuf,
  ce qui ralentit les trains qui y passent.
- *Anti-collision* : sections 0, 1, 2, 7 coupées si un train occupe la 8 ;
  jonctions 8 et 15 coupées si un train approche (sections 0–3) ; section 14
  coupée si un train occupe la 2 ou la 3.

Le programme QBasic d'origine avait ici une ambiguïté de précédence d'opérateurs ;
le firmware exprime l'intention voulue plutôt que de la reproduire.

**Overdrive** — après chaque cycle, de brèves impulsions sont envoyées sur les
trois groupes de sections [0–7], [8–15], [16–36]. Elles donnent un coup de
courant supplémentaire pour empêcher les trains de caler dans les courbes, où la
friction est plus forte.

---

## Le protocole série

Commandes ASCII terminées par un retour de ligne, à 115200 bauds. Chaque commande
renvoie une ligne de réponse.

| Commande | Réponse | Rôle |
|----------|---------|------|
| `PING` | `PONG` | test de liaison |
| `SET <pin> <0\|1>` | `OK` | pilote une sortie brute |
| `GET <pin>` | `0`/`1` | lit une entrée brute |
| `TC_ADDR <section> <0\|1>` | `OK` | pose une adresse (2e arg = bit alimentation) |
| `TC_LATCH` / `TC_END` / `TC_RELEASE_ALL` | `OK` | pilote les lignes de contrôle |
| `TC_SENSE` | `0`/`1` | lit le capteur de présence |
| `SCAN <n>` | `0`/`1` | scanne une section |
| `ENERGIZE <n>` | `OK` | alimente une section |
| `DEENERGIZE_ALL` | `OK` | coupe toutes les sections |
| `OVERDRIVE <n>` | `OK` | impulsion d'overdrive sur une section |
| `GET_STATE` | 10 hex | état de présence des 37 sections |
| `FORCE_PRESENT <n> <0\|1>` | `OK` | force l'état d'une section (test du gating) |
| `RESET_FORCED` | `OK` | annule tous les forçages |
| `AUTO_START <Hz> <%>` | `OK` | démarre le cycle automatique |
| `AUTO_STOP` | `OK` | arrête le cycle |

---

## Les outils Python

Dans `python/`. Tous détectent le port du Mega automatiquement, ou l'acceptent
en argument.

- **`control_panel.py`** — UI graphique. Onglet *Test* : contrôle manuel section
  par section. Onglet *Auto* : démarre le cycle et affiche l'état des 37 sections
  en direct. Même UI sur breadboard et sur le vrai module.
- **`gpio_test.py`** — console série : envoie n'importe quelle commande au Mega.
  L'outil principal pour dérouler le plan de test.
- **`handshake.py`** — vérifie la liaison (`PING`/`PONG`).
- **`serial_link.py`** — client série partagé par les outils ci-dessus.

---

## Build et exécution

```
arduino-cli compile --fqbn arduino:avr:mega arduino/mine_derien
arduino-cli upload  --fqbn arduino:avr:mega -p /dev/ttyACM0 arduino/mine_derien

python -m venv python/.venv
python/.venv/bin/pip install -r python/requirements.txt
python/.venv/bin/python python/control_panel.py
```

Le port du Mega se retrouve avec `arduino-cli board list`. Un seul programme à la
fois peut ouvrir le port : fermer un outil avant d'en lancer un autre. Sous Linux,
l'utilisateur doit appartenir au groupe `dialout` pour accéder au port.

---

## Plan de test

### 1. Montage breadboard

On valide le firmware sans le module de Roger en simulant ses signaux :

| Broche | Composant | Simule |
|--------|-----------|--------|
| D22–D29 | 8 LEDs + résistance 220 Ω vers GND | le bus d'adresse |
| D30, D31 | 1 LED + 220 Ω chacune | les lignes de contrôle |
| D32 | switch entre +5 V et la broche, pull-down 10 kΩ vers GND | le capteur de présence |

> D30 et D31 sont **actives à l'état bas** : LED allumée = ligne au repos, LED
> éteinte = ligne active. C'est l'inverse de l'intuition. Pour un visuel direct,
> câbler ces deux LEDs vers +5 V au lieu de GND.

### 2. Tests sur breadboard

Téléverser le sketch, puis dérouler via `gpio_test.py` :

| Commande | Attendu |
|----------|---------|
| `PING` | `PONG` ; la LED interne du Mega clignote |
| `SET 22 1` … `SET 29 1` | chaque LED du bus s'allume |
| `GET 32` | suit le switch (0 ouvert / 1 fermé) |
| `TC_ADDR 5 1` | LEDs D22, D24 et D29 (bit alimentation) allumées |
| `TC_LATCH` | D30 **s'éteint** (verrou actif) |
| `TC_RELEASE_ALL` | D30 et D31 allumées (repos) |
| `TC_SENSE` | suit le switch |
| `SCAN 12` | suit le switch |
| `ENERGIZE 5` | LEDs montrant `0x85` |
| `DEENERGIZE_ALL` | bus à zéro |
| `AUTO_START 2 50` | D29 clignote lentement, visible à l'œil |
| `GET_STATE` | 10 caractères hexadécimaux |
| `AUTO_STOP` | le cycle s'arrête |

Puis ouvrir `control_panel.py` : onglet *Test* (scan/énergiser par section),
onglet *Auto* (démarrer le cycle, grille rafraîchie en direct).

Le gating se vérifie avec `FORCE_PRESENT` : forcer une présence puis lire
`GET_STATE`. Son effet visible (sections sautées) ne se constate qu'avec de
vrais trains — le balayage d'énergisation est trop rapide pour les LEDs.

### 3. Transition vers le module de Roger

1. **Câblage** — remplacer le breadboard par le câble vers le module, selon les
   colonnes `Legacy_signal` / `DB25_pin` de `pin_mapping.csv`. Ajouter une
   résistance série de 1 kΩ sur la ligne du capteur (D32) comme protection.
2. **Polarités** — vérifier l'hypothèse « actif à l'état bas » de D30/D31. Si le
   module ne réagit pas, inverser `MODULE_ACTIVE_LEVEL` dans `track_controller.cpp`.
3. **Smoke test** — poser un train sur une section connue, `SCAN <n>` doit
   renvoyer `1`.
4. **Énergisation** — `ENERGIZE <n>` doit faire bouger le train (ou alimenter le
   moteur, mesurable au multimètre).
5. **Timing** — si le module ne verrouille pas l'adresse, le pulse de verrou est
   peut-être trop court ; ajouter un `delayMicroseconds()` dans `track_controller`.
6. **Cycle complet** — `AUTO_START 15 25` (paramètres historiques), les trains
   roulent.

---

## Programme d'origine

Le programme QBasic d'origine est conservé, commenté, dans
`initial_basic_program.bas` — référence pour la logique du réseau.
