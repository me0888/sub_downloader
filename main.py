from flask import Flask, Response, stream_with_context, request, render_template_string
import requests
import time

app = Flask(__name__)

TIMEOUT = 3

HTML = '''
<!doctype html>
<html>
<head>
    <title>Прокси сканер</title>
</head>
<body>
    <h1>🔎 9 Прокси сканер</h1>
    <form id="proxyForm">
        <label>IP сервера (прокси): <input type="text" name="ip" required></label><br>
        <label>Порт от: <input type="number" name="start_port" min="1" max="65535" value="1" required></label><br>
        <label>Порт до: <input type="number" name="end_port" min="1" max="65535" value="1000" required></label><br>
        <label>Пользователь: <input type="text" name="username"></label><br>
        <label>Пароль: <input type="password" name="password"></label><br>
        <button type="submit">Начать сканирование</button>
    </form>

    <h2>Результаты:</h2>
    <pre id="output"></pre>

    <script>
        const form = document.getElementById('proxyForm');
        const output = document.getElementById('output');
        let eventSource;

        form.addEventListener('submit', function(e) {
            e.preventDefault();

            if (eventSource) {
                eventSource.close();
            }
            output.textContent = '';

            const formData = new FormData(form);
            const params = new URLSearchParams(formData).toString();

            eventSource = new EventSource('/scan?' + params);

            eventSource.onmessage = function(e) {
                output.textContent += e.data + "\\n";
            };
            eventSource.onerror = function() {
                output.textContent += "\\n[Соединение закрыто]\\n";
                eventSource.close();
            };
        });
    </script>
</body>
</html>
'''

def test_proxy(ip, port, username, password):
    if username and password:
        proxy_auth = f"{username}:{password}@"
    else:
        proxy_auth = ""
    proxy_url = f"http://{proxy_auth}{ip}:{port}"

    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }

    try:
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=TIMEOUT)
        return r.status_code == 200
    except Exception:
        return False

def scan_ports(ip, username, password, start_port, end_port):
    for port in range(start_port, end_port + 1):
        status = test_proxy(ip, port, username, password)
        if status:
            yield f"data: ✅ Порт {port} работает\n\n"
        else:
            yield f"data: ❌ Порт {port} не работает\n\n"
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/scan')
def stream():
    ip = request.args.get('ip')
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    try:
        start_port = int(request.args.get('start_port', 1))
        end_port = int(request.args.get('end_port', 1000))
    except ValueError:
        return "Порт должен быть числом", 400

    if not ip:
        return "IP сервера обязателен", 400
    if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
        return "Порты должны быть в диапазоне 1-65535", 400
    if start_port > end_port:
        return "Порт от не может быть больше порта до", 400

    return Response(stream_with_context(scan_ports(ip, username, password, start_port, end_port)),
                    mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
