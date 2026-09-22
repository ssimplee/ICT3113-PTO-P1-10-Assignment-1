"""Functional checks using a fake Ollama backend, not benchmark evidence."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'service'))
from app import create_app


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.log = Path(self.temp.name) / 'requests.jsonl'
        self.backend = Mock()
        response = Mock()
        response.json.return_value = {'done': True, 'message': {'content': '{"category":"Mortgage"}'}}
        self.backend.return_value = response
        self.config = {
            'TESTING': True, 'OLLAMA_MODEL': 'test-model:fake',
            'DATABASE_PATH': str(Path(self.temp.name) / 'tickets.db'),
            'LOG_PATH': str(self.log), 'OLLAMA_HTTP_POST': self.backend,
        }
        self.app = create_app(self.config)
        self.client = self.app.test_client()

    def test_empty_create_search_stats_and_persistence(self):
        self.assertEqual(self.client.get('/stats').json['total'], 0)
        result = self.client.post('/tickets', json={'narrative': 'Mortgage rate is 5%_fixed'})
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json['category'], 'Mortgage')
        self.assertEqual(self.client.get('/search', query_string={'q': '%_'}).json['count'], 1)
        self.assertEqual(self.client.get('/search', query_string={'q': 'unmatched'}).json['count'], 0)
        stats = self.client.get('/stats').json
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['categories']['Mortgage'], 1)
        self.assertEqual(len(stats['categories']), 7)
        restarted = create_app(self.config).test_client()
        self.assertEqual(restarted.get('/stats').json['total'], 1)
        payload = self.backend.call_args.kwargs['json']
        self.assertFalse(payload['stream'])
        self.assertEqual(payload['options']['num_gpu'], 0)

    def test_invalid_input_and_failures_never_persist(self):
        for body in ({}, {'narrative': ''}, {'narrative': '  '}, {'narrative': 123}, []):
            self.assertGreaterEqual(self.client.post('/tickets', json=body).status_code, 400)
        self.backend.assert_not_called()
        self.backend.side_effect = requests.Timeout('fake timeout')
        self.assertEqual(self.client.post('/tickets', json={'narrative': 'Example'}).status_code, 504)
        self.backend.side_effect = None
        self.backend.return_value.json.return_value = {'done': True, 'message': {'content': '{"category":"Unknown"}'}}
        self.assertEqual(self.client.post('/tickets', json={'narrative': 'Example'}).status_code, 502)
        self.assertEqual(self.client.get('/stats').json['total'], 0)

    def test_every_request_logged_without_narrative(self):
        responses = [self.client.post('/tickets', json={'narrative': 'PRIVATE SENTINEL'}),
                     self.client.get('/missing'), self.client.post('/tickets', json={})]
        entries = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual(len(entries), len(responses))
        for entry, response in zip(entries, responses):
            self.assertEqual(entry['request_id'], response.headers['X-Request-ID'])
            self.assertEqual(entry['status'], response.status_code)
            self.assertGreaterEqual(entry['duration_ms'], 0)
        self.assertNotIn('PRIVATE SENTINEL', self.log.read_text())


if __name__ == '__main__':
    unittest.main()
