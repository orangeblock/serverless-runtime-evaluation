import csv
import time
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# default openwhisk credentials from official docs
AUTH_USER = '23bc46b1-71f6-4ed5-8c54-816aa4f8c502'
AUTH_PASS = '123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
CONTAINER_LIFETIME = 605

def _csvdump(data, path, header=None):
  with open(path, 'ab') as f:
      writer = csv.writer(f)
      if header:
          writer.writerow(header)
      for line in data:
          writer.writerow(line)

def _exec_action(name, params=None):
  if params is None:
    params = {'blocking': 'true'}
  resp = requests.post(
    'https://172.18.0.3:31001/api/v1/namespaces/_/actions/%s' % name,
    params=params,
    auth=(AUTH_USER, AUTH_PASS),
    verify=False
  )
  return resp.json()

def _get_container_state(resp_json):
  for annotation in resp_json['annotations']:
    if annotation['key'] == 'initTime':
      return 'cold'
  return 'warm'

def _get_runtime(resp_json):
  for annotation in resp_json['annotations']:
    if annotation['key'] == 'kind':
      return annotation['value']
  return None

def _get_memory(resp_json):
  for annotation in resp_json['annotations']:
    if annotation['key'] == 'limits':
      return annotation['value']['memory']
  return None

def _run_raw_test(name, nruns, wait_seconds, export_type='stdout'):
  assert nruns > 0, "Invalid number of runs"
  for i in range(nruns):
    record = {
      'ts': int(time.time()),
      'execution': 'raw',
      'platform': 'openwhisk',
      'cstate': None,
      'language': None,
      'duration': None,
      'success': None,
      'reason': None,
      'memory': None
    }
    try:
      resp = _exec_action(name)
      record['duration'] = int(resp['duration'])
      record['cstate'] = _get_container_state(resp) 
      record['language'] = _get_runtime(resp)
      record['memory'] = _get_memory(resp)
      record['success'] = True
    except Exception as e:
      record['success'] = False
      record['reason'] = str(e)
    if export_type == 'stdout':
      print(record)
    elif export_type == 'csv':
      row = [
        record['ts'], record['cstate'], record['execution'], 
        record['duration'], record['memory'], record['language'], 
        record['platform'], int(record['success']), record.get('reason')
      ]
      _csvdump([row], 'out.csv')
    time.sleep(wait_seconds)


def run_cold_raw_test(name):
  # wait for container lifetime to ensure cold start on first invocation
  _exec_action(name)
  time.sleep(CONTAINER_LIFETIME)
  # execute tests every 10 minutes for a day
  print('Running raw cold start test for %s' % name)
  _run_raw_test(name, 144, CONTAINER_LIFETIME, 'csv')

def run_warm_raw_test(name):
  print('Running raw warm start test for %s' % name)
  for i in range(3):
    # prewarm runtime container
    for _ in range(3):
      _exec_action(name)
    print('Running batch %d' % i)
    # execute tests each minute for 2 hours
    _run_raw_test(name, 120, 60, 'csv')
    if i != 2:
      time.sleep(2*60*60)

# Examples
# run_warm_raw_test('py')
# run_cold_raw_test('py')
