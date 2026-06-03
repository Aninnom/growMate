# GrowMate 라즈베리파이 센서 전송

라즈베리파이가 센서값을 읽어 **노트북 서버**로 보내고, 앱(홈 화면)이 그 값을 보여줍니다.

```
[라즈베리파이] --POST /api/sensors--> [노트북 FastAPI 서버] <--GET /api/sensors-- [웹앱(홈)]
```

## 1. 사전 조건

- **라즈베리파이와 노트북이 같은 Wi-Fi**에 연결돼 있어야 합니다.
- 노트북 서버가 `0.0.0.0:8000`으로 실행 중이어야 합니다(외부 접속 허용):
  ```
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```
- 노트북 Wi-Fi IP: **`172.17.67.118`** (바뀌면 노트북에서 `ipconfig`로 다시 확인)

## 2. 노트북 방화벽 허용 (한 번만)

Windows 방화벽이 8000 포트 인바운드를 막을 수 있습니다. **노트북에서 관리자 PowerShell**로 한 번 실행:

```powershell
New-NetFirewallRule -DisplayName "GrowMate 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

## 3. 라즈베리파이에서 실행

```bash
pip install requests
python3 send_sensors.py
```

- 처음엔 `TEST_MODE = True`(기본)라 **배선 없이 가짜 값**을 보냅니다 → 파이프라인부터 확인하세요.
- 잘 되면 홈 화면 센서 카드 숫자가 5초마다 바뀝니다.

## 4. 연결 확인

라즈베리파이에서 서버가 보이는지 먼저 테스트:

```bash
curl http://172.17.67.118:8000/api/sensors
```
JSON이 나오면 연결 OK. `Connection refused`/타임아웃이면 → Wi-Fi 동일망 여부, 서버 `--host 0.0.0.0`, 방화벽(2번)을 점검하세요.

## 5. 실제 센서로 전환

`send_sensors.py`의 `read_sensors_real()`에 실제 센서 읽기 코드를 채운 뒤 `TEST_MODE = False`로 바꿉니다.
DHT22(온습도) + MCP3008(토양/조도 아날로그) 예시 코드가 함수 주석에 들어 있습니다.

```bash
pip install adafruit-circuitpython-dht adafruit-circuitpython-mcp3xxx
```

## 보내는 데이터 형식

```json
{ "soil": 24, "temp": 24.6, "humid": 58, "light": 520 }
```
| 키 | 의미 | 단위 | 상태 판정(서버) |
|---|---|---|---|
| `soil` | 토양 수분 | % | 30 미만 → 주의 |
| `temp` | 온도 | °C | 15~28 벗어나면 주의 |
| `humid` | 습도 | % | 40~75 벗어나면 주의 |
| `light` | 조도 | lux | 500 미만 → 주의 |

가진 센서만 보내도 됩니다(없는 키 생략 가능). 상태(good/warn) 판정과 한글 라벨은 서버·앱이 알아서 합니다.
