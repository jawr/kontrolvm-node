#!/bin/bash
pwd=$(pwd)
backup_dir=$pwd"/backups/"
date=$(date +%Y%m%d%H%M%S)
iptables-save -c > "$backup_dir/iptables.$date"
