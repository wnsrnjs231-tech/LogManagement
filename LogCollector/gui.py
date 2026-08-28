import tkinter as tk
from tkinter import ttk
from datetime import datetime

from collector import (
    load_machine_config,
    find_machine,
    download_log,
    check_date
)


# Collector에서 사용할 로그 목록
LOG_MAP = {
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


class LogCollectorGUI:

    def __init__(self, root):

        self.root = root

        # 머신 설정 불러오기
        self.machines = load_machine_config()

        # 선택된 라인을 저장하는 변수
        self.line_vars = {}

        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        """GUI 기본 설정을 구성한다."""

        self.root.title("Log Collector v1.0")
        self.root.geometry("560x340")
        self.root.resizable(False, False)

    def create_widgets(self):
        """GUI 구성 요소를 생성한다."""

        left_frame = tk.Frame(self.root)
        right_frame = tk.Frame(self.root)

        left_frame.pack(
            side="left",
            padx=20,
            pady=20,
            anchor="n"
        )

        right_frame.pack(
            side="right",
            padx=20,
            pady=20,
            anchor="n"
        )

        self.create_line_widgets(
            left_frame
        )

        self.create_date_widgets(
            right_frame
        )

        self.create_log_widgets(
            right_frame
        )

        self.create_status_widgets(
            right_frame
        )

    def create_line_widgets(self, frame):
        """라인 선택 UI를 생성한다."""

        tk.Label(
            frame,
            text="라인"
        ).pack(anchor="w")

        for machine in self.machines["machines"]:

            name = machine["name"]

            var = tk.BooleanVar()

            self.line_vars[name] = var

            tk.Checkbutton(
                frame,
                text=name,
                variable=var
            ).pack(anchor="w")

    def create_date_widgets(self, frame):
        """날짜 입력 UI를 생성한다."""

        tk.Label(
            frame,
            text="날짜"
        ).pack(anchor="w")

        self.date_entry = tk.Entry(
            frame,
            width=25
        )

        self.date_entry.pack(
            anchor="w"
        )

        self.date_entry.insert(
            0,
            datetime.today().strftime("%Y-%m-%d")
        )

    def create_log_widgets(self, frame):
        """로그 선택 UI를 생성한다."""

        tk.Label(
            frame,
            text="로그"
        ).pack(
            anchor="w",
            pady=(10, 0)
        )

        self.log_var = tk.StringVar(
            value="APPLICATION"
        )

        self.log_combo = ttk.Combobox(
            frame,
            textvariable=self.log_var,
            values=list(LOG_MAP.keys()),
            state="readonly",
            width=22
        )

        self.log_combo.pack(
            anchor="w"
        )

    def create_status_widgets(self, frame):
        """상태 표시 및 다운로드 버튼을 생성한다."""

        self.status_label = tk.Label(
            frame,
            text="대기중"
        )

        self.status_label.pack(
            anchor="w",
            pady=(10, 0)
        )

        tk.Button(
            frame,
            text="다운로드",
            width=20,
            command=self.start_download
        ).pack(
            pady=15
        )

    def get_selected_lines(self):
        """사용자가 선택한 라인 목록을 반환한다."""

        return [
            name
            for name, var in self.line_vars.items()
            if var.get()
        ]

    def start_download(self):
        """선택한 라인의 로그 파일을 다운로드한다."""

        selected_lines = self.get_selected_lines()

        if not selected_lines:

            self.status_label.config(
                text="라인을 선택하세요."
            )

            return

        date = self.date_entry.get()

        if not check_date(date):

            self.status_label.config(
                text="날짜 형식 오류 (YYYY-MM-DD)"
            )

            return

        log_info = LOG_MAP[
            self.log_var.get()
        ]

        success = True
        last_path = ""

        for line in selected_lines:

            machine = find_machine(
                self.machines,
                line
            )

            if machine is None:

                success = False
                continue

            result = download_log(
                machine,
                line,
                date,
                log_info
            )

            if not result:

                success = False

            else:

                last_path = result

        if success:

            self.status_label.config(
                text=f"다운로드 완료\n{last_path}"
            )

        else:

            self.status_label.config(
                text="일부 또는 전체 다운로드 실패"
            )


def main():

    root = tk.Tk()

    LogCollectorGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()