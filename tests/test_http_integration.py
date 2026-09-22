"""Real HTTP service-to-backend integration without model downloads."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

ROOT = Path(__file__).resolve().parents[1]


class HttpIntegrationTests(unittest.TestCase):
    def test_http_boundary_sequential_processing_and_restart(self):
        received = []
        active = 0
        max_active = 0
        entered = threading.Event()
        release = threading.Event()

        class Backend(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_POST(self):
                nonlocal active, max_active
                self.assert_path = self.path
                payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                received.append((self.path, payload))
                active += 1
                max_active = max(max_active, active)
                entered.set()
                release.wait(5)
                active -= 1
                body = json.dumps({'done': True, 'message': {'content': '{"category":"Mortgage"}'}}).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        with tempfile.TemporaryDirectory() as folder:
            backend = ThreadingHTTPServer(('127.0.0.1', 0), Backend)
            thread = threading.Thread(target=backend.serve_forever, daemon=True)
            thread.start()
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1', 0))
                port = reservation.getsockname()[1]
            base = f'http://127.0.0.1:{port}'
            env = dict(os.environ, OLLAMA_MODEL='test:fake',
                       OLLAMA_BASE_URL=f'http://127.0.0.1:{backend.server_port}',
                       DATABASE_PATH=str(Path(folder) / 'tickets.db'),
                       LOG_PATH=str(Path(folder) / 'requests.jsonl'), PORT=str(port))
            process = None

            def start():
                proc = subprocess.Popen([sys.executable, '-m', 'app'], cwd=ROOT / 'service',
                                        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                for _ in range(100):
                    if proc.poll() is not None:
                        self.fail('Service exited before becoming ready')
                    try:
                        if requests.get(base + '/stats', timeout=.2).status_code == 200:
                            return proc
                    except requests.RequestException:
                        pass
                    time.sleep(.05)
                proc.terminate()
                proc.wait(timeout=5)
                self.fail('Service did not become ready')

            try:
                process = start()
                self.assertEqual(requests.get(base + '/stats', timeout=2).json()['total'], 0)
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=2) as pool:
                    first = pool.submit(requests.post, base + '/tickets', json={'narrative': 'First mortgage'}, timeout=10)
                    self.assertTrue(entered.wait(3))
                    self.assertFalse(first.done(), 'POST must wait for the model')
                    second = pool.submit(requests.post, base + '/tickets', json={'narrative': 'Second mortgage'}, timeout=10)
                    # Keep the first backend call pending while another HTTP client connects.
                    time.sleep(.15)
                    self.assertEqual(len(received), 1)
                    release.set()
                    for future in (first, second):
                        self.assertEqual(future.result().status_code, 201)
                self.assertEqual(max_active, 1)
                self.assertEqual(len(received), 2)
                for path, payload in received:
                    self.assertEqual(path, '/api/chat')
                    self.assertEqual(payload['options']['num_gpu'], 0)
                    self.assertFalse(payload['stream'])
                process.terminate()
                process.wait(timeout=5)
                process = start()
                self.assertEqual(requests.get(base + '/stats', timeout=2).json()['total'], 2)
                result = requests.get(base + '/search', params={'q': 'First'}, timeout=2)
                self.assertEqual(result.json()['count'], 1)
                logs = [json.loads(line) for line in (Path(folder) / 'requests.jsonl').read_text().splitlines()]
                self.assertEqual(sum(row['status'] == 201 for row in logs), 2)
                self.assertIn(result.headers['X-Request-ID'], {row['request_id'] for row in logs})
            finally:
                release.set()
                if process is not None and process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                backend.shutdown()
                backend.server_close()
                thread.join(timeout=5)


if __name__ == '__main__':
    unittest.main()
