#!/usr/bin/env python3
"""
Alertmanager → DingTalk Webhook Bridge
支持加签（HMAC-SHA256）和纯 Token 两种模式
"""
import os, json, http.server, urllib.request, base64, hashlib, hmac, time, urllib.parse

TOKEN = os.environ.get('DINGTALK_TOKEN', '')
SECRET = os.environ.get('DINGTALK_SECRET', '')
BASE_URL = 'https://oapi.dingtalk.com/robot/send?access_token=' + TOKEN

def build_url():
    """构造请求 URL，如果配置了加签密钥则追加签名参数"""
    if SECRET:
        timestamp = str(round(time.time() * 1000))
        sign_str = timestamp + '\n' + SECRET
        signature = base64.b64encode(
            hmac.new(SECRET.encode('utf-8'), sign_str.encode('utf-8'),
                     digestmod=hashlib.sha256).digest()
        ).decode('utf-8')
        return BASE_URL + '&timestamp=' + timestamp + '&sign=' + urllib.parse.quote(signature)
    return BASE_URL

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))

        status = data.get('status', 'unknown').upper()
        alerts = data.get('alerts', [])

        lines = ['# Infrastructure Monitoring Alert', '---']
        lines.append('Status: ' + status + ' | Count: ' + str(len(alerts)))

        for a in alerts:
            labels = a.get('labels', {})
            annotations = a.get('annotations', {})
            severity = labels.get('severity', '?')
            alertname = labels.get('alertname', '?')
            instance = labels.get('instance', '?')
            summary = annotations.get('summary', '')

            icon = '【故障】' if a.get('status') == 'firing' else '【恢复】'
            lines.append('')
            lines.append(icon + ' [' + severity.upper() + '] ' + alertname)
            lines.append('Instance: ' + instance)
            lines.append('Detail: ' + summary)

        msg = {'msgtype': 'text', 'text': {'content': '\n'.join(lines)}}
        url = build_url()
        req = urllib.request.Request(
            url,
            data=json.dumps(msg).encode(),
            headers={'Content-Type': 'application/json'}
        )
        try:
            resp = urllib.request.urlopen(req, timeout=5)
            body = resp.read().decode()
            print('DingTalk response:', body)
        except Exception as e:
            print('DingTalk send failed:', e)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    if not TOKEN:
        print('WARNING: DINGTALK_TOKEN not set. Bot will not send messages.')
    if SECRET:
        print('DingTalk sign mode enabled (HMAC-SHA256)')
    http.server.HTTPServer(('0.0.0.0', 8060), Handler).serve_forever()
