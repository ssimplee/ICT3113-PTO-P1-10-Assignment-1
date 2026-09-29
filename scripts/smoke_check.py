"""Check a running service with synthetic text; this is not a benchmark."""
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:18000')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    records = []

    def call(path, body=None, expected=200):
        data = None if body is None else json.dumps(body).encode()
        req = Request(args.url.rstrip('/') + path, data=data,
                      headers={'Content-Type': 'application/json'})
        try:
            response = urlopen(req, timeout=180)
        except HTTPError as error:
            response = error
        with response:
            result = json.loads(response.read())
            records.append({'path': path, 'status': response.status,
                            'request_id': response.headers.get('X-Request-ID'),
                            'body': result})
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(records, indent=2), encoding='utf-8')
            assert response.status == expected, records[-1]
            assert records[-1]['request_id'], records[-1]
        return result

    before = call('/stats')['total']
    ticket = call('/tickets', {'narrative': 'Synthetic connection check: my mortgage payment was charged twice.'}, 201)
    assert ticket['category'] in call('/stats')['categories']
    assert call('/stats')['total'] == before + 1
    assert any(row['id'] == ticket['id'] for row in call('/search?q=Synthetic%20connection%20check')['tickets'])
    call('/tickets', {'narrative': ''}, 400)
    call('/missing', expected=404)
    print('PASS: real HTTP classification, persistence, search, stats, validation and request IDs.')
    print('Evidence:', args.output)


if __name__ == '__main__':
    main()
