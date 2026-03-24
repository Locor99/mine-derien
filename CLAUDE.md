# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Contexte du projet

Système de commande de trains miniatures développé par un ingénieur électrique. Le code original est en QBasic et communique avec le hardware des trains via port parallèle. L'objectif est de moderniser la plateforme logicielle et matérielle côté ordinateur, tout en conservant l'interface parallèle existante côté trains.

La piste principale pour remplacer le port parallèle est une connexion USB (adaptateur USB-parallèle ou microcontrôleur intermédiaire).

## Architecture matérielle

### Alimentation et détection

La voie ferrée utilise deux rails :
- **Rail A** : 12V constant
- **Rail B** : connecté au module électronique pour le contrôle PWM des moteurs

Les trains consomment le 12V via leurs moteurs. Quand un train est présent dans une section, il crée un chemin de retour du courant vers le rail B. Cette chute de tension/courant est lue via le port parallèle pour détecter la présence du train (état binaire par section).

### 37 sections de voie

La voie est divisée en 37 sections indépendantes (indices 0–36). Chaque section est alimentée ou non individuellement via le module électronique. L'état de chaque section (train présent / absent) est stocké dans le tableau `BO(50)`.

### Interface port parallèle (LPT1, 0x378–0x37A)

| Registre | Adresse | Direction | Rôle |
|----------|---------|-----------|------|
| Data     | 888 (0x378) | OUT | Sélectionne la section (0–36) ou l'énergise (128+N) |
| Status   | 889 (0x379) | IN  | Lit la présence d'un train (bit 3 du byte lu) |
| Control  | 890 (0x37A) | OUT | Séquence de contrôle : 0 → init, 1 → pulse, 2 → reset |

**Détection d'un train dans la section N :**
```
OUT 888, N     ← sélectionner la section
OUT 890, 1     ← pulse
ETAT = INP(889)
BO(N) = ETAT / 8 AND 1   ← extraire le bit 3
OUT 890, 0
OUT 890, 2
```

**Énergiser la section N (alimenter le moteur) :**
```
OUT 888, 128 + N   ← valeur > 127 = commande d'alimentation
OUT 890, 1
OUT 890, 2
```

### Contrôle PWM

Le PWM est implémenté en logiciel via des boucles de délai :
- **TD1** = temps ON (section alimentée)
- **TD2** = temps OFF (section coupée)
- Formule : `TD = D / (173.15 × F × 0.000001)` avec F en Hz, D en %

Un mode **overdrive** applique des impulsions supplémentaires courtes sur chaque groupe de sections (0–7, 8–15, 16–36) pour assurer le démarrage ou l'accélération des trains.

### Logique de contrôle

Le programme tourne en boucle principale :
1. **Scan** : lire l'état des 37 sections
2. **Gating conditionnel** : certaines sections sont alimentées seulement si le compteur de cycle `I MOD 9 = 1` (réduction de vitesse) ou bloquées si un train est détecté en section 8 (protection anti-collision)
3. **Pulse ON** : délai TD1
4. **Désénergisation** : toutes les sections coupées
5. **Pulse OFF** : délai TD2
6. **Overdrive** : impulsions courtes par groupe
7. **Affichage** : état des 37 sections en temps réel sur terminal texte

## Code quality

Apply Clean Code and SOLID principles: expressive names, short single-responsibility functions, no duplication, injected dependencies, open/closed. No comments — code must read like prose.