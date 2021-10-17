#!/usr/bin/env bash

host=$1
port=$2
concurrent=$3
limit_time=$4
thoughput=$5

echo "start the command host: $thost concurrent:$concurrent"

CRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"

echo $CRIPTPATH

$CRIPTPATH/runLocust.sh -h $host:$port -c $concurrent -t $limit_time
