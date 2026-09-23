#!/usr/bin/env bash
# Some Codespaces images ship both nft and legacy iptables with conflicting rules.
# The kernel enforces the legacy tables, whose FORWARD policy is DROP - which
# silently drops NEW container-to-container connections while letting established
# ones through. Symptom: frontend -> backend hangs ~30s, then ConnectTimeout.
sudo iptables-legacy -P FORWARD ACCEPT 2>/dev/null || true
echo -n "legacy FORWARD policy is now: "
sudo iptables-legacy -L FORWARD -n 2>/dev/null | head -1
