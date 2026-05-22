import sys

from serial_link import SerialLink, find_arduino_port

USAGE = """Commandes :
  set <pin> <0|1>   allume ou éteint une sortie
  get <pin>         lit l'état d'une entrée
  ping              teste la liaison
  quit              quitte
"""


def resolve_port(arguments):
    if len(arguments) > 1:
        return arguments[1]
    return find_arduino_port()


def translate(user_input):
    parts = user_input.split()
    if not parts:
        return None
    verb = parts[0].lower()
    if verb == "set" and len(parts) == 3:
        return f"SET {parts[1]} {parts[2]}"
    if verb == "get" and len(parts) == 2:
        return f"GET {parts[1]}"
    if verb == "ping":
        return "PING"
    return None


def run_session(link):
    print(USAGE)
    while True:
        try:
            user_input = input("> ").strip()
        except EOFError:
            return
        if user_input.lower() in ("quit", "exit", "q"):
            return
        command = translate(user_input)
        if command is None:
            print(USAGE)
            continue
        print(link.request(command))


def main():
    port = resolve_port(sys.argv)
    if port is None:
        print("Aucun Arduino détecté. Donne le port en argument :")
        print("  python gpio_test.py /dev/ttyACM0")
        return 1

    print(f"Connexion à {port}...")
    with SerialLink(port) as link:
        run_session(link)
    return 0


if __name__ == "__main__":
    sys.exit(main())
