"""CNF auto-healer: watches label app=cnf, probes /healthz, remediates."""
import os
import time
import urllib.request
import json
from kubernetes import client, config

NAMESPACE = os.environ.get("WATCH_NAMESPACE", "cnf-lab")
LABEL = os.environ.get("WATCH_LABEL", "app=cnf")
INTERVAL = int(os.environ.get("HEAL_INTERVAL", "10"))
FAIL_THRESHOLD = int(os.environ.get("FAIL_THRESHOLD", "2"))

failures: dict[str, int] = {}

def load_kube():
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()

def pod_ip_health(ip: str) -> bool:
    try:
        with urllib.request.urlopen(f"http://{ip}:8080/healthz", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False

def remediate(v1: client.CoreV1Api, pod: client.V1Pod):
    name = pod.metadata.name
    print(f"[healer] remediating {name}: collecting diag + restart", flush=True)
    # annotate for audit
    try:
        v1.patch_namespaced_pod(name, NAMESPACE, {"metadata": {"annotations": {"cnf-healer/last-remediation": time.strftime("%FT%TZ")}}})
    except Exception as e:
        print(f"[healer] annotate failed: {e}", flush=True)
    # collect logs (truncated) for runbook
    try:
        logs = v1.read_namespaced_pod_log(name, NAMESPACE, tail_lines=50)
        print(f"[healer] --- logs {name} ---\n{logs[-2000:]}\n--- end ---", flush=True)
    except Exception as e:
        print(f"[healer] log collect failed: {e}", flush=True)
    # restart = delete (Deployment recreates); real CNF would do graceful reset via API first
    try:
        v1.delete_namespaced_pod(name, NAMESPACE)
        print(f"[healer] deleted {name} for restart", flush=True)
    except Exception as e:
        print(f"[healer] delete failed: {e}", flush=True)
    failures[name] = 0

def main():
    load_kube()
    v1 = client.CoreV1Api()
    print(f"[healer] watching ns={NAMESPACE} label={LABEL}", flush=True)
    while True:
        try:
            pods = v1.list_namespaced_pod(NAMESPACE, label_selector=LABEL).items
            for pod in pods:
                name = pod.metadata.name
                phase = pod.status.phase
                ip = pod.status.pod_ip
                ready = all(c.ready for c in (pod.status.container_statuses or []) if c.state)
                healthy = pod_ip_health(ip) if ip and phase == "Running" else False
                if phase != "Running" or not ready or not healthy:
                    failures[name] = failures.get(name, 0) + 1
                    print(f"[healer] unhealthy {name} phase={phase} ready={ready} http_ok={healthy} count={failures[name]}", flush=True)
                    if failures[name] >= FAIL_THRESHOLD:
                        remediate(v1, pod)
                else:
                    if failures.get(name):
                        print(f"[healer] recovered {name}", flush=True)
                    failures[name] = 0
        except Exception as e:
            print(f"[healer] loop error: {e}", flush=True)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
