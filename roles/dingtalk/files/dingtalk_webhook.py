#!/usr/bin/env python3
"""
Alertmanager → DingTalk Webhook Bridge
从环境变量读取 DINGTALK_TOKEN，不硬编码
"""
import os, json, http.server, urllib.request

TOKEN = os.environ.get('DINGTALK_TOKEN', '')
DINGTALK_URL = 'https://oapi.dingtalk.com/robot/send?access_token=' + TOKEN

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

            icon = 'Rocket' if a.get('status') == 'firing' else 'WhiteCheckMark'
            lines.append('')
            lines.append(icon + ' [' + severity.upper() + '] ' + alertname)
            lines.append('Instance: ' + instance)
            lines.append('Detail: ' + summary)

        msg = {'msgtype': 'text', 'text': {'content': '\n'.join(lines)}}
        req = urllib.request.Request(
            DINGTALK_URL,
            data=json.dumps(msg).encode(),
            headers={'Content-Type': 'application/json'}
        )
        try:
            urllib.request.urlopen(req, timeout=5)
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
    http.server.HTTPServer(('0.0.0.0', 8060), Handler).serve_forever()
