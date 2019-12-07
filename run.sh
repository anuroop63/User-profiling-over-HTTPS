#!/bin/bash
pkill firefox
pkill tcpdump
MOZ_DISABLE_AUTO_SAFE_MODE=1

expName=$(date +"%Y%m%d%H%M%S")

COUNTER=0
while IFS= read -r line; do
    for i in {1}; do
        echo $line
        name=$(date +"%Y%m%d%H%M%S")
        rm -rf ~/.cache/mozilla/firefox/*
        rm -rf ~/.mozilla/firefox/*
        echo $name","$line >> report.txt
        sudo echo $line,$(dig +short $(echo ${line#*//} | sed 's/\/.*//' | cut -f1 -d":") | tail -n1) >> ips.txt
        sudo echo $line,$(dig +short $(echo www.${line#*//} | sed 's/\/.*//' | cut -f1 -d":") | tail -n1) >> ips.txt
        sudo /usr/sbin/tcpdump -s 65535 -w ./results/$name.pcap  &
        firefox  -private $line &
        sleep 10
        sudo pkill firefox
        sudo pkill tcpdump
    done
done < "listSort.csv"
