from collector import (
    load_machine_config,
    find_machine,
    check_date,
    download_log
)


def print_header():
    """Log Collector 메뉴를 출력한다."""

    print("\n==============================")
    print("Log Collector")
    print("==============================")


def parse_lines(line_input):
    """입력된 라인 목록을 분리한다."""

    return [
        line.strip()
        for line in line_input.split(",")
        if line.strip()
    ]


def main():

    # 머신 설정 불러오기
    machines = load_machine_config()

    # 로그 목록
    log_map = {
        "APPLICATION": {
            "id": "APPLICATION",
            "file": "application.log"
        },
        "SYSTEM": {
            "id": "SYSTEM",
            "file": "system.log"
        },
        "ERROR": {
            "id": "ERROR",
            "file": "error.log"
        },
        "ACCESS": {
            "id": "ACCESS",
            "file": "access.log"
        }
    }

    while True:

        print_header()

        # 라인 입력
        line_input = input(
            "라인명 (종료:q, 여러 개는 , 로 구분) : "
        )

        if line_input.lower() == "q":
            print("Log Collector 종료")
            break

        lines = parse_lines(
            line_input
        )

        # 날짜 입력
        date = input("날짜 : ")

        if not check_date(date):

            print(
                "날짜 형식 오류 (YYYY-MM-DD)"
            )

            continue

        # 로그 입력
        log = input(
            "로그명 (APPLICATION / SYSTEM / ERROR / ACCESS) : "
        ).strip().upper()

        log_info = log_map.get(log)

        if log_info is None:

            print(
                "등록되지 않은 로그입니다."
            )

            continue

        # 입력된 각 라인 처리
        for line in lines:

            machine = find_machine(
                machines,
                line
            )

            if machine is None:

                print(
                    f"{line} : 등록되지 않은 라인입니다."
                )

                continue

            # LogAgent에 로그 요청
            download_log(
                machine,
                line,
                date,
                log_info
            )


if __name__ == "__main__":
    main()