#!/bin/bash

title=$(echo "$@" | sed 's!([^)]*)!!g' | sed 's!\[[^]]*\]!!g' | awk '$1=$1')
if [ "${title}"x == ""x ]; then
    exit 1
fi

echo "${title}"
