#!/bin/bash
set -e


echo "[*] Starting socat on port 5000 -> afc_list"

# socat forks afc_list for each connection as user ctf
exec socat TCP-LISTEN:5000,reuseaddr,fork EXEC:/app/afc_list,su=ctf
