#!/bin/bash

writer_info=$(echo "$@" | grep -o "\[[^]]*(.*)[^[]*\]")
if [ "${writer_info}"x == ""x ]; then
    exit 1
fi
writer_bracket=$(echo "${writer_info}" | grep -o "(.*)")
if [ "${writer_bracket}"x != ""x ]; then
writer=$(echo "${writer_bracket}" | sed 's/[()]//g')
fi
penciller=$(echo "${writer_info}" | sed "s/${writer_bracket}//g" | tr -d '\[\]' | awk '$1=$1')
if [ "${writer}"x == ""x ]; then
    echo "${penciller}"
else
    echo "${writer}"
fi
echo "${penciller}"
