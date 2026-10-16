"""Dummy CNF control-plane. Mimics telco CNF agent: configures data-plane + serves health/metrics."""
import os
import subprocess
import time
from flask import Flask, jsonify

app = Flask(__name__)
START = time.time()
FORWARDER_BIN = os.environ.get("FORWARDER_BIN", "./forwarder")

def forwarder_alive() -> bool:
    try:
        out = subprocess.run(["pgrep", "-f", "forwarder"], capture_output=True, timeout=2)
        return out.returncode == 0
    except Exception:
        return False

@app.route("/healthz")
def healthz():
    # failure injection: touch /tmp/fail to simulate CNF fault
    if os.path.exists("/tmp/fail"):
        return jsonify(status="fail", reason="injected fault"), 500
    if not forwarder_alive():
        return jsonify(status="degraded", reason="forwarder not running"), 503
    return jsonify(status="ok", uptime=int(time.time() - START)), 200

@app.route("/metrics")
def metrics():
    return (
        f'cnf_uptime_seconds {int(time.time()-START)}\n'
        f'cnf_forwarder_up {1 if forwarder_alive() else 0}\n',
        200, {"Content-Type": "text/plain"},
    )

@app.route("/")
def root():
    return jsonify(service="cnf-agent", forwarder_up=forwarder_alive()), 200

if __name__ == "__main__":
    # best-effort start C data-plane
    try:
        subprocess.Popen([FORWARDER_BIN])
    except Exception as e:
        print(f"forwarder start skipped: {e}", flush=True)
    app.run(host="0.0.0.0", port=8080)
