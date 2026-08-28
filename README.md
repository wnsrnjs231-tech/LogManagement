# Log Management System

물류 현장의 로그 파일을 원격으로 수집하고 관리하기 위한
Python 기반 로그 관리 시스템입니다.

설비 PC에서 실행되는 **LogAgent**와 중앙 PC에서 실행되는 **LogCollector**로 구성되어 있으며, TCP 통신을 통해 설비의 로그 파일을 중앙 PC로 다운로드할 수 있습니다.

---

## 주요 기능

* 설비 PC의 로그 파일 원격 다운로드
* TCP Socket 기반 통신
* IP 주소 기반 접근 제어
* Key 기반 요청 인증
* 날짜별 로그 파일 조회
* 여러 라인 동시 선택 및 다운로드
* 다운로드 파일 자동 저장
* Tkinter 기반 GUI 제공
* CLI 기반 LogCollector 제공
* JSON 설정 파일을 통한 설비 및 로그 관리

---

## 시스템 구성

```text
┌──────────────────────┐
│      중앙 PC         │
│                      │
│    LogCollector      │
│                      │
│  - 라인 선택         │
│  - 날짜 선택         │
│  - 로그 선택         │
│  - 로그 다운로드     │
└──────────┬───────────┘
           │
           │ TCP Socket
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌──────────┐ ┌──────────┐
│ 설비 PC  │ │ 설비 PC  │
│          │ │          │
│LogAgent  │ │LogAgent  │
│          │ │          │
│ 로그 제공 │ │ 로그 제공 │
└──────────┘ └──────────┘
```

### LogAgent

설비 PC에서 실행됩니다.

* 로그 파일 요청 수신
* 클라이언트 IP 확인
* 요청 Key 인증
* 로그 ID를 통한 파일 조회
* 파일 크기 확인
* 로그 파일 전송

### LogCollector

중앙 PC에서 실행됩니다.

* 등록된 설비 목록 관리
* 라인 선택
* 날짜 선택
* 로그 종류 선택
* LogAgent 접속
* 로그 파일 다운로드
* 다운로드 파일 저장

---

## 프로젝트 구조

```text
LogManagement/
│
├── README.md
│
├── LogAgent/
│   ├── main.py
│   ├── log_server.py
│   ├── config.json
│   └── config.example.json
│
└── LogCollector/
    ├── main.py
    ├── gui.py
    ├── collector.py
    ├── machines.json
    ├── machines.example.json
    └── received/
```

### LogAgent

```text
LogAgent/
├── main.py
├── log_server.py
├── config.json
└── config.example.json
```

* `main.py` : 프로그램 실행 및 설정 로딩
* `log_server.py` : TCP 서버 및 로그 파일 전송
* `config.json` : 설비별 실제 설정
* `config.example.json` : GitHub 공유용 설정 예제

### LogCollector

```text
LogCollector/
├── main.py
├── gui.py
├── collector.py
├── machines.json
├── machines.example.json
└── received/
```

* `main.py` : CLI 기반 Collector 실행
* `gui.py` : Tkinter 기반 GUI 실행
* `collector.py` : LogAgent 통신 및 파일 다운로드
* `machines.json` : 설비 PC 접속 정보
* `machines.example.json` : GitHub 공유용 설정 예제
* `received/` : 다운로드한 로그 파일 저장 폴더

---

## 동작 방식

### 1. LogAgent 실행

설비 PC에서 LogAgent를 실행합니다.

```bash
python main.py
```

설정 파일의 포트와 로그 정보를 불러온 후 TCP 서버를 실행합니다.

---

### 2. LogCollector 실행

중앙 PC에서 GUI를 실행합니다.

```bash
python gui.py
```

또는 CLI를 사용할 수 있습니다.

```bash
python main.py
```

---

### 3. 로그 다운로드

GUI에서 다음 정보를 선택합니다.

```text
라인
↓
날짜
↓
로그
↓
다운로드
```

Collector는 선택한 설비의 LogAgent에 TCP 연결을 생성하고 로그 파일을 요청합니다.

---

### 4. LogAgent 인증

LogAgent는 요청을 받은 후 다음 순서로 확인합니다.

```text
클라이언트 접속
      ↓
IP 주소 확인
      ↓
요청 Key 확인
      ↓
라인 / 날짜 / 로그 ID 확인
      ↓
로그 파일 확인
      ↓
파일 크기 전송
      ↓
로그 파일 전송
```

---

### 5. 로그 파일 저장

다운로드한 파일은 Collector의 `received` 폴더에 저장됩니다.

파일명은 다음 형식으로 생성됩니다.

```text
날짜_라인명_로그명.txt
```

예:

```text
2026-08-28_TEST_LINE_application.txt
```

---

## 설정

### LogAgent 설정

`config.json`

```json
{
    "line": "TEST_LINE",
    "port": 5000,
    "key": "YOUR_TEST_KEY",
    "log_root": "C:\\LogFile",
    "allowed_ips": [
        "192.168.0.10"
    ],
    "logs": [
        {
            "id": "APPLICATION",
            "name": "Application Log",
            "file": "application.log"
        }
    ]
}
```

### LogCollector 설정

`machines.json`

```json
{
    "machines": [
        {
            "name": "TEST_LINE",
            "ip": "192.168.0.100",
            "port": 5000,
            "key": "YOUR_TEST_KEY"
        }
    ]
}
```

실제 환경에서는 각 설비 PC의 IP 주소와 인증 Key를 설정해야 합니다.

---

## 실행 환경

* Python 3.x
* Windows
* TCP/IP Network
* Tkinter

외부 Python 패키지 설치 없이 Python 기본 라이브러리만 사용합니다.

---

## 기술 스택

| 구분           | 기술        |
| ------------- | ---------- |
| Language      | Python     |
| GUI           | Tkinter    |
| Network       | TCP Socket |
| Configuration | JSON       |
| File Transfer | Socket     |
| Encoding      | UTF-8      |

---

## 주의사항

`config.json`과 `machines.json`에는 실제 환경의 IP 주소 및 인증 Key가 포함될 수 있으므로 GitHub에 공개하지 않습니다.

GitHub에는 다음과 같은 예제 설정 파일을 사용합니다.

```text
config.example.json
machines.example.json
```

실제 설정 파일은 `.gitignore`에 등록하여 관리합니다.
