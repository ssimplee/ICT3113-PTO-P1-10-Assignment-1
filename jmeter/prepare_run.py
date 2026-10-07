"""Prepare an isolated run bundle. Never invokes JMeter, Docker or HTTP."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    "qwen06": "qwen3:0.6b-q4_K_M",
    "llama1": "llama3.2:1b-instruct-q4_K_M",
    "qwen17": "qwen3:1.7b-q4_K_M",
    "llama3": "llama3.2:3b-instruct-q4_K_M",
}
PROFILES = {
    "validation": (0, 60, (2, 2, 2)),
    "normal": (120, 900, (12, 2.4, 0.6)),
    "peak": (120, 600, (36, 7.2, 1.8)),
    "read-heavy": (120, 600, (12, 4.8, 1.2)),
    "stress": (120, 1800, (6, 1.2, 0.3)),
}


def prop(element, name, value, kind="stringProp"):
    node = element.find(f"*[@name='{name}']")
    if node is None:
        node = ET.SubElement(element, kind, name=name)
    node.text = str(value)


def prepare(profile, model, repeat, run_id, host):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", run_id):
        raise ValueError("Run ID must contain only letters, digits, underscores and hyphens")
    if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
        raise ValueError("Host must be an IPv4 address or hostname, without URL or port")
    if repeat not in (1, 2, 3):
        raise ValueError("Repeat must be 1, 2 or 3")
    output = ROOT / "jmeter" / "runs" / run_id
    if output.exists():
        raise ValueError(f"Refusing to overwrite existing run: {output}")
    tag = MODELS[model]
    pins = json.loads((ROOT / "docs/member4-model-manifest.json").read_text())
    pin = next(p for p in pins["accepted_candidates"] if p["tag"] == tag)
    golden = ROOT / "golden-set/golden_tickets_175_baseline.csv"
    with golden.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 175 and len({r["row"] for r in rows}) == 175
    assert all(10000 <= int(r["row"]) <= 10999 and r["narrative"].strip() for r in rows)
    seed = 1000 + repeat * 100
    random.Random(seed).shuffle(rows)
    tree = ET.parse(ROOT / "jmeter/load-test.jmx")
    plan_tree = tree.getroot().find("hashTree/hashTree")
    # Remove the disabled development group and its listener from formal bundles.
    children = list(plan_tree)
    for i, node in enumerate(children):
        if node.tag == "ThreadGroup" and node.get("enabled") == "false":
            plan_tree.remove(node)
            plan_tree.remove(children[i + 1])
    prop(tree.getroot().find("hashTree/TestPlan"), "TestPlan.serialize_threadgroups", "false", "boolProp")
    warmup, measured, rates = PROFILES[profile]
    groups = tree.findall(".//OpenModelThreadGroup")
    assert len(groups) == 3
    schedules = {}
    for i, group in enumerate(groups):
        rate = rates[i]
        if profile == "stress":
            factor = (1, 0.2, 0.05)[i]
            schedule = f"rate({6 * factor:g}/min) random_arrivals(120 sec) rate({6 * factor:g}/min) "
            for post_rate in (6, 12, 18, 24, 30, 36):
                step = post_rate * factor
                schedule += f"rate({step:g}/min) random_arrivals(300 sec) rate({step:g}/min) "
            schedule += "pause(360 sec)"
        else:
            schedule = f"rate({rate:g}/min) random_arrivals({warmup + measured} sec) rate({rate:g}/min) pause(360 sec)"
        prop(group, "OpenModelThreadGroup.schedule", schedule)
        prop(group, "OpenModelThreadGroup.random_seed", seed + i + 1, "longProp")
        schedules[group.get("testname")] = schedule
    for sampler in tree.findall(".//HTTPSamplerProxy"):
        prop(sampler, "HTTPSampler.domain", host)
        prop(sampler, "HTTPSampler.connect_timeout", 10000, "intProp")
        prop(sampler, "HTTPSampler.response_timeout", 300000, "intProp")
        if sampler.find("*[@name='HTTPSampler.method']").text == "POST":
            sampler.set("testname", "POST tickets")
    output.mkdir(parents=True)
    (output / "data").mkdir()
    with (output / "data/tickets.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["row", "payload"])
        for row in rows:
            writer.writerow([row["row"], json.dumps({"narrative": row["narrative"]}, ensure_ascii=False)])
    ET.indent(tree, space="  ")
    (output / "plan.jmx").write_bytes(ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True))
    shutil.copyfile(ROOT / "jmeter/results.properties", output / "results.properties")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest = dict(run_id=run_id, profile=profile, model_tag=tag, model_digest=pin["digest"],
                    repeat=repeat, host=host, port=18000, preparation_git_revision=revision,
                    warmup_seconds=warmup, measurement_seconds=measured, drain_seconds=360,
                    narrative_seed=seed, arrival_seeds=[seed + i + 1 for i in range(3)],
                    post_search_stats_rates_per_minute=rates, schedules=schedules,
                    golden_sha256=hashlib.sha256(golden.read_bytes()).hexdigest(),
                    status="PREPARED_NOT_RUN", search_query="payment",
                    limitations=["175-ticket category-selected subset, not the full natural workload",
                                 "Arrival schedule is seeded; concurrent assignment of CSV rows can vary",
                                 "Computer A differs from historical accuracy-test hardware"])
    manifest["file_sha256"] = {str(p.relative_to(output)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (output / "plan.jmx", output / "results.properties", output / "data/tickets.csv")}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Compose paths resolve relative to the repository's first compose file.
    relative = output.relative_to(ROOT).as_posix()
    override = {"services": {"service": {"environment": {"OLLAMA_MODEL": tag, "OLLAMA_TIMEOUT_SECONDS": "120"}, "volumes": [
        f"./{relative}/service-data:/data", f"./{relative}/service-logs:/logs"]}}}
    (output / "server.override.json").write_text(json.dumps(override, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, required=True)
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--repeat", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--host", default="192.168.1.5")
    args = parser.parse_args()
    print(prepare(args.profile, args.model, args.repeat, args.run_id, args.host))
    print("PREPARED ONLY. No Docker, JMeter or HTTP requests were executed.")
