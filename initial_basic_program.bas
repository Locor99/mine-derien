REM ============================================================
REM  MINE DE RIEN ET PORT RIEN-A-FER
REM  Programme QBasic original — commande de 37 sections de voie
REM  via le port parallele LPT1 (adresses 888/889/890).
REM ============================================================

REM ---------- INITIALISATION ----------
    DEFLNG A-Z              'Toutes les variables A..Z sont des entiers longs
                            '(obligatoire en 1re ligne, sinon erreur de capacite)
    OUT 888, 0              'Registre DATA (0x378) remis a 0 : aucune section selectionnee
    OUT 890, 0              'Registre CONTROL (0x37A) remis a 0 : init de la sequence
    I = 0                   'Compteur de cycles de la boucle principale
    COLOR 11, 9             'Couleurs du terminal : texte cyan clair sur fond bleu
    CLS                     'Efface l'ecran

REM ---------- PARAMETRES UTILISATEUR ----------
REM F = frequence PWM (Hz), D = rapport cyclique (%), Y = duree overdrive
REM Exemple typique saisi par l'operateur : 15, 25, 200
INPUT "ENTER FREQUENCY,DUTY IN % "; F, D, Y
DIM N%(50), BO(50), ETAT(50)    'N% = index section, BO = etat (train present),
                                'ETAT = byte brut lu sur le port

REM ---------- CALCUL DES DELAIS PWM ----------
REM Boucles FOR de delai logiciel : nb d'iterations a faire pour obtenir
REM le temps ON (TD1) et le temps OFF (TD2) correspondants a F et D.
TD1 = D / (173.15 * F * .000001)            'Duree ON  (section alimentee)
TD2 = (100 - D) / (173.15 * F * .000001)    'Duree OFF (section coupee)
TD3 = 7000                                  'Delais auxiliaires (non utilises ici)
TD4 = 500
TD5 = 5000

REM ---------- EN-TETE A L'ECRAN ----------
CLS
PRINT TAB(30); "MINE DERIEN ET PORT RIENAFER"
PRINT TAB(35); "MD0809023"
PRINT TAB(30); "--------------------------"

REM ---------- DEBUT DU CYCLE ----------
    A = TIMER               'Memorise l'heure de depart (en secondes depuis minuit)
                            'utilisee plus loin pour calculer la frequence reelle

REM ============================================================
REM  BOUCLE PRINCIPALE — tourne jusqu'a ce qu'une touche soit pressee
REM ============================================================
DO

REM ---------- 1) SCAN DES ENTREES : presence d'un train dans chaque section ----------
1           FOR N% = 0 TO 36
                OUT 888, N%             'Selectionne l'adresse de la section N%
                OUT 890, 1              'Pulse de lecture
                ETAT = INP(889)         'Lit le registre STATUS du port parallele
                BO(N%) = ETAT / 8 AND 1 'Extrait le bit 3 -> 1 si train present, 0 sinon
                OUT 890, 0              'Fin de pulse
                OUT 890, 2              'Reset de la sequence de lecture
            NEXT N%

REM ---------- 2) REMISE A ZERO DU REGISTRE D'ADRESSE ----------
2           OUT 888, 0
            OUT 890, 0

REM ---------- 3) ENERGISATION CONDITIONNELLE DES SECTIONS ----------
REM Selon des regles de "ralentissement" et de "stops complets", on choisit
REM de NE PAS alimenter certaines sections (GOTO 25 = sauter cette section).
3           FOR N% = 0 TO 36

REM Reduction de vitesse : 1 cycle sur 9, on saute les sections 0,1,2,7,14
REM (elles ne sont pas alimentees ce cycle -> le train y va moins vite).
                IF N% = 0 AND I MOD 9 = 1 THEN GOTO 25
                IF N% = 1 AND I MOD 9 = 1 THEN GOTO 25
                IF N% = 2 AND I MOD 9 = 1 THEN GOTO 25
                IF N% = 7 AND I MOD 9 = 1 THEN GOTO 25
                IF N% = 14 AND I MOD 9 = 1 THEN GOTO 25

REM Arrets complets (anti-collision) : si un train est dans la section 8,
REM on coupe l'alimentation des sections 0,1,2,7 ; si un train est detecte
REM en 0/1/2/3, on coupe 15 et 8 ; et la section 14 est coupee si train en 2 ou 3.
REM NOTE : "IF N% = 15 OR 8 AND BO(...) = 1" est ambigu en QBasic et se lit en fait
REM comme "IF (N% = 15) OR (8 AND BO(...) = 1)" — comportement original conserve.
                IF N% = 0 AND BO(8) = 1 THEN GOTO 25
                IF N% = 1 AND BO(8) = 1 THEN GOTO 25
                IF N% = 2 AND BO(8) = 1 THEN GOTO 25
                IF N% = 7 AND BO(8) = 1 THEN GOTO 25
                IF N% = 15 OR 8 AND BO(0) = 1 THEN GOTO 25
                IF N% = 15 OR 8 AND BO(1) = 1 THEN GOTO 25
                IF N% = 15 OR 8 AND BO(2) = 1 THEN GOTO 25
                IF N% = 15 OR 8 AND BO(3) = 1 THEN GOTO 25
                IF N% = 14 AND BO(3) = 1 THEN GOTO 25
                IF N% = 14 AND BO(2) = 1 THEN GOTO 25

REM EXCEPTION (desactivee) : IF N% = 15 AND BO(16) = 1 THEN GOTO 20

20          REM Energise la section courante : valeur 128+N -> commande "alimenter"
                OUT 888, 128 + N%
                OUT 890, 1
                OUT 890, 0
25          NEXT N%

REM ---------- 4) DELAI ON (duree pendant laquelle les sections restent alimentees) ----------
    FOR X = 0 TO TD1
    NEXT X

REM ---------- 5) DESENERGISATION : on coupe toutes les sections ----------
    FOR N% = 0 TO 36
        OUT 888, 0
        OUT 890, 1
        OUT 890, 2
    NEXT N%

REM ---------- 6) DELAI OFF (duree pendant laquelle les sections restent coupees) ----------
    FOR X = 0 TO TD2
    NEXT X

REM ---------- 7) OVERDRIVE : impulsions courtes par groupe de sections ----------
REM Aide au demarrage / accelere les trains qui peinent.
REM Groupe 1 : sections 0..7
    FOR N% = 0 TO 7
        OUT 888, 128 + N%
        OUT 890, 0
        OUT 890, 1
    NEXT N%
    FOR T = 0 TO 200            'Petit delai entre groupes
    NEXT T

REM Groupe 2 : sections 8..15
    FOR N% = 8 TO 15
        OUT 888, 128 + N%
        OUT 890, 0
        OUT 890, 1
    NEXT N%
    FOR T = 0 TO 200
    NEXT T

REM Groupe 3 : sections 16..36
    FOR N% = 16 TO 36
        OUT 888, 128 + N%
        OUT 890, 0
        OUT 890, 1
    NEXT N%
    FOR T = 0 TO 200
    NEXT T

REM Fin d'overdrive : on remet tout a zero.
    OUT 888, 0
    OUT 890, 1
    OUT 890, 2

REM ---------- 8) INCREMENT DU COMPTEUR DE CYCLE ----------
30  I = I + 1
REM 1 cycle sur 5, on rafraichit l'ecran (sinon on saute directement au calcul de Hz).
35  IF I MOD 5 = 1 THEN GOTO 110 ELSE GOTO 115

REM ---------- 9) MISE A JOUR DE L'AFFICHAGE (CRT = ecran) ----------
110 REM Colonne de gauche : sections 0..15
    FOR N% = 0 TO 15
        LOCATE 4, 5, 0
        PRINT "BLOC", "BO(N%)"
        LOCATE (5 + N%), 5, 0
        PRINT N%, BO(N%)
    NEXT N%

REM Colonne du milieu : sections 16..31
    FOR N% = 16 TO 31
        LOCATE 4, 24, 0
        PRINT "BLOC", "BO(N%)"
        LOCATE (4 + N% - 15), 24, 0
        PRINT N%, BO(N%)
    NEXT N%

REM Colonne de droite : sections 32..36
    FOR N% = 32 TO 36
        LOCATE 4, 44, 0
        PRINT "BLOC", "BO(N%)"
        LOCATE (4 + N% - 31), 44, 0
        PRINT N%, BO(N%)
    NEXT N%

REM Bas d'ecran : parametres PWM en clair
    LOCATE 21, 5
    PRINT "FREQUENCY - REF:"; F, "ACTUAL:"; Hz, "D%="; D;
    LOCATE 22, 5
    PRINT "TD1="; TD1; "TD2="; TD2; "TD3="; TD3; "TD4="; TD4; "OVERDRIVE="; Y

    LOCATE 23, 69
    PRINT TIME$                 'Horloge systeme HH:MM:SS

REM ---------- 10) CALCUL DE LA FREQUENCE REELLE DE LA BOUCLE ----------
115 B = TIMER                   'Heure courante
    C = (B + 1) - A             'Temps ecoule depuis le debut (+1 pour eviter /0)

120 Hz = I / C                  'Frequence effective = cycles / temps
    LOCATE 23, 5
    PRINT "TIMER - START:"; A, "PRESENT:"; B, "ELAPSED TIME:"; C

REM ---------- 11) SORTIE : n'importe quelle touche arrete le programme ----------
    A$ = INKEY$                 'Lit le clavier sans bloquer (chaine vide si rien)

LOOP UNTIL A$ <> ""             'Tant qu'aucune touche n'a ete pressee, on recommence
