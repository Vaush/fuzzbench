#!/bin/bash
used=`df -k --output=used "/dev/sda2" | tail -n1`
max=-1
while true
do
	used2=`df -k --output=used "/dev/sda2" | tail -n1`
	diff=$((used2-used))
	if [[ $diff -gt $max ]]; then
		max=$diff
		echo "New max: "$diff
	fi;
done
