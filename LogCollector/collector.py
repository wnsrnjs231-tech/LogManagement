import json
import os
import socket
import sys
from datetime import datetime


# 파일 전송 시 한 번에 수신할 최대 데이터 크기 (64 KB = 65,536 bytes)
BUFFER_SIZE = 64 * 1024


# Python 실행 환경에 따라 기준 폴더 결정
# 일반 실행: 현재 Python 파일이 있는 폴더
# PyInstaller 실행: 실행 파일(.exe)이 있는 폴더
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )


def load_machine_config():
    """machines.json 설정을 불러온다."""

    path = os.path.join(
        BASE_DIR,
        "machines.json"
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def find_machine(config, line_name):
    """라인 이름에 해당하는 LogAgent 정보를 찾는다."""

    for machine in config["machines"]:

        if machine["name"] == line_name:
            return machine

    return None


def check_date(date):
    """날짜가 YYYY-MM-DD 형식인지 확인한다."""

    try:

        datetime.strptime(
            date,
            "%Y-%m-%d"
        )

        return True

    except ValueError:

        return False


def create_request(machine, line, date, log_info):
    """LogAgent에 전달할 요청 데이터를 생성한다."""

    return {
        "key": machine["key"],
        "line": line,
        "date": date,
        "log_id": log_info["id"]
    }


def receive_line(client_socket):
    """TCP 소켓에서 개행 문자까지 데이터를 수신한다."""

    data = b""

    while b"\n" not in data:

        recv_data = client_socket.recv(1)

        if not recv_data:
            return None

        data += recv_data

    return data.decode("utf-8").strip()


def receive_file(client_socket, file_size, save_path):
    """지정된 크기의 파일을 수신하여 저장한다."""

    received = 0

    with open(
        save_path,
        "wb"
    ) as file:

        while received < file_size:

            # 파일 전체 크기를 초과하지 않도록
            # 남은 데이터와 BUFFER_SIZE 중 작은 크기만 요청
            recv_data = client_socket.recv(
                min(
                    BUFFER_SIZE,
                    file_size - received
                )
            )

            if not recv_data:
                print("파일 전송 중 연결 종료")
                return False

            file.write(
                recv_data
            )

            received += len(recv_data)

    return received == file_size


def create_save_path(line, date, file_name):
    """다운로드한 로그 파일의 저장 경로를 생성한다."""

    save_dir = os.path.join(
        BASE_DIR,
        "received"
    )

    os.makedirs(
        save_dir,
        exist_ok=True
    )

    base_name = os.path.splitext(
        file_name
    )[0]

    save_file_name = (
        f"{date}_"
        f"{line}_"
        f"{base_name}.txt"
    )

    return os.path.join(
        save_dir,
        save_file_name
    )


def download_log(
    machine,
    line,
    date,
    log_info
):
    """LogAgent에 접속하여 로그 파일을 다운로드한다."""

    file_name = log_info["file"]

    # LogAgent에 전달할 요청 생성
    request = create_request(
        machine,
        line,
        date,
        log_info
    )

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        # LogAgent 서버에 TCP 연결
        client_socket.connect(
            (
                machine["ip"],
                machine["port"]
            )
        )

        # 요청 데이터를 JSON 문자열로 변환
        request_data = json.dumps(
            request,
            ensure_ascii=False
        )

        # JSON 요청 전송
        client_socket.sendall(
            request_data.encode("utf-8")
        )

        # 서버 응답 상태 확인
        status = receive_line(
            client_socket
        )

        if status is None:
            print("서버 연결 종료")
            return False

        # OK가 아닌 경우 서버에서 전달한 오류 메시지 출력
        if status != "OK":

            error_message = receive_line(
                client_socket
            )

            print(
                f"오류 : {error_message}"
            )

            return False

        # 서버에서 전송할 파일 크기 수신
        size_data = receive_line(
            client_socket
        )

        if size_data is None:
            print("파일 크기 수신 실패")
            return False

        file_size = int(size_data)

        # 다운로드 파일 저장 경로 생성
        save_path = create_save_path(
            line,
            date,
            file_name
        )

        # 파일 데이터 수신 및 저장
        success = receive_file(
            client_socket,
            file_size,
            save_path
        )

        if not success:
            return False

        print(
            f"다운로드 완료 : {save_path}"
        )

        return save_path

    except ConnectionRefusedError:

        print("서버 접속 거부")
        return False

    except socket.timeout:

        print("서버 응답 시간 초과")
        return False

    except ValueError:

        print("잘못된 파일 크기")
        return False

    except Exception as e:

        print(
            f"오류 발생 : {e}"
        )

        return False

    finally:

        # 통신이 종료되면 소켓 연결 해제
        client_socket.close()