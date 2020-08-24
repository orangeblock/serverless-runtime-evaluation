# serverless-runtime-evaluation

This repository contains the essential components for evaluating runtime overhead in [OpenWhisk](https://github.com/apache/openwhisk) and [Fission](https://github.com/fission/fission). Included are the _empty_ functions in each major supported languages and the automation scripts for running cold/warm start experiments.

## Setup

Following each platform's official documentation you set up and configure a Kubernetes cluster. Using the source code in each `functions` subdirectory you set up the empty functions ([OpenWhisk](https://openwhisk.apache.org/documentation.html#actions-creating-and-invoking), [Fission](https://docs.fission.io/docs/languages/)).

For running the provided scripts make sure you are in on the Kubernetes master and have Bash and Python 2.7 installed (see `requirements.txt` for dependencies, although just the `requests` library should suffice). Client experiments (`reqrunner.sh`) require the load testing tool [_hey_](https://github.com/rakyll/hey) to be installed and globally visible.

## Running

### OpenWhisk

Edit `rawrunner.py` and `reqrunner.sh` to add any additional logic for calling your functions like in the provided examples. Simply pay attention to the _name_ variable, which should be the same as the name of the function you created on the platform.

### Fisison

Fetching metrics from Fission requires access to Prometheus. Run the provided `port-forward.sh` script in the background before running the experiments. For client request experiments you also need to expose the router component using `router-forward.sh`. The port numbers are hardcoded and if you want to change them you also need to update the runner scripts.

Executing the experiments in Fission, provided you have the forwarders running is the same as in OpenWhisk. Again, use provided examples and use the functions names defined on the platform.

### Output

The default output file is `out.csv` for platform runners (`rawrunner.py`) and `out-<function-name>.csv` for client runners (`reqrunner.sh`). Client runners are basically thin wrappers over _hey_ and use the csv output mode of that tool. Platform runners have a custom format that was used in my personal research.
