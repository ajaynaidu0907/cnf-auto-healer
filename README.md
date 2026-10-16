# CNF Auto-Healer Operator (Local DevOps Lab)

Local project for 1-YOE targeting **Cloud-Native CNF Platform** roles.
Simulates what a Platform Team does: run a telco-like CNF (Python + C),
then auto-detect + auto-remediate failures in Kubernetes.

## What it proves (maps to your JD)
- **Python + Shell + C**: `app/forwarder.c` (data-plane) + `app/cnf-agent.py` (control-plane) + `shell/*.sh` diagnostics
- **Linux**: `ip, ss, tcpdump, dmesg, journalctl` collectors
- **Docker/K8s troubleshooting**: CrashLoop, readiness failures, packet-loss injection, `kubectl debug`
- **IaC**: Terraform provisions Kind cluster, Ansible bootstraps + deploys (stand-in for KVM/RHV/OpenStack/OpenShift concepts)
- **CI/CD Jenkins**: lint -> test -> build -> Trivy scan -> deploy
- **DevSecOps**: Trivy, non-root images, readOnlyFS, Kyverno policies

## Quick start (Windows + WSL2 + Docker Desktop)
```powershell
# in WSL2 Ubuntu:
kind create cluster --config kind-config.yaml
docker build -t cnf:local ./app
docker build -t cnf-healer:local ./operator
kind load docker-image cnf:local cnf-healer:local
kubectl apply -f k8s/
kubectl apply -f policies/
# inject failure:
kubectl exec -it deploy/cnf -- touch /tmp/fail
# watch healer fix it:
kubectl logs -f deploy/cnf-healer
kubectl get events --sort-by=.lastTimestamp
```

## Failure modes demoed
1. `touch /tmp/fail` -> `/healthz` 500s -> healer restarts + collects logs
2. Kill `forwarder` process -> control-plane marks degraded -> healer execs diag script
3. `tc qdisc add dev eth0 root netem loss 30%` -> latency alert -> healer annotates + scales

## Repo layout
```
app/           dummy CNF (Python + C)
operator/      auto-healer (Python k8s client)
shell/         Linux diag collectors
k8s/           manifests (works on Kind, K3s, MicroShift/OpenShift)
terraform/     local Kind provisioning
ansible/       bootstrap + deploy (KVM/RHV analogue via VMs)
jenkins/       Jenkinsfile
policies/      Kyverno (no :latest, non-root, readOnlyFS)
monitoring/    PrometheusRule
```

See `docs/INTERVIEW.md` for talking points.
