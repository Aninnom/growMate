#!/usr/bin/env python3
"""
GrowMate 라즈베리파이 → 노트북 서버 센서 전송기.

라즈베리파이에서 센서를 주기적으로 읽어 노트북의 FastAPI 서버로 POST 한다.
서버는 최신값을 저장하고, 앱(홈 화면)이 그 값을 10초마다 폴링해서 보여준다.

전송 형식 (POST http://<노트북IP>:8000/api/sensors):
    {"soil": 24, "temp": 24.6, "humid": 58, "light": 520}
  - 가진 센서만 보내도 됨 (없는 키는 생략 가능)
  - soil: 토양 수분 %, temp: 온도 °C, humid: 습도 %, light: 조도 lux

준비:
    pip install requests
실행:
    python3 send_sensors.py
"""
import time
import random

import requests

# ── 설정 ────────────────────────────────────────────────────────
# 노트북의 Wi-Fi IP. (노트북에서 ipconfig 로 확인 / IP 가 바뀌면 여기도 수정)
SERVER_URL = "http://172.17.67.118:8000/api/sensors"
INTERVAL_SEC = 5          # 몇 초마다 보낼지
TEST_MODE = True          # True: 가짜 값 전송(배선 없이 파이프라인 테스트). 실제 센서 연결 후 False.


# ── 센서 읽기 ────────────────────────────────────────────────────
def read_sensors_test():
    """하드웨어 없이 테스트용 가짜 값. 매번 조금씩 흔들리는 값을 만든다."""
    return {
        "soil": random.randint(15, 70),
        "temp": round(random.uniform(20, 30), 1),
        "humid": random.randint(40, 70),
        "light": random.randint(300, 900),
    }


def read_sensors_real():
    """
    실제 센서 읽기. 사용하는 부품에 맞게 채운다.
    예) 온습도 = DHT22, 토양수분·조도 = 아날로그 → MCP3008(ADC) 로 읽음.

    먼저 라이브러리 설치:
        pip install adafruit-circuitpython-dht adafruit-circuitpython-mcp3xxx

    --- 온습도 (DHT22, 데이터핀 GPIO4 예시) ---
        import board, adafruit_dht
        dht = adafruit_dht.DHT22(board.D4)      # 모듈 최상단에서 1번만 생성 권장
        temp = dht.temperature                  # °C
        humid = dht.humidity                    # %

    --- 토양수분 / 조도 (MCP3008 SPI ADC) ---
        import board, busio, digitalio
        from adafruit_mcp3xxx.mcp3008 import MCP3008
        from adafruit_mcp3xxx.analog_in import AnalogIn
        spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = digitalio.DigitalInOut(board.D5)
        mcp = MCP3008(spi, cs)
        soil_raw = AnalogIn(mcp, 0).value       # CH0, 0~65535
        light_raw = AnalogIn(mcp, 1).value      # CH1, 0~65535
        # 센서 특성에 맞게 % / lux 로 환산 (아래는 예시, 보정 필요)
        soil = round((1 - soil_raw / 65535) * 100)   # 젖을수록 값↑ 가 되도록 보정
        light = round(light_raw / 65535 * 1000)
    """
    raise NotImplementedError(
        "read_sensors_real() 에 실제 센서 읽기 코드를 채운 뒤 TEST_MODE = False 로 바꾸세요."
    )


# ── 메인 루프 ────────────────────────────────────────────────────
def main():
    read = read_sensors_test if TEST_MODE else read_sensors_real
    print(f"[GrowMate] 전송 시작 → {SERVER_URL}  (간격 {INTERVAL_SEC}s, TEST_MODE={TEST_MODE})")
    while True:
        try:
            data = read()
            res = requests.post(SERVER_URL, json=data, timeout=5)
            print(f"보냄 {data} → {res.status_code} {res.text[:80]}")
        except requests.exceptions.RequestException as e:
            print(f"전송 실패(네트워크): {e}")
        except Exception as e:
            print(f"센서 읽기/전송 오류: {e}")
        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()
