import socket
import os
import json
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = os.path.join(
    BASE_DIR,
    "logagent.log"
)


def write_log(message):
    """LogAgent 동작 로그를 기록한다."""

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"[{now}] {message}\n"
        )


def get_log_file(config, log_id):
    """log_id에 해당하는 실제 로그 파일명을 반환한다."""

    for log in config["logs"]:

        if log["id"] == log_id:
            return log["file"]

    return None


def create_server_socket(port):
    """TCP 서버 소켓을 생성하고 포트에 연결한다."""

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        ("0.0.0.0", port)
    )

    server_socket.listen()

    return server_socket


def is_allowed_ip(config, client_ip):
    """클라이언트 IP가 허용된 IP인지 확인한다."""

    return client_ip in config["allowed_ips"]


def authenticate(request_data, config):
    """요청의 인증 키를 확인한다."""

    request_key = request_data.get("key")

    return request_key == config["key"]


def validate_request(request_data):
    """요청에 필요한 값이 모두 존재하는지 확인한다."""

    line = request_data.get("line")
    date = request_data.get("date")
    log_id = request_data.get("log_id")

    if not line or not date or not log_id:
        return False

    return True


def parse_date(date):
    """날짜 문자열을 검증하고 datetime 객체로 반환한다."""

    try:

        return datetime.strptime(
            date,
            "%Y-%m-%d"
        )

    except ValueError:

        return None


def create_log_path(config, date_obj, file_name):
    """날짜와 파일명을 이용해 로그 파일 경로를 생성한다."""

    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")
    day = date_obj.strftime("%d")

    return os.path.join(
        config["log_root"],
        year,
        month,
        day,
        file_name
    )


def send_error(client_socket, message):
    """클라이언트에게 오류 메시지를 전송한다."""

    response = f"ERROR\n{message}\n"

    client_socket.sendall(
        response.encode("utf-8")
    )


def send_file(client_socket, file_path, file_name):
    """로그 파일을 클라이언트에게 전송한다."""

    file_size = os.path.getsize(file_path)

    # 성공 응답
    client_socket.sendall(
        b"OK\n"
    )

    # 파일 크기 전송
    client_socket.sendall(
        f"{file_size}\n".encode("utf-8")
    )

    write_log(
        f"파일 전송 시작 : {file_name}"
    )

    # 파일 전송
    with open(file_path, "rb") as file:

        while True:

            data = file.read(4096)

            if not data:
                break

            client_socket.sendall(data)

    write_log(
        f"파일 전송 완료 : {file_name} ({file_size} byte)"
    )


def handle_client(client_socket, client_ip, config):
    """클라이언트의 요청을 처리한다."""

    file_name = None

    try:

        write_log(
            f"접속 요청 IP:{client_ip}"
        )

        # IP 확인
        if not is_allowed_ip(config, client_ip):

            write_log(
                f"허용되지 않은 IP 차단 : {client_ip}"
            )

            send_error(
                client_socket,
                "허용되지 않은 IP입니다."
            )

            return

        # 요청 수신
        request = client_socket.recv(1024)

        if not request:
            return

        # JSON 변환
        try:

            request_data = json.loads(
                request.decode("utf-8")
            )

        except (json.JSONDecodeError, UnicodeDecodeError):

            write_log(
                f"잘못된 JSON 요청 IP:{client_ip}"
            )

            send_error(
                client_socket,
                "잘못된 요청 형식입니다."
            )

            return

        # 인증
        if not authenticate(request_data, config):

            write_log(
                f"인증 실패 IP:{client_ip}"
            )

            send_error(
                client_socket,
                "인증에 실패했습니다."
            )

            return

        write_log(
            f"인증 성공 IP:{client_ip}"
        )

        # 요청값 확인
        if not validate_request(request_data):

            write_log(
                f"잘못된 요청 IP:{client_ip}"
            )

            send_error(
                client_socket,
                "잘못된 요청입니다."
            )

            return

        line = request_data["line"]
        date = request_data["date"]
        log_id = request_data["log_id"]

        print(f"라인 : {line}")
        print(f"날짜 : {date}")
        print(f"로그 ID : {log_id}")

        # 날짜 확인
        date_obj = parse_date(date)

        if date_obj is None:

            write_log(
                f"잘못된 날짜 형식 IP:{client_ip} / date:{date}"
            )

            send_error(
                client_socket,
                "날짜 형식이 올바르지 않습니다."
            )

            return

        # 로그 파일 찾기
        file_name = get_log_file(
            config,
            log_id
        )

        if file_name is None:

            write_log(
                f"등록되지 않은 로그 ID:{log_id}"
            )

            send_error(
                client_socket,
                "등록되지 않은 로그입니다."
            )

            return

        # 파일 경로 생성
        file_path = create_log_path(
            config,
            date_obj,
            file_name
        )

        # 파일 확인
        if not os.path.exists(file_path):

            write_log(
                f"파일 없음 : {file_path}"
            )

            send_error(
                client_socket,
                "파일이 존재하지 않습니다."
            )

            return

        print("파일 존재")

        file_size = os.path.getsize(file_path)

        print(
            f"파일 크기 : {file_size} byte"
        )

        # 파일 전송
        send_file(
            client_socket,
            file_path,
            file_name
        )

    except Exception as e:

        print(
            f"전송 오류 : {e}"
        )

        write_log(
            f"전송 오류 : "
            f"{file_name if file_name else ''} / {e}"
        )


def start_server(port, config):
    """LogAgent TCP 서버를 시작한다."""

    server_socket = create_server_socket(port)

    print("LogAgent 서버 실행")

    write_log(
        f"서버 시작 - 포트:{port}"
    )

    write_log(
        "요청 대기 중"
    )

    while True:

        client_socket, address = (
            server_socket.accept()
        )

        client_ip = address[0]

        try:

            handle_client(
                client_socket,
                client_ip,
                config
            )

        finally:

            client_socket.close()