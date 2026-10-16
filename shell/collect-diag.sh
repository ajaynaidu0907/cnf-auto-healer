#!/bin/bash
# Linux CNF diag collector - run inside cluster via kubectl debug or on node.
# Usage: ./collect-diag.sh <namespace> <label>
set -euo pipefail
NS=${1:-cnf-lab}
LABEL=${2:-app=cnf}
echo "== pods =="
kubectl get pods -n "$NS" -l "$LABEL" -o wide
echo "== describes =="
kubectl describe pods -n "$NS" -l "$LABEL" | tail -n 120
echo "== logs =="
for p in $(kubectl get pods -n "$NS" -l "$LABEL" -o jsonpath='{.items[*].metadata.name}'); do
  echo "--- $p ---"
  kubectl logs -n "$NS" "$p" --tail=50 || true
done
echo "== events =="
kubectl get events -n "$NS" --sort-by=.lastTimestamp | tail -n 30
echo "== node net (run on node if needed) =="
ss -tulpn || true
ip route || true
dmesg | tail -n 30 || true
