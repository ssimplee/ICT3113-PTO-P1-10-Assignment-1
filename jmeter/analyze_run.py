"""Offline summary of a fixed-rate run; uses Singapore JMeter engine timestamps."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re


def percentile(values, fraction):
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * fraction
    low = int(position)
    return round(values[low] + (values[min(low + 1, len(values) - 1)] - values[low]) * (position - low), 3)


def analyze(folder):
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8-sig'))
    if manifest['profile'] == 'stress':
        raise ValueError('Stress requires separate per-step analysis')
    log = (folder / 'jmeter.log').read_text(encoding='utf-8-sig')
    matches = re.findall(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}).*StandardJMeterEngine: Running the test!', log, re.M)
    if len(matches) != 1:
        raise ValueError('Expected exactly one engine start in jmeter.log')
    start = datetime.strptime(matches[0], '%Y-%m-%d %H:%M:%S,%f').replace(tzinfo=timezone(timedelta(hours=8)))
    begin = int(start.timestamp() * 1000) + manifest['warmup_seconds'] * 1000
    end = begin + manifest['measurement_seconds'] * 1000
    with (folder / 'results.jtl').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    service = [json.loads(line) for line in (folder / 'service-logs/requests.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    indexed = defaultdict(list)
    for row in service:
        indexed[row['request_id']].append(row)
    duplicates = [rid for rid, count in Counter(r['request_id'] for r in rows).items() if count != 1]
    problems = []
    expected = {'POST tickets': ('POST', '/tickets'), 'GET search': ('GET', '/search'), 'GET stats': ('GET', '/stats')}
    for row in rows:
        found = indexed[row['request_id']]
        if len(found) != 1:
            problems.append({'request_id': row['request_id'], 'matches': len(found)})
        elif (str(found[0]['status']) != row['responseCode'] or
              (found[0]['method'], found[0]['path']) != expected[row['label']] or
              found[0]['model'] != manifest['model_tag']):
            problems.append({'request_id': row['request_id'], 'reason': 'status/endpoint/model mismatch'})
    endpoints = {}
    for label in expected:
        all_rows = [r for r in rows if r['label'] == label]
        cohort = [r for r in all_rows if begin <= int(r['timeStamp']) < end]
        completed = [r for r in all_rows if r['success'] == 'true' and begin <= int(r['timeStamp']) + int(r['elapsed']) < end]
        late = [r for r in cohort if int(r['timeStamp']) + int(r['elapsed']) >= end]
        values = [int(r['elapsed']) for r in cohort]
        failures = sum(r['success'] != 'true' for r in cohort)
        endpoints[label] = dict(measured_arrivals=len(cohort), successful_completions_in_window=len(completed),
            completions_per_minute=round(len(completed) * 60 / manifest['measurement_seconds'], 4),
            failures=failures, error_percent=round(100 * failures / len(cohort), 3) if cohort else None,
            p50_ms=percentile(values, .5), p95_ms=percentile(values, .95), p99_ms=percentile(values, .99),
            pending_at_window_end=len(late))
    ids = {r['request_id'] for r in rows}
    result = dict(run_id=manifest['run_id'], model=manifest['model_tag'],
        engine_start_sgt=start.isoformat(),
        measurement_start_sgt=datetime.fromtimestamp(begin / 1000, start.tzinfo).isoformat(),
        measurement_end_sgt=datetime.fromtimestamp(end / 1000, start.tzinfo).isoformat(),
        percentile_method='linear interpolation at (n-1)*p; all attempts in start-time cohort',
        whole_run_requests=len(rows), whole_run_failures=sum(r['success'] != 'true' for r in rows),
        endpoints=endpoints, duplicate_client_ids=duplicates, reconciliation_problems=problems,
        extra_service_records=[r for r in service if r['request_id'] not in ids],
        jmeter_warnings_errors=[line for line in log.splitlines() if re.search(r'\b(WARN|ERROR)\b', line)])
    (folder / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_folder', type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.run_folder), indent=2))
