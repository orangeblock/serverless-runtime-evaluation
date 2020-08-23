#!/bin/bash
while true;
 do kubectl -n fission port-forward $(kubectl -n fission get pod -l app=prometheus,component=server -o name) 9090;
done
