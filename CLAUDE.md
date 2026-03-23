# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Contexte du projet

Système de commande de trains miniatures développé par un ingénieur électrique. Le code original est en QBasic et communique avec le hardware des trains via port parallèle. L'objectif est de moderniser la plateforme logicielle et matérielle côté ordinateur, tout en conservant l'interface parallèle existante côté trains.

La piste principale pour remplacer le port parallèle est une connexion USB (adaptateur USB-parallèle ou microcontrôleur intermédiaire).

## Code quality

Apply Clean Code and SOLID principles: expressive names, short single-responsibility functions, no duplication, injected dependencies, open/closed. No comments — code must read like prose.