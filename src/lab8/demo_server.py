"""Local presentation UI: python -m lab8.demo_server (run from src/)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from lab8.app import PUBLIC_CLAIMS
from lab8.db import load_jsonl

ROOT = Path(__file__).resolve().parent.parent
UI = Path(__file__).resolve().parent / 'demo_ui'
SHAPES = {'workflow', 'single', 'orchestrator', 'swarm'}
CLAIMS = {item['claim_id'] for item in load_jsonl(PUBLIC_CLAIMS)}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data, content_type='application/json; charset=utf-8'):
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/benchmark':
            try:
                data = json.loads((ROOT / 'reports' / 'benchmark.json').read_text(encoding='utf-8'))
                self.respond(200, {'shapes': data['by_shape'], 'claims': sorted(CLAIMS)})
            except (OSError, KeyError, ValueError):
                self.respond(500, {'error': 'Không đọc được benchmark công khai.'})
            return
        files = {'/': ('index.html', 'text/html; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8')}
        if path not in files:
            self.respond(404, {'error': 'Không tìm thấy trang.'})
            return
        filename, mime = files[path]
        self.respond(200, (UI / filename).read_bytes(), mime)

    def do_POST(self):
        if urlparse(self.path).path != '/api/run':
            self.respond(404, {'error': 'Không tìm thấy thao tác.'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 2048:
                raise ValueError('Dữ liệu không hợp lệ.')
            data = json.loads(self.rfile.read(length))
            shape, claim, seed = data['shape'], data['claim'], data['seed']
            if shape not in SHAPES or claim not in CLAIMS or type(seed) is not int or seed not in (11, 22, 33, 44, 55):
                raise ValueError('Hãy chọn shape, claim và seed hợp lệ.')
            with tempfile.TemporaryDirectory(prefix='lab8-ui-') as temp:
                env = os.environ.copy()
                env['PYTHONPATH'] = str(ROOT) + os.pathsep + env.get('PYTHONPATH', '')
                cmd = [sys.executable, '-m', 'lab8.run', '--shape', shape, '--claim-id', claim, '--seed', str(seed), '--db', str(Path(temp) / 'demo.sqlite')]
                process = subprocess.run(cmd, cwd=temp, env=env, capture_output=True, text=True, encoding='utf-8', timeout=30, check=True)
                result = json.loads(process.stdout)
                trace = json.loads((Path(temp) / result['trace_path']).read_text(encoding='utf-8'))
                allowed = ('run_id', 'status', 'proposal_amount', 'model_calls', 'tool_calls', 'cost_estimate', 'error_reason', 'committed_audit_count')
                output = {key: result.get(key) for key in allowed}
                output['refund_amount'] = sum(int(x.get('amount_vnd', 0)) for x in result.get('refund_effects', []))
                output['events'] = [str(event.get('kind', 'event')) for event in trace.get('events', [])]
                self.respond(200, output)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.respond(400, {'error': 'Dữ liệu không hợp lệ. Hãy chọn lại và thử lần nữa.'})
        except (OSError, subprocess.SubprocessError):
            self.respond(500, {'error': 'Không chạy được tình huống. Hãy kiểm tra terminal và môi trường Python.'})


def main():
    address = ('127.0.0.1', 8765)
    server = ThreadingHTTPServer(address, Handler)
    print('LogiX Lab UI: http://127.0.0.1:8765  (Ctrl+C để dừng)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
