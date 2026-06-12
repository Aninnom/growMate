# GrowMate 라즈베리파이 (센서 전송 + LCD 표정)

라즈베리파이에서 도는 두 프로그램:

| 파일 | 역할 |
|---|---|
| `send_sensors.py` | 센서값을 읽어 노트북 FastAPI 서버로 POST |
| `face.py` | Waveshare 3.5" SPI LCD에 식물 표정(happy/thirsty/angry/sad/cold/hot) 표시 |

---

## 0. 접속 정보 (우리 환경 기준)

| 항목 | 값 |
|---|---|
| 라즈베리파이 계정 | `phc_15` |
| 라즈베리파이 IP | `172.20.10.5` (Wi-Fi 바뀌면 변동 — 아래 "IP 확인" 참고) |
| 라즈베리파이 코드 경로 | `~/growMate/raspberry/` |
| LCD | Waveshare 3.5" **A타입** (SPI, 480×320) |

> ⚠️ **모든 `scp`/`ssh` 명령은 "Mac 터미널"에서** 친다. 라즈베리파이 프롬프트(`phc_15@PhC-15:~ $`)에서 scp 하면 "No such file" 난다.

IP가 바뀌었으면 라즈베리파이에서 `hostname -I` 로 다시 확인.

---

## 1. SSH 접속

```bash
ssh phc_15@172.20.10.5
# 비밀번호 입력
```

---

## 2. 코드 업데이트 (Mac → 라즈베리파이 전송)

Mac에서 코드 고친 뒤, **변경된 파일만** 라즈베리파이로 복사:

```bash
# 표정 코드
scp /Users/hyeokjunlee/Documents/Claude/Projects/RasberryPi_PhysicalAI/growMate/raspberry/face.py phc_15@172.20.10.5:~/growMate/raspberry/

# 센서 코드
scp /Users/hyeokjunlee/Documents/Claude/Projects/RasberryPi_PhysicalAI/growMate/raspberry/send_sensors.py phc_15@172.20.10.5:~/growMate/raspberry/
```

둘 다 한 번에:

```bash
scp /Users/hyeokjunlee/Documents/Claude/Projects/RasberryPi_PhysicalAI/growMate/raspberry/face.py /Users/hyeokjunlee/Documents/Claude/Projects/RasberryPi_PhysicalAI/growMate/raspberry/send_sensors.py phc_15@172.20.10.5:~/growMate/raspberry/
```

> 폴더가 없다고 나오면(`remote mkdir ... No such file`) 한 번만:
> ```bash
> ssh phc_15@172.20.10.5 "mkdir -p ~/growMate/raspberry"
> ```

---

## 3. 실행

SSH로 접속한 라즈베리파이에서:

```bash
cd ~/growMate/raspberry
```

### 센서 전송
```bash
python3 send_sensors.py
```

### LCD 표정
```bash
DISPLAY=:0 python3 face.py
```

> **`DISPLAY=:0` 꼭 붙인다.** SSH 세션엔 화면이 없어서 빼면 "Can't open display"로 죽는다.
> `face.py`가 `xrandr`로 LCD(480×320, SPI 출력) 위치를 자동 감지해 그 자리에 테두리 없는 창을 올린다.
> 정상이면 로그에 `[face] LCD 위치 (1920, 0) 에 테두리 없는 창으로 표시` 가 뜨고 LCD에 얼굴이 나온다.

자동 감지가 빗나가 HDMI 쪽에 뜨면 위치 직접 지정:
```bash
DISPLAY=:0 LCD_POS=1920,0 python3 face.py
```
(`1920,0` 은 `DISPLAY=:0 xrandr` 에서 `480x320+1920+0` 의 `+X+Y` 값)

### 둘 다 동시에
```bash
python3 send_sensors.py &        # 백그라운드
DISPLAY=:0 python3 face.py       # 앞에서 실행
```

---

## 4. 멈추기

- 앞에서 돌고 있으면 `Ctrl + C`.
- 안 멈추거나 백그라운드로 돌고 있으면:
  ```bash
  pkill -f face.py
  pkill -f send_sensors.py
  ```

---

## 5. 화면(디스플레이) 관련

이 LCD는 SPI라 HDMI와 **별개 DRM 장치**다. 그래서 `tvservice`(없음)나 `xrandr --output HDMI... --off`(→ `RRSetScreenSize BadMatch`)로 HDMI를 완전히 끄는 건 잘 안 된다.

- 출력 목록/위치 확인:
  ```bash
  DISPLAY=:0 xrandr
  # HDMI-A-2 = 외부 모니터, SPI-1 = LCD
  ```
- HDMI 모니터를 까맣게(끈 것처럼):
  ```bash
  DISPLAY=:0 xrandr --output HDMI-A-2 --brightness 0   # 되돌리기: --brightness 1
  ```
- 굳이 HDMI를 끌 필요는 없다. `face.py`가 알아서 LCD에만 그린다.

### LCD가 데스크톱조차 안 나올 때 (드라이버 미설치)
Waveshare 3.5" A타입 드라이버:
```bash
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show
chmod +x LCD35-show
./LCD35-show     # 자동 재부팅됨
```

---

## 6. 사전 조건 (서버 쪽)

- 라즈베리파이와 노트북이 **같은 Wi-Fi**.
- 노트북에서 백엔드가 외부 접속 허용으로 떠 있어야 함:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```
- `send_sensors.py` 안의 서버 IP가 현재 노트북 IP와 같은지 확인(바뀌면 수정).
- 연결 테스트(라즈베리파이에서):
  ```bash
  curl http://<노트북IP>:8000/api/sensors
  ```
