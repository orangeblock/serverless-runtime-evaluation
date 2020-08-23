#!/bin/bash

function warm_run () {
  echo "Running request warm test for $1"
  for i in {1..3}
  do
    for j in {1..3}
    do
      curl -k http://localhost:1234/$1 &>/dev/null
    done
    echo "Running batch $i..."
    hey -n 120 -c 1 -q 0.016 -o csv -T "application/json" -m GET http://localhost:1234/$1 >> ~/out-$1.csv
    if [ $i -lt 3 ]
    then
      sleep 2h
    fi
  done
  echo "Done!"
}

function cold_run() {
  echo "Running request cold test for $1"
  for j in {1..3}
  do
    curl -k http://localhost:1234/$1 &>/dev/null
  done
  sleep 65s
  hey -n 144 -c 1 -q 0.0016 -o csv -T "application/json" -m GET http://localhost:1234/$1 >> ~/out-$1.csv
  echo "Done!"
}

# Examples
# warm_run py
# cold_run py
