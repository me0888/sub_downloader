from flask import Flask, Response, stream_with_context
import requests
import socks
import socket
import time

# ==== Настройки ====
PROXY_IP = '12.87.98.78'
USERNAME = 'ed123'
PASSWORD = 'jo998'
START_PORT = 1
END_PORT = 1000  # Уменьшено для примера, можешь увеличить
TIMEOUT = 3
# ====================

app = Flask(__name__)

def test_proxy(port):
    socks.set_default_proxy(socks.SOCKS5, PROXY_IP, port, username=USERNAME, password=PASSWORD)
    socket.socket = socks.socksocket
    try:
        r = requests.get('http://httpbin.org/ip', timeout=TIMEOUT)
        return r.status_code == 200
    except:
        return False

def scan_ports():
    for port in range(START_PORT, END_PORT + 1):
        status = test_proxy(port)
        if status:
            yield f"data: ✅ Порт {port} работает\n\n"
        else:
            yield f"data: ❌ Порт {port} не работает\n\n"
        time.sleep(0.1)  # чтоб не зафлудить

@app.route('/')
def index():
    return '''
    <h1>🔎 Прокси сканер</h1>
    <p><a href="/scan">Hi, Начать сканирование портов</a></p>
    <pre id="output"></pre>
    <script>
        const output = document.getElementById("output");
        const eventSource = new EventSource("/scan");
        eventSource.onmessage = function(e) {
            output.textContent += e.data + "\\n";
        }
    </script>
    '''

@app.route('/scan')
def stream():
    return Response(stream_with_context(scan_ports()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
