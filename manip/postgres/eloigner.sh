#!/bin/bash
# Retarde chaque paquet qui sort de cette machine vers le réseau interne.
#   eloigner.sh 20ms     B répond avec 20 ms de retard
#   eloigner.sh 0ms      plus de retard
set -e
retard="${1:-20ms}"
for iface in $(ls /sys/class/net | grep -E '^eth'); do
  tc qdisc del dev "$iface" root 2>/dev/null || true
  if [ "$retard" != "0ms" ] && [ "$retard" != "0" ]; then
    tc qdisc add dev "$iface" root netem delay "$retard"
  fi
done
echo "Retard sortant : $retard"
