#!/bin/bash
while true;
  do kubectl -n fission port-forward $(kubectl -n fission get pod -l svc=router -o name) 1234:8888;
done
