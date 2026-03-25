# Mine Derien — Système de commande de trains miniatures

Projet développé par un ingénieur électrique pour contrôler un réseau de trains miniatures via port parallèle depuis un PC sous QBasic. Le code original (`initial_basic_program.bas`) date de 2008–2009 (référence interne `MD0809023`).

L'objectif actuel est de moderniser la plateforme logicielle et matérielle côté ordinateur, tout en conservant l'interface parallèle existante côté trains.

---

## Architecture matérielle

### Voie ferrée — deux rails

| Rail | Rôle |
|------|------|
| Rail A | 12V constant (alimentation) |
| Rail B | Connecté au module électronique (contrôle PWM) |

Quand un train est présent dans une section, son moteur crée un chemin de retour du courant vers le rail B. Cette chute de courant est détectée électroniquement et lue par le port parallèle comme un état binaire (train présent / absent).

### 37 sections de voie (indices 0–36)

Chaque section est un segment de voie électriquement isolé, alimenté ou non individuellement. L'état de chaque section est stocké dans le tableau `BO(N)` :

- `BO(N) = 1` → train présent dans la section N
- `BO(N) = 0` → section vide

### Interface port parallèle (LPT1 — adresses 0x378 à 0x37A)

| Registre | Adresse décimale | Direction | Rôle |
|----------|-----------------|-----------|------|
| Data     | 888 (0x378)     | OUT       | Sélectionne la section (0–36) ou l'énergise (128+N) |
| Status   | 889 (0x379)     | IN        | Lit la présence d'un train (bit 3) |
| Control  | 890 (0x37A)     | OUT       | Séquence de contrôle (0, 1, 2) |

#### Encodage du registre Data

Le bit 7 du byte envoyé sur le registre Data distingue deux modes :

- **Valeur 0–127** → sélection d'une section pour lecture (7 bits suffisent pour couvrir 0–36)
- **Valeur 128–164** → alimentation de la section N, où `N = valeur - 128`

`128 = 0b10000000` : le bit 7 allumé signifie "commande d'alimentation" au module électronique.

#### Séquence de détection d'un train dans la section N

```basic
OUT 888, N      ' sélectionner la section
OUT 890, 1      ' pulse : déclencher la lecture
ETAT = INP(889) ' lire le registre Status
BO(N) = ETAT / 8 AND 1  ' extraire le bit 3
OUT 890, 0      ' reset
OUT 890, 2      ' reset
```

`ETAT / 8` décale le byte de 3 bits vers la droite. `AND 1` isole le bit 3, qui indique la présence du train.

#### Séquence d'alimentation de la section N

```basic
OUT 888, 128 + N   ' bit 7 = 1 → commande alimentation
OUT 890, 1
OUT 890, 0
```

---

## Contrôle PWM (software)

La vitesse des trains est contrôlée par modulation de largeur d'impulsion (PWM) implémentée entièrement en logiciel via des boucles de délai à vide.

### Paramètres (saisis au démarrage)

| Variable | Rôle | Valeur typique |
|----------|------|----------------|
| `F` | Fréquence PWM en Hz | 15 |
| `D` | Rapport cyclique en % (duty cycle) | 25 |
| `Y` | Durée overdrive (paramètre supplémentaire) | 200 |

### Calcul des délais

```basic
TD1 = D / (173.15 * F * 0.000001)        ' itérations boucle ON
TD2 = (100 - D) / (173.15 * F * 0.000001) ' itérations boucle OFF
```

**Pourquoi 173.15 ?**
C'est une constante empirique représentant la vitesse de la boucle `FOR-NEXT` vide sur le PC utilisé lors du développement. Chaque itération dure environ **1.73 µs** (soit ~577 000 itérations/seconde), mesurée sur ce matériel spécifique. Cette constante n'est pas portable : sur un PC plus rapide ou plus lent, le timing serait incorrect. La fréquence réelle `Hz` affichée à l'écran permettait de vérifier et d'ajuster.

### Cycle PWM

```
┌─────────────────────────────────────────────────┐
│ 1. SCAN      Lire l'état des 37 sections        │
│ 2. GATING    Décider quelles sections alimenter │
│ 3. ON        Alimenter les sections actives     │
│ 4. DÉLAI ON  Boucle vide TD1 itérations         │
│ 5. OFF       Couper toutes les sections         │
│ 6. DÉLAI OFF Boucle vide TD2 itérations         │
│ 7. OVERDRIVE Impulsions courtes par groupe      │
│ 8. AFFICHAGE Mettre à jour l'écran (1/5 cycles) │
└─────────────────────────────────────────────────┘
```

---

## Logique de contrôle (gating)

Avant d'alimenter chaque section, le programme applique des règles conditionnelles.

### Réduction de vitesse (`I MOD 9 = 1`)

Les sections 0, 1, 2, 7 et 14 sont sautées (non alimentées) quand le compteur de cycle `I` est tel que `I MOD 9 = 1`, soit environ 1 cycle sur 9. Cela réduit leur rapport cyclique effectif de ~11%, ralentissant les trains dans ces zones sans modifier les paramètres globaux F et D.

Le chiffre 9 a été déterminé empiriquement pour obtenir la réduction de vitesse souhaitée sur ces sections spécifiques de la voie.

### Arrêts complets (anti-collision)

| Condition | Sections bloquées | Raison |
|-----------|------------------|--------|
| `BO(8) = 1` | 0, 1, 2, 7 | Train détecté en section 8 → arrêter les trains en amont |
| `BO(0..3) = 1` | 8, 15 | Trains en sections 0–3 → bloquer section 8 et 15 |
| `BO(2) = 1` ou `BO(3) = 1` | 14 | Protection supplémentaire section 14 |

> **Note :** Les lignes 54–57 contiennent une ambiguïté de précédence des opérateurs QBasic (`OR` vs `AND`) qui mériterait vérification lors de la réécriture.

---

## Overdrive

À la fin de chaque cycle PWM, le programme applique des impulsions courtes sur toutes les sections, par groupe :

```
Groupe 1 : sections 0–7   → impulsion → délai 200 iter
Groupe 2 : sections 8–15  → impulsion → délai 200 iter
Groupe 3 : sections 16–36 → impulsion → délai 200 iter
```

**Raison physique :** Les virages de la voie créent une résistance mécanique accrue (friction). Sans overdrive, les trains peuvent caler dans les courbes. Les impulsions courtes fournissent un coup de courant supplémentaire pour maintenir le mouvement, indépendamment du cycle PWM principal.

L'overdrive est uniforme sur tous les groupes — il n'est pas conditionnel à la détection d'un virage. Les sections en ligne droite le reçoivent aussi, sans effet négatif notable.

---

## Affichage terminal

Toutes les 5 itérations (`I MOD 5 = 1`), l'écran est mis à jour :

```
                    MINE DERIEN ET PORT RIENAFER
                              MD0809023
                    --------------------------

BLOC  BO(N%)        BLOC  BO(N%)        BLOC  BO(N%)
0     0             16    1             32    0
1     1             17    0             33    0
...                 ...                 ...
15    0             31    0             36    1

FREQUENCY - REF: 15   ACTUAL: 14.8   D%= 25
TD1= 9625   TD2= 28876   TD3= 7000   TD4= 500   OVERDRIVE= 200
TIMER - START: 12.3   PRESENT: 45.7   ELAPSED TIME: 33.4     14:23:07
```

Les 37 sections sont affichées en 3 colonnes (0–15, 16–31, 32–36). La fréquence réelle est calculée comme `Hz = I / temps_écoulé` et permet de vérifier la calibration.

---

## Variables principales

| Variable | Type | Rôle |
|----------|------|------|
| `F` | Long | Fréquence PWM cible (Hz) |
| `D` | Long | Rapport cyclique (%) |
| `Y` | Long | Paramètre overdrive |
| `TD1` | Long | Itérations délai ON |
| `TD2` | Long | Itérations délai OFF |
| `TD3` | Long | 7000 (non utilisé activement dans la boucle visible) |
| `TD4` | Long | 500 (non utilisé activement dans la boucle visible) |
| `TD5` | Long | 5000 (non utilisé activement dans la boucle visible) |
| `BO(50)` | Long[] | État de présence train par section (0 ou 1) |
| `I` | Long | Compteur de cycles |
| `N%` | Integer | Index de section courant |
| `A`, `B`, `C` | Long | Timer : départ, présent, écoulé |
| `Hz` | Long | Fréquence réelle calculée |

> `DEFLNG A-Z` en ligne 2 déclare toutes les variables comme entiers longs (32 bits). Sans cette directive, QBasic utilise des entiers 16 bits, insuffisants pour les grandes valeurs de TD1/TD2.

---

## Améliorations planifiées

Voir les issues GitHub du projet :

- **#1** — Remplacer les boucles busy-wait par du threading Python
- **#2** — Overdrive : documenter et modéliser le comportement en virage
- **#3** — Remplacer la constante empirique 173.15 par un timing calibré dynamiquement
