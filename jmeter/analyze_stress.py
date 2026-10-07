"""Offline analysis of the prepared six-step stress profile. Sends no traffic."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from analyze_run import percentile


def analyze(folder):
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8-sig'))
    assert manifest['profile'] == 'stress' and manifest['measurement_seconds'] == 1800
    log = (folder / 'jmeter.log').read_text(encoding='utf-8-sig')
    starts = re.findall(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}).*StandardJMeterEngine: Running the test!', log, re.M)
    assert len(starts) == 1
    tz = timezone(timedelta(hours=8))
    start = datetime.strptime(starts[0], '%Y-%m-%d %H:%M:%S,%f').replace(tzinfo=tz)
    begin = round(start.timestamp() * 1000) + manifest['warmup_seconds'] * 1000
    with (folder / 'results.jtl').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    server = [json.loads(line) for line in (folder / 'service-logs/requests.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    index = defaultdict(list)
    for row in server:
        index[row['request_id']].append(row)
    expected = {'POST tickets': ('POST', '/tickets'), 'GET search': ('GET', '/search'), 'GET stats': ('GET', '/stats')}
    issues = []
    for row in rows:
        found = index[row['request_id']]
        if len(found) != 1:
            issues.append({'request_id': row['request_id'], 'matches': len(found)})
        elif (str(found[0]['status']) != row['responseCode'] or
              (found[0]['method'], found[0]['path']) != expected[row['label']] or
              found[0]['model'] != manifest['model_tag']):
            issues.append({'request_id': row['request_id'], 'reason': 'status/endpoint/model mismatch'})
    steps = []
    for i, rate in enumerate((6, 12, 18, 24, 30, 36)):
        left, right = begin + i * 300000, begin + (i + 1) * 300000
        metrics = {}
        for label in expected:
            group = [r for r in rows if r['label'] == label]
            cohort = [r for r in group if left <= int(r['timeStamp']) < right]
            complete = [r for r in group if r['success'] == 'true' and left <= int(r['timeStamp']) + int(r['elapsed']) < right]
            pending = [r for r in group if int(r['timeStamp']) < right <= int(r['timeStamp']) + int(r['elapsed'])]
            v = [int(r['elapsed']) for r in cohort]
            errors = sum(r['success'] != 'true' for r in cohort)
            metrics[label] = dict(arrivals=len(cohort), completions=len(complete), throughput_per_min=len(complete) / 5,
                error_percent=100 * errors / len(cohort) if cohort else None,
                p50_ms=percentile(v, .5), p95_ms=percentile(v, .95), p99_ms=percentile(v, .99),
                pending_all_arrivals_at_step_end=len(pending))
        post = metrics['POST tickets']
        post['throughput_percent_of_actual_arrivals'] = 100 * post['completions'] / post['arrivals'] if post['arrivals'] else None
        post['throughput_percent_of_target'] = 100 * post['throughput_per_min'] / rate
        passed = (post['arrivals'] > 0 and post['throughput_percent_of_actual_arrivals'] >= 95
                  and post['error_percent'] <= 1 and post['p95_ms'] <= 30000)
        steps.append(dict(post_target_per_min=rate, start_sgt=datetime.fromtimestamp(left / 1000, tz).isoformat(),
                          end_sgt=datetime.fromtimestamp(right / 1000, tz).isoformat(),
                          numeric_limits_pass=passed, endpoints=metrics))
    last = begin + 1800000
    ids = {r['request_id'] for r in rows}
    result = dict(run_id=manifest['run_id'], engine_start_sgt=start.isoformat(), steps=steps,
        whole_run_requests=len(rows), whole_run_failures=sum(r['success'] != 'true' for r in rows),
        reconciliation_problems=issues,
        duplicate_client_ids=[rid for rid, count in Counter(r['request_id'] for r in rows).items() if count != 1],
        extra_service_records=[r for r in server if r['request_id'] not in ids],
        final_completion_seconds_after_arrivals_end=round(max(0, max(int(r['timeStamp']) + int(r['elapsed']) for r in rows) - last) / 1000, 3),
        jmeter_warnings_errors=[line for line in log.splitlines() if re.search(r'\b(WARN|ERROR)\b', line)],
        method='Start-time cohorts; interpolated (n-1)*p percentiles; completion throughput includes earlier-step carry-over. Compare throughput with actual offered arrivals; also show nominal target ratio. Six finite steps do not prove indefinite stability.')
    (folder / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    lines = ['# Llama 1B stress results', '', '| Target POST/min | Arrivals | Completions | Throughput/min | POST p95 (s) | Errors (%) | Pending at step end | Numeric limits |', '|---:|---:|---:|---:|---:|---:|---:|---|']
    for step in steps:
        p = step['endpoints']['POST tickets']
        lines.append(f"| {step['post_target_per_min']} | {p['arrivals']} | {p['completions']} | {p['throughput_per_min']:.2f} | {p['p95_ms']/1000:.2f} | {p['error_percent']:.2f} | {p['pending_all_arrivals_at_step_end']} | {'PASS' if step['numeric_limits_pass'] else 'FAIL'} |")
    lines += ['', result['method'], '', f"Last client completion was {result['final_completion_seconds_after_arrivals_end']} seconds after the arrival schedule ended.", '', 'Source: analysis.json, results.jtl, jmeter.log and service-logs/requests.jsonl in this folder.']
    (folder / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_folder', type=Path)
    print(json.dumps(analyze(parser.parse_args().run_folder), indent=2))
