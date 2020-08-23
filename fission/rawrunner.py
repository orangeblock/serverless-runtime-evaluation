import csv
import time
import requests
import subprocess
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from collections import defaultdict

COLD_START_TIMEOUT = 600
TRANSFER_TIMEOUT = 65

def _csvdump(data, path, header=None):
    with open(path, 'ab') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        for line in data:
            writer.writerow(line)

def _get_container_state(fname, ts_start, ts_end):
    # query prometheus for number of cold start invocations
    resp = requests.get(
        'http://localhost:9090/api/v1/query_range',
        params={
            'query': 'fission_cold_starts_total{funcname="%s"}' % fname,
            'start': str(ts_start), 'end': str(ts_end), 'step': '30'
        }
    )
    # find if we had a new cold start in this timeframe
    vals = resp.json()['data']['result'][0]['values']
    uniq = set()
    for _, val in vals:
      uniq.add(val)
    assert len(uniq) == 2 or len(uniq) == 1, "Invalid container state: %s" % vals
    if len(uniq) == 2:
        return 'cold'
    return 'warm'

def _get_duration(fname, ts_start, ts_end):
    # query prometheus for total function execution duration in specified timeframe
    resp = requests.get(
        'http://localhost:9090/api/v1/query_range', 
        params={
            'query': 'fission_function_duration_seconds_sum{name="%s", code="200"}' % fname,
            'start': str(ts_start), 'end': str(ts_end), 'step': '30'
        }
    )
    # calculate difference to get the duration of single invocation
    vals = resp.json()['data']['result'][0]['values']
    uniq = set()
    for _, val in vals:
      uniq.add(val)
    uniq = sorted(uniq)
    # make sure that only one invocation occurred
    assert len(uniq) == 2, "Invalid number of executions: %s" % vals
    duration = float(uniq[1]) - float(uniq[0])
    return duration

def _exec_action(name, full=True):
    record = defaultdict(lambda: None)
    ts_start = int(time.time())
    subprocess.check_output("fission fn test --name %s" % name, shell=True)
    if not full:
        return (None, None)
    # wait until metrics have been transferred to prometheus
    time.sleep(TRANSFER_TIMEOUT)
    ts_end = int(time.time())
    cstate = _get_container_state(name, ts_start, ts_end)
    duration = _get_duration(name, ts_start, ts_end)
    return (cstate, duration)

def _run_raw_test(name, nruns, wait_seconds, export_type='stdout'):
    assert nruns > 0, "Invalid number of runs"
    wait_seconds -= TRANSFER_TIMEOUT
    wait_seconds = 0 if wait_seconds < 0 else wait_seconds
    for i in range(nruns):
        record = {
          'ts': int(time.time()),
          'execution': 'raw',
          'platform': 'fission',
          'cstate': None,
          'language': None,
          'duration': None,
          'success': None,
          'reason': None
        }
        try:
            cstate, duration = _exec_action(name)
            record['duration'] = duration
            record['cstate'] = cstate
            record['language'] = name
            record['success'] = True
        except Exception as e:
            record['success'] = False
            record['reason'] = str(e)
        if export_type == 'stdout':
            print(record)
        elif export_type == 'csv':
            row = [
                record['ts'], record['cstate'], record['execution'], record['duration'],
                record['language'], record['platform'], int(record['success']), record.get('reason')
            ]
            _csvdump([row], 'out.csv')
        time.sleep(wait_seconds)

def run_cold_raw_test(name):
    print('Running raw cold start test for %s' % name)
    _exec_action(name, full=False)
    time.sleep(COLD_START_TIMEOUT)
    _run_raw_test(name, 144, COLD_START_TIMEOUT, 'csv')

def run_warm_raw_test(name):
    print('Running raw warm start test for %s' % name)
    for i in range(3):
        # prewarm runtime container
        for _ in range(3):
            _exec_action(name, full=False)
        print('Running batch %d' % i)
        _run_raw_test(name, 120, 60, 'csv')
        if i != 2:
            time.sleep(2*60*60)

# Examples
# run_warm_raw_test("py")
# run_cold_raw_test("py")
