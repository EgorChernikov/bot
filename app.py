from commands.updater import start_updater
from context.initialization import initialize_context


def main() -> None:
    initialize_context()
    start_updater()


if __name__ == '__main__':
    main()
