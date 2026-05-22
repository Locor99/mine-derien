import sys

from serial_link import SerialLink, find_arduino_port


def resolve_port(arguments):
    if len(arguments) > 1:
        return arguments[1]
    return find_arduino_port()


def main():
    port = resolve_port(sys.argv)
    if port is None:
        print("Aucun Arduino détecté. Donne le port en argument :")
        print("  python handshake.py /dev/ttyACM0")
        return 1

    print(f"Connexion à {port}...")
    with SerialLink(port) as link:
        reply = link.request("PING")

    if reply == "PONG":
        print("PONG reçu — la liaison série fonctionne.")
        return 0

    print(f"Réponse inattendue : {reply!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
