from __future__ import print_function

import os
import sys
import requests
import json
import time
import re

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

class DeploymentTimeoutError(Exception):
    pass

class DeploymentError(Exception):
    pass


from dnac import get_auth_token, create_url, wait_on_task

def get_url(url):

    url = create_url(path=url)
    print(url)
    token = get_auth_token()
    headers = {'X-auth-token' : token['token']}
    try:
        response = requests.get(url, headers=headers, verify=False)
    except requests.exceptions.RequestException as cerror:
        print("Error processing request", cerror)
        sys.exit(1)

    return response.json()

def post_and_wait(url, data):

    token = get_auth_token()
    url = create_url(path=url)
    print(url)
    headers= { 'x-auth-token': token['token'], 'content-type' : 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException  as cerror:
        print ("Error processing request", cerror)
        sys.exit(1)
    print ("Response", response.json())

    # this has changed in 1.2 ##
    deploymentId = response.json()['deploymentId'].split(":")[-1].strip()

    # look for the already deployed issue
    if "already deployed" in deploymentId:
        print("Error:", deploymentId)
        sys.exit(1)
    applicable = response.json()['deploymentId'].split(":")[1].strip()

    # look for device type issues
    if 'nonApp' in applicable:
        print("Error: {}".format(response.json()['deploymentId']))
        sys.exit(1)

    print ("waiting for deploymentId", deploymentId)

    start_time = time.time()
    retry_interval = 2
    timeout = 10 * retry_interval

    while True:
        # changed in 1.2
        response = get_url('template-programmer/template/deploy/status/' + deploymentId)
        print (response)
        if response["endTime"] != '':
            break
        else:
            if timeout and (start_time + timeout < time.time()):
                raise DeploymentTimeoutError("Task %s did not complete within the specified timeout "
                                       "(%s seconds)" % (task_id, timeout))

            print("Task=%s has not completed yet. Sleeping %s seconds..." % (deploymentId, retry_interval))
            time.sleep(retry_interval)

    if response["status"] != "SUCCESS":
        raise DeploymentError("Task %s had status: %s" % (deploymentId, response['status']))

    #print (response)

    return response
