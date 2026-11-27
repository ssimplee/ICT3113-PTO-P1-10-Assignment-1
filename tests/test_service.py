"""Functional checks using a fake Ollama backend, not benchmark evidence."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'service'))
from app import CATEGORIES, create_app


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

    def test_all_categories_and_malformed_backend_responses(self):
        for category in CATEGORIES:
            with self.subTest(category=category):
                self.backend.return_value.json.return_value = {
                    'done': True, 'message': {'content': json.dumps({'category': category})}}
                self.assertEqual(self.client.post('/tickets', json={'narrative': 'Example'}).json['category'], category)
        for result in (None, [], {'done': False}, {'done': True},
                       {'done': True, 'message': {'content': 'not JSON'}},
                       {'done': True, 'message': {'content': '[]'}},
                       {'done': True, 'message': {'content': '{"category":"Mortgage","extra":true}'}}):
            with self.subTest(result=result):
                self.backend.return_value.json.return_value = result
                self.assertEqual(self.client.post('/tickets', json={'narrative': 'Example'}).status_code, 502)
        self.assertEqual(self.client.get('/stats').json['total'], 7)

    def test_http_validation_and_backend_connection_error(self):
        self.assertEqual(self.client.post('/tickets', data='plain text').status_code, 415)
        self.assertEqual(self.client.post('/tickets', data='{', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.get('/search').status_code, 400)
        self.backend.assert_not_called()
        self.backend.side_effect = requests.ConnectionError('fake offline backend')
        self.assertEqual(self.client.post('/tickets', json={'narrative': 'Example'}).status_code, 502)
        self.assertEqual(self.client.get('/stats').json['total'], 0)

    def test_single_model_log_records_no_escalation(self):
        self.client.post('/tickets', json={'narrative': 'one two three'})
        entry = json.loads(self.log.read_text().splitlines()[-1])
        self.assertEqual((entry['escalated'], entry['final_model'], entry['narrative_words']),
                         (False, 'test-model:fake', 3))
        self.assertIsNone(entry['second_model_ms'])


class CascadeTests(unittest.TestCase):
    LABEL = 'cascade[small=small:fake;large=large:fake;min_words=5]'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.log = Path(self.temp.name) / 'requests.jsonl'
        self.answers = {'small:fake': 'Credit reporting', 'large:fake': 'Debt collection'}
        self.calls = []

        def backend(url, json, timeout):
            self.calls.append(json['model'])
            answer = self.answers[json['model']]
            if isinstance(answer, Exception):
                raise answer
            response = Mock()
            response.json.return_value = {'done': True, 'message': {'content': '{"category":"%s"}' % answer}}
            return response

        self.config = {
            'TESTING': True, 'OLLAMA_MODEL': 'small:fake', 'CASCADE_LARGE_MODEL': 'large:fake',
            'CASCADE_MIN_WORDS': '5', 'DATABASE_PATH': str(Path(self.temp.name) / 'tickets.db'),
            'LOG_PATH': str(self.log), 'OLLAMA_HTTP_POST': backend,
        }
        self.client = create_app(self.config).test_client()

    def last_log(self):
        return json.loads(self.log.read_text().splitlines()[-1])

    def test_short_escalation_category_goes_to_large_model(self):
        result = self.client.post('/tickets', json={'narrative': 'one two three four five'})
        self.assertEqual((result.status_code, result.json['category']), (201, 'Debt collection'))
        self.assertEqual(self.calls, ['small:fake', 'large:fake'])
        entry = self.last_log()
        self.assertEqual((entry['escalated'], entry['final_model'], entry['first_category'], entry['category']),
                         (True, 'large:fake', 'Credit reporting', 'Debt collection'))
        self.assertGreaterEqual(entry['second_model_ms'], 0)

    def test_long_ticket_and_other_categories_keep_small_answer(self):
        long_ticket = self.client.post('/tickets', json={'narrative': 'one two three four five six'})
        self.assertEqual(long_ticket.json['category'], 'Credit reporting')
        self.assertEqual((self.last_log()['escalated'], self.last_log()['final_model']), (False, 'small:fake'))
        self.answers['small:fake'] = 'Mortgage'
        short_ticket = self.client.post('/tickets', json={'narrative': 'one two'})
        self.assertEqual(short_ticket.json['category'], 'Mortgage')
        self.assertFalse(self.last_log()['escalated'])
        self.assertEqual(self.calls, ['small:fake', 'small:fake'])

    def test_caller_cannot_tell_which_model_answered(self):
        escalated = self.client.post('/tickets', json={'narrative': 'short ticket'}).json
        kept = self.client.post('/tickets', json={'narrative': 'a much longer ticket than five words'}).json
        self.assertEqual({escalated['model'], kept['model'], self.last_log()['model']}, {self.LABEL})
        stored = self.client.get('/search', query_string={'q': 'ticket'}).json['tickets']
        self.assertEqual({ticket['model'] for ticket in stored}, {self.LABEL})

    def test_large_model_failure_is_not_stored(self):
        self.answers['large:fake'] = requests.Timeout('fake timeout')
        self.assertEqual(self.client.post('/tickets', json={'narrative': 'short ticket'}).status_code, 504)
        entry = self.last_log()
        self.assertEqual((entry['escalated'], entry['final_model'], entry['error']), (True, None, 'ollama_timeout'))
        self.assertEqual(self.client.get('/stats').json['total'], 0)

    def test_cascade_requires_a_word_threshold(self):
        for value in ('', 'many', '-1', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                create_app(dict(self.config, CASCADE_MIN_WORDS=value))


if __name__ == '__main__':
    unittest.main()
