# Mine Derien — Système de commande de trains miniatures

Réseau de trains miniatures « Mine Derien et Port Rienafer » (réf. `MD0809023`).
Le réseau était à l'origine piloté par un PC sous QBasic via le port parallèle.
Ce projet remplace ce PC par un **Arduino Mega 2560** qui pilote directement le
module électronique des trains, observé et configuré depuis une **UI Python** par
liaison série USB. Le matériel des trains (module, voie, câblage) reste inchangé.

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

Le **module électronique** des trains est conservé tel quel : on ne remplace que
l'ordinateur qui le pilotait.

---

## L'interface de commande

Le module attend les mêmes signaux que lui fournissait le port parallèle ; le Mega
les reproduit sur ses broches. Le câblage complet — broche Mega, signal, broche
DB25 d'origine, polarité — est dans **`pin_mapping.csv`**.

Quatre signaux :

- un **bus d'adresse** de 8 bits qui sélectionne une section ; son bit de poids
  fort distingue une *lecture* d'une *alimentation* ;
- une ligne de **verrou** qui valide l'adresse et déclenche l'action du module ;
- une ligne de **fin de transaction** ;
- une entrée **capteur** qui rapporte la présence d'un train dans la section
  sélectionnée.

Le verrou et la fin de transaction sont actifs à l'état bas. Le capteur est lui
aussi actif à l'état bas : pin à `LOW` ⇒ train détecté. Une transaction consiste
à poser une adresse, pulser le verrou, puis lire le capteur (scan) ou laisser le
module alimenter la section (énergisation).

### Séquence d'une énergisation

Énergiser la section *N* se fait en trois temps.

**1 — Pose de l'adresse.** Le firmware écrit la valeur `0x80 | N` sur les huit
broches du bus d'adresse. Les sept bits de poids faible portent le numéro de la
section ; le bit de poids fort, mis à 1, indique au module qu'il s'agit d'une
commande d'alimentation et non d'une lecture. Les deux lignes de contrôle —
verrou et fin de transaction — sont alors au repos, c'est-à-dire à l'état haut.

**2 — Verrou actif.** Le firmware abaisse la ligne de verrou. Sur ce front
descendant, le module échantillonne le bus d'adresse, reconnaît la commande
d'alimentation grâce au bit 7, et redirige le courant vers la section *N*. La
ligne de fin de transaction reste haute pendant tout ce temps : une énergisation
ne la sollicite jamais — c'est ce qui la distingue d'un scan ou d'une coupure.

**3 — Relâchement.** Le firmware ramène la ligne de verrou à l'état haut. Le
bus d'adresse reste piloté à `0x80 | N` après cette étape ; la section
demeure alimentée jusqu'à la prochaine transaction. C'est `deenergizeAllSections()`
dans le cycle PWM qui écrit l'adresse `0` (sans le bit d'alimentation) et pulse
cette fois la ligne de fin de transaction pour signaler au module de couper
toutes les sections.

Un **scan** suit la même ouverture — pose d'adresse (sans le bit 7) puis
abaissement du verrou — mais intercale une lecture du capteur de présence avant
le relâchement, et se termine par un pulse de la ligne de fin de transaction
qui signale au module que la lecture est terminée.

---

## Le firmware Arduino

Dans `arduino/src/`, en couches :

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
2. **Gating** : décider quelles sections alimenter (voir `gating.cpp`)
3. **Énergisation** des sections permises, puis délai ON
4. **Coupure** de toutes les sections, puis délai OFF
5. **Overdrive** : brèves impulsions par groupe

L'**overdrive** envoie après chaque cycle de brèves impulsions sur les trois
groupes de sections [0–7], [8–15], [16–36]. Ces impulsions donnent un coup de
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
| `TC_SENSE` | `0`/`1` | lit le capteur de présence (1 = train détecté) |
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

Le firmware est un projet **PlatformIO** dans `arduino/`. Sous CLion, ouvrir
le dossier `arduino/` avec le plugin PlatformIO ; la ligne de commande marche aussi :

```
pio run -d arduino                       # compile
pio run -d arduino -t upload             # téléverse sur le Mega
pio device monitor -d arduino            # ouvre le moniteur série

python -m venv python/.venv
python/.venv/bin/pip install -r python/requirements.txt
python/.venv/bin/python python/control_panel.py
```

Le port du Mega se retrouve avec `pio device list`. Un seul programme à la fois
peut ouvrir le port : fermer un outil avant d'en lancer un autre. Sous Linux,
l'utilisateur doit appartenir au groupe `dialout` pour accéder au port.

---

## Plan de test

### 1. Montage breadboard

On valide le firmware sans le module en simulant ses signaux :

| Broche | Composant | Simule |
|--------|-----------|--------|
| D22–D29 | 8 LEDs + résistance 220 Ω vers GND | le bus d'adresse |
| D30, D31 | 1 LED + 220 Ω chacune | les lignes de contrôle |
| D32 | switch entre GND et la broche, pull-up 10 kΩ vers +5 V | le capteur de présence |

> D30 et D31 sont **actives à l'état bas** : LED allumée = ligne au repos, LED
> éteinte = ligne active. C'est l'inverse de l'intuition. Pour un visuel direct,
> câbler ces deux LEDs vers +5 V au lieu de GND.

> Le capteur est lui aussi **actif à l'état bas** : switch fermé (broche à GND) =
> train détecté ; switch ouvert (pull-up à +5 V) = section vide.

### 2. Tests sur breadboard

Téléverser le sketch, puis dérouler via `gpio_test.py` :

| Commande | Attendu |
|----------|---------|
| `PING` | `PONG` ; la LED interne du Mega clignote |
| `SET 22 1` … `SET 29 1` | chaque LED du bus s'allume |
| `GET 32` | `0` switch fermé, `1` switch ouvert |
| `TC_ADDR 5 1` | LEDs D22, D24 et D29 (bit alimentation) allumées |
| `TC_LATCH` | D30 **s'éteint** (verrou actif) |
| `TC_RELEASE_ALL` | D30 et D31 allumées (repos) |
| `TC_SENSE` | `1` switch fermé, `0` switch ouvert |
| `SCAN 12` | même logique que `TC_SENSE` |
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

### 3. Branchement sur le module

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
6. **Cycle complet** — `AUTO_START 15 25`, les trains roulent.

---

## Programme d'origine

Le programme QBasic d'origine est conservé, commenté, dans
`initial_basic_program.bas` — référence pour la logique du réseau. Une ambiguïté
de précédence d'opérateurs y rendait la combinaison des règles de gating
incertaine ; le firmware exprime l'intention voulue plutôt que de la reproduire
littéralement.
