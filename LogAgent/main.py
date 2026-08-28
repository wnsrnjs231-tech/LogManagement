import json
import os

from log_server import start_server


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "config.json"
)


def load_config():
    """config.json 설정을 불러온다."""

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def print_config(config):
    """현재 LogAgent 설정을 출력한다."""

    print("=== LogAgent 시작 ===")

    print(f"라인 : {config['line']}")
    print(f"포트 : {config['port']}")

    print("\n로그 목록")

    for log in config["logs"]:
        print(
            f"- {log['name']} : {log['file']}"
        )

    print("\n설정 로딩 완료")


def main():
    """LogAgent 프로그램을 시작한다."""

    config = load_config()

    print_config(config)

    start_server(
        config["port"],
        config
    )


if __name__ == "__main__":
    main()