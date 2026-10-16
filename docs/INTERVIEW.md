# Interview talking points (1-YOE)
1. "CNF = containerized network function. Mine has C data-plane + Python control-plane, like real UPF/firewall split."
2. "Healer watches label app=cnf, probes /healthz + k8s readiness, needs 2 failures before restart to avoid flapping."
3. "Diag: kubectl logs/describe/events + ss/ip/tcpdump. I delete pod to let Deployment self-heal, annotate for audit."
4. "Infra: Terraform creates Kind cluster locally (same code shape as AWS/KVM/OpenStack), Ansible builds/loads/deploys."
5. "Security: Trivy in Jenkins blocks HIGH/CRITICAL, Kyverno enforces non-root + readOnlyFS + no :latest."
6. "Demo: touch /tmp/fail -> 500s -> healer deletes pod -> new pod Ready. Show `kubectl get events`."
7. If asked OpenShift: "Manifests use only core APIs + SecurityContext, portable to MicroShift/CRC/OpenShift."
8. If asked C/C++: walk through forwarder.c signal handling + how Python supervises it.
