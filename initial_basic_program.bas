REM INITIALIZE
    DEFLNG A-Z    'MUST APPEAR ON FIRSY LINE OTHERWISE ERROR RE CAPACITY
    OUT 888, 0    'DEFLNG TO PREVENT ERROR RE CAPACITY
    OUT 890, 0
    I = 0
    COLOR 11, 9
    CLS

INPUT "ENTER FREQUENCY,DUTY IN % "; F, D, Y: REM:TYPICAL:15,25,200
DIM N%(50), BO(50), ETAT(50)
TD1 = D / (173.15 * F * .000001)
TD2 = (100 - D) / (173.15 * F * .000001)
TD3 = 7000
TD4 = 500
TD5 = 5000

CLS
PRINT TAB(30); "MINE DERIEN ET PORT RIENAFER"

PRINT TAB(35); "MD0809023"
PRINT TAB(30); "--------------------------"

REM BEGIN CYCLE
    A = TIMER

REM SCAN INPUT
DO
1           FOR N% = 0 TO 36
                OUT 888, N%
                OUT 890, 1
                ETAT = INP(889)
                BO(N%) = ETAT / 8 AND 1
                OUT 890, 0
                OUT 890, 2
            NEXT N%

REM CLEAR ADDRESS REGISTER
2           OUT 888, 0
            OUT 890, 0

    REM SPEED REDUCTION
3           FOR N% = 0 TO 36
                IF N% = 0 AND I MOD 9 = 1 THEN GOTO 25
                IF N% = 1 AND I MOD 9 = 1 THEN GOTO 25
                IF N% = 2 AND I MOD 9 = 1 THEN GOTO 25
                IF N% = 7 AND I MOD 9 = 1 THEN GOTO 25
                IF N% = 14 AND I MOD 9 = 1 THEN GOTO 25

            REM COMPLETE STOPS
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

            REM EXCEPTION:    IF N% = 15 AND BO(16) = 1 THEN GOTO 20

20          REM ENERGIZE EACH BLOCK
                OUT 888, 128 + N%
                OUT 890, 1
                OUT 890, 0
25          NEXT N%

REM DELAY ON
    FOR X = 0 TO TD1
    NEXT X

REM DEENERGIZE EACH SECTION
    FOR N% = 0 TO 36
        OUT 888, 0
        OUT 890, 1
        OUT 890, 2
    NEXT N%

REM DELAY OFF
    FOR X = 0 TO TD2
    NEXT X

REM SELECTED BLOCK OVERDRIVE

    FOR N% = 0 TO 7
        OUT 888, 128 + N%
        OUT 890, 0
        OUT 890, 1
    NEXT N%
    FOR T = 0 TO 200
    NEXT T

    FOR N% = 8 TO 15
        OUT 888, 128 + N%
        OUT 890, 0
        OUT 890, 1
    NEXT N%
    FOR T = 0 TO 200
    NEXT T

    FOR N% = 16 TO 36
        OUT 888, 128 + N%
        OUT 890, 0
        OUT 890, 1
    NEXT N%
    FOR T = 0 TO 200
    NEXT T

    OUT 888, 0
    OUT 890, 1
    OUT 890, 2

REM INCREMENT CYCLE COUNTER
30  I = I + 1
35  IF I MOD 5 = 1 THEN GOTO 110 ELSE GOTO 115

110 REM UPDATE CRT

    FOR N% = 0 TO 15
        LOCATE 4, 5, 0
        PRINT "BLOC", "BO(N%)"
        LOCATE (5 + N%), 5, 0
        PRINT N%, BO(N%)
    NEXT N%

    FOR N% = 16 TO 31
        LOCATE 4, 24, 0
        PRINT "BLOC", "BO(N%)"
        LOCATE (4 + N% - 15), 24, 0
        PRINT N%, BO(N%)
    NEXT N%

    FOR N% = 32 TO 36
        LOCATE 4, 44, 0
        PRINT "BLOC", "BO(N%)"
        LOCATE (4 + N% - 31), 44, 0
        PRINT N%, BO(N%)
    NEXT N%

    LOCATE 21, 5
    PRINT "FREQUENCY - REF:"; F, "ACTUAL:"; Hz, "D%="; D;
    LOCATE 22, 5
    PRINT "TD1="; TD1; "TD2="; TD2; "TD3="; TD3; "TD4="; TD4; "OVERDRIVE="; Y

    LOCATE 23, 69
    PRINT TIME$

REM CALCULATE ACTUAL FREQUENCY
115 B = TIMER
    C = (B + 1) - A

120 Hz = I / C
    LOCATE 23, 5
    PRINT "TIMER - START:"; A, "PRESENT:"; B, "ELAPSED TIME:"; C

REM PRESS ANY KEY TO STOP
    A$ = INKEY$

LOOP UNTIL A$ <> ""
