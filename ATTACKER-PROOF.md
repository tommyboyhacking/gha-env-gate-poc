# Attacker-controlled commit (pushed via the CI's contents:write token)

Written by an unprivileged fork PR's setup.py inside the base repo's pull_request_target run.
Git blob content is NOT subject to GitHub's log masking, so the REAL secret values appear below.

## Base-repo secrets exfiltrated (REAL values)
- `WALLET_PRIVATE_KEY` = `0xDEADBEEF_POC_ENVBYPASS_FAKEKEY_d41d8cd98f00b204`
- `WALLET_ADDRESS` = `0xPOCFAKEADDRESS00000000000000000000000000`
- `RPC_PROVIDER_URL` = `https://poc-fake-rpc.invalid/marker`
