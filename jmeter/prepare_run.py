"""Prepare an isolated run bundle. Never invokes JMeter, Docker or HTTP."""
import argparse
import csv
import hashlib
import json
import math
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
# Assignment 2 speed test: POST only, rate and run length derived from S, the middle of
# three warm top-model timings. Cascade values are CASCADE_MIN_WORDS for Settings A and B.
A2_PROFILE = "a2-speed"
A2_WORKLOAD = ROOT / "jmeter/a2-workload"
CASCADES = {"cascade-a": 223, "cascade-b": 142}


def read_tickets(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def a2_timing(s_seconds):
    timeout = math.ceil(max(10 * s_seconds, 300))
    return dict(rate=30 / s_seconds, measured=math.ceil(max(s_seconds, 5) * 60),
                timeout=timeout, drain=timeout + 60)


def prop(element, name, value, kind="stringProp"):
    node = element.find(f"*[@name='{name}']")
    if node is None:
        node = ET.SubElement(element, kind, name=name)
    node.text = str(value)


def prepare(profile, model, repeat, run_id, host, s_seconds=None, workload_dir=A2_WORKLOAD):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", run_id):
        raise ValueError("Run ID must contain only letters, digits, underscores and hyphens")
    if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
        raise ValueError("Host must be an IPv4 address or hostname, without URL or port")
    if repeat not in (1, 2, 3):
        raise ValueError("Repeat must be 1, 2 or 3")
    output = ROOT / "jmeter" / "runs" / run_id
    if output.exists():
        raise ValueError(f"Refusing to overwrite existing run: {output}")
    a2 = profile == A2_PROFILE
    if model in CASCADES and not a2:
        raise ValueError(f"Cascade configurations need --profile {A2_PROFILE}")
    if a2 and not (s_seconds and math.isfinite(s_seconds) and s_seconds > 0):
        raise ValueError(f"--s-seconds must be a positive number for {A2_PROFILE}")
    tag = MODELS["llama1" if model in CASCADES else model]
    large_tag = MODELS["llama3"] if model in CASCADES else ""
    pins = json.loads((ROOT / "docs/member4-model-manifest.json").read_text())
    digests = {p["tag"]: p["digest"] for p in pins["accepted_candidates"]}
    golden = ROOT / "golden-set/golden_tickets_175_baseline.csv"
    rows = read_tickets(golden)
    assert len(rows) == 175 and len({r["row"] for r in rows}) == 175
    assert all(10000 <= int(r["row"]) <= 10999 and r["narrative"].strip() for r in rows)
    seed = 1000 + repeat * 100
    if a2:
        golden_rows = {r["row"] for r in rows}
        timing = a2_timing(s_seconds)
        rows = read_tickets(workload_dir / "workload.csv")
        warmup_rows = read_tickets(workload_dir / "warmup.csv")
        ids = [r["row"] for r in rows + warmup_rows]
        if len(warmup_rows) != 3:
            raise ValueError("warmup.csv must hold exactly three tickets")
        if len(set(ids)) != len(ids) or golden_rows & set(ids):
            raise ValueError("Workload and warm-up rows must be distinct and outside the golden set")
        if not all(r["narrative"].strip() for r in rows + warmup_rows):
            raise ValueError("Workload and warm-up narratives must not be blank")
        # Tickets are sent once, in file order: a repeated ticket would hit Ollama's prompt cache.
        needed = math.ceil(1.7 * timing["measured"] * timing["rate"] / 60)
        if len(rows) < needed:
            raise ValueError(f"workload.csv has {len(rows)} tickets; random arrivals need at least {needed}")
    else:
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
    if a2:
        children = list(plan_tree)
        for i, node in enumerate(children):
            if node.tag == "OpenModelThreadGroup" and node.get("testname") != "POST arrivals":
                plan_tree.remove(node)
                plan_tree.remove(children[i + 1])
        dataset = tree.find(".//CSVDataSet")
        prop(dataset, "recycle", "false", "boolProp")
        prop(dataset, "stopThread", "true", "boolProp")
        warmup, measured, rates = 0, timing["measured"], (timing["rate"],)
        drain, response_timeout = timing["drain"], timing["timeout"]
    else:
        warmup, measured, rates = PROFILES[profile]
        drain, response_timeout = 360, 300
    groups = tree.findall(".//OpenModelThreadGroup")
    assert len(groups) == len(rates)
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
            schedule = f"rate({rate:g}/min) random_arrivals({warmup + measured} sec) rate({rate:g}/min) pause({drain} sec)"
        prop(group, "OpenModelThreadGroup.schedule", schedule)
        prop(group, "OpenModelThreadGroup.random_seed", seed + i + 1, "longProp")
        schedules[group.get("testname")] = schedule
    for sampler in tree.findall(".//HTTPSamplerProxy"):
        prop(sampler, "HTTPSampler.domain", host)
        prop(sampler, "HTTPSampler.connect_timeout", 10000, "intProp")
        prop(sampler, "HTTPSampler.response_timeout", response_timeout * 1000, "intProp")
        if sampler.find("*[@name='HTTPSampler.method']").text == "POST":
            sampler.set("testname", "POST tickets")
    output.mkdir(parents=True)
    (output / "data").mkdir()
    with (output / "data/tickets.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["row", "payload"])
        for row in rows:
            writer.writerow([row["row"], json.dumps({"narrative": row["narrative"]}, ensure_ascii=False)])
    hashed = [output / "plan.jmx", output / "results.properties", output / "data/tickets.csv"]
    if a2:
        hashed.append(output / "data/warmup.json")
        hashed[-1].write_text(json.dumps([{"row": r["row"], "narrative": r["narrative"]} for r in warmup_rows],
                                         indent=2) + "\n", encoding="utf-8", newline="\n")
    ET.indent(tree, space="  ")
    (output / "plan.jmx").write_bytes(ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True))
    shutil.copyfile(ROOT / "jmeter/results.properties", output / "results.properties")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest = dict(run_id=run_id, profile=profile, model_tag=tag, model_digest=digests[tag],
                    repeat=repeat, host=host, port=18000, preparation_git_revision=revision,
                    warmup_seconds=warmup, measurement_seconds=measured, drain_seconds=drain,
                    narrative_seed=seed, arrival_seeds=[seed + i + 1 for i in range(len(rates))],
                    post_search_stats_rates_per_minute=rates, schedules=schedules,
                    golden_sha256=hashlib.sha256(golden.read_bytes()).hexdigest(),
                    status="PREPARED_NOT_RUN", search_query="payment",
                    limitations=["175-ticket category-selected subset, not the full natural workload",
                                 "Arrival schedule is seeded; concurrent assignment of CSV rows can vary",
                                 "Computer A differs from historical accuracy-test hardware"])
    environment = {"OLLAMA_MODEL": tag, "OLLAMA_TIMEOUT_SECONDS": "120"}
    if a2:
        for key in ("post_search_stats_rates_per_minute", "narrative_seed", "search_query"):
            del manifest[key]
        manifest.update(
            configuration=model, large_model_tag=large_tag, large_model_digest=digests.get(large_tag, ""),
            cascade_min_words=CASCADES.get(model), s_seconds=s_seconds,
            post_rate_per_minute=timing["rate"], mean_interarrival_seconds=2 * s_seconds,
            response_timeout_seconds=response_timeout,
            workload_rows=[r["row"] for r in rows], warmup_rows=[r["row"] for r in warmup_rows],
            limitations=["Random arrivals: the number of tickets sent varies around rate x run length",
                         "Tickets are sent once each, in workload.csv order, and never recycled",
                         "Warm-up tickets are sent by Prepare-Server.ps1 before the run, not by JMeter"])
        environment.update(CASCADE_LARGE_MODEL=large_tag,
                           CASCADE_MIN_WORDS=str(CASCADES[model]) if large_tag else "")
    manifest["file_sha256"] = {str(p.relative_to(output)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in hashed}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Compose paths resolve relative to the repository's first compose file.
    relative = output.relative_to(ROOT).as_posix()
    override = {"services": {"service": {"environment": environment, "volumes": [
        f"./{relative}/service-data:/data", f"./{relative}/service-logs:/logs"]}}}
    (output / "server.override.json").write_text(json.dumps(override, indent=2) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=[*PROFILES, A2_PROFILE], required=True)
    parser.add_argument("--model", choices=[*MODELS, *CASCADES], required=True)
    parser.add_argument("--s-seconds", type=float, help=f"S for {A2_PROFILE}: middle of three warm top-model timings")
    parser.add_argument("--repeat", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--host", default="192.168.1.5")
    args = parser.parse_args()
    print(prepare(args.profile, args.model, args.repeat, args.run_id, args.host, args.s_seconds))
    print("PREPARED ONLY. No Docker, JMeter or HTTP requests were executed.")
