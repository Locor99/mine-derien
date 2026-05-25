import sys

from serial_link import SerialLink, find_arduino_port

USAGE = """Console série — tape une commande, Entrée pour l'envoyer.
Exemples :
  PING                  test de liaison
  SET 22 1 / GET 32     piloter / lire une pin
  TC_ADDR 5 1           bus d'adresse du module
  SCAN 12 / ENERGIZE 5  opérations par section
  AUTO_START 15 25      démarrer le cycle PWM
  GET_STATE             état des 37 sections
  FORCE_PRESENT 8 1     simuler un train (test gating)
  quit                  quitter
La casse n'a pas d'importance.
"""


def resolve_port(arguments):
    if len(arguments) > 1:
        return arguments[1]
    return find_arduino_port()


def run_session(link):
    print(USAGE)
    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            return
        if user_input.lower() in ("quit", "exit", "q"):
            return
        if not user_input:
            continue
        print(link.request(user_input.upper()))


def main():
    port = resolve_port(sys.argv)
    if port is None:
        print("Aucun Arduino détecté. Donne le port en argument :")
        print("  python gpio_test.py COM3")
        return 1

    print(f"Connexion à {port}...")
    with SerialLink(port) as link:
        run_session(link)
    return 0


if __name__ == "__main__":
    sys.exit(main())