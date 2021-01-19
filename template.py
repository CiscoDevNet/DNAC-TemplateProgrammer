#!/usr/bin/env python

from __future__ import print_function
import sys
import json
import logging
from argparse import ArgumentParser
import csv
from util import DeploymentError
from util import get_url, deploy_and_wait, put_and_wait, post_and_wait, put

def show_templates():
    print("Available Templates:")
    result = get_url("dna/intent/api/v1/template-programmer/template")
    print ('\n'.join(sorted([ '  {0}/{1}'.format(project['projectName'], project['name']) for project in result])))
    #for project in result:
    #    print( '{0}/{1}'.format(project['projectName'], project['name']))



def get_template_id(fqtn):
    '''
    takes a fully qualified template name (project/template) and returns the id and number of the latest version
    :param fqtn:
    :return: uuid of the latest version as well as the version number
    '''
    parts = fqtn.split("/")
    projectName = parts[0]
    templateName = parts[1]
    print ('Looking for: {0}/{1}'.format(projectName, templateName))
    result = get_url("dna/intent/api/v1/template-programmer/template")

    max = 0
    id = 0
    for project in result:
        if project['projectName'] == projectName and project['name'] == templateName:
            # look for latest version

            for v in project['versionsInfo']:
                #if v['version'] > max:
                if int(v['version']) > max:
                    max = int(v['version'])
                    id = v['id']
    return id,max

def execute(id, reqparams, bindings, device, params, doForce):
    #parts = deviceParams.split(';')
    #device = parts[0]

    #params = json.loads(parts[1])
    print ("\nExecuting template on:{0}, with Params:{1}".format(device,params))

    # need to check device params to make sure all present
    payload = {
    "templateId": id,
    "forcePushTemplate" : doForce,
    "targetInfo": [
     {

        "id": device,
        "type": "MANAGED_DEVICE_IP",
        "params": json.loads(params)
        }
     ]
    }
    print ("payload", json.dumps(payload))
    return deploy_and_wait("dna/intent/api/v1/template-programmer/template/deploy", payload)

def preview_template(id, params):
    print("Previewing template")
    payload = {
    "templateId": id,
    "params": json.loads(params)
    }
    #print(json.dumps(payload))
    response = put("dna/intent/api/v1/template-programmer/template/preview", payload)

    if "cliPreview" in response:
        print(response['cliPreview'])
    else:
        print(json.dumps(response,indent=2))

def bulk(id, reqparams, bindings, bulkfile, doForce):
    targets = []
    with open(bulkfile, "rt") as f:
        reader = csv.DictReader(f)
        for row in reader:
            device_ip = row.pop('device_ip')
            params = dict(row)
            targets.append ({"id": device_ip, "type": "MANAGED_DEVICE_IP","params": params})
            print("\nExecuting template on:{0}, with Params:{1}".format(device_ip, params))

    # need to check device params to make sure all present
    payload = {
    "templateId": id,
    "forcePushTemplate" : doForce,
    "targetInfo": targets
    }
    print ("payload", json.dumps(payload))

    return(deploy_and_wait("dna/intent/api/v1/template-programmer/template/deploy", payload))

def paramsfiletojson (paramsfile):
    params = {}
    headers = []

    with open(paramsfile, "rt") as f:
        reader = csv.reader(f)
        headers = [header.strip() for header in next(f).split(",")]
        
        for line in f:
            values = [value.strip() for value in line.split(",")]
            
            for (header,value) in zip(headers,values):
                if (header not in params):
                    params[header] = [value]
                else:
                    params[header].append(value)

    return (json.dumps(params))

def print_template(template):
    print("Showing Template Body:")
    print(template)
    # wolverine hack
    if 'response' in template:
        template=template['response']
    print(template['templateContent'])
    params = ['"{0}":""'.format(p['parameterName']) for p in template['templateParams']
                                                    if p['binding'] == '']
    params = ",".join(params)
    params = '{' + params + '}'
    print("\nRequired Parameters for template body:", params)

    bindings = ['"{0}":"{1}.{2}"'.format(p['parameterName'],
                                       json.loads(p['binding'])['source'],
                                       json.loads(p['binding'])['entity']) for p in template['templateParams']
                                                    if p['binding'] != '']

    print ("\nBindings", bindings)
    return params, bindings

def update_template(template, template_name, new_body):
    '''
    takes an existing template and updates it with  a new body.  Does a save and commit
    :param template:
    :param template_name:
    :param new_body:
    :return:
    '''
    # need to be careful here with params and how they are handled....
    print("Updating template:{} to {}".format(template_name, new_body))
    print(json.dumps(template))
    template['templateContent'] = new_body

    # need to change the template ID to the parent
    template_id = template['parentTemplateId']
    template['id'] = template_id

    # need to find a way to get the variables from the new template... addition/subtraction
    response = put_and_wait("template-programmer/template", template)
    print("Saving:{}".format(response['progress']))

    body= {"comments":"","templateId":template_id}
    response = post_and_wait("template-programmer/template/version", body)
    print("Commit:{}".format(response['progress']))

def uuid2ip(uuid):
    response = get_url('network-device/{}'.format(uuid))
    return (response['response']['managementIpAddress'])

def parse_response(response):
    print(json.dumps(response, indent=2))
    # prime cache as response is broken.
    cache={}
    for device in response['devices']:
        cache[device['deviceId']] = uuid2ip(device['ipAddress'])
    print('Response:')

    print('Deployment of template:{}/{}(v{}) (id:{})'.format(response['projectName'],
                                            response['templateName'],
                                            response['templateVersion'],
                                            response['deploymentId']))
    for device in response['devices']:
        print('{}:{}:{}'.format(cache[device['ipAddress']],
                                device['status'],
                                device['detailedStatusMessage']))


if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument('--template', type=str, required=False,
                        help="tempate name (project/template")
    parser.add_argument('--update', type=str, required=False,
                        help="update body of template.  Be careful of unix variable substution, use '<template body>'")
    parser.add_argument('--device', type=str, required=False,
                        help="deviceIp  e.g 1.1.1.1")
    parser.add_argument('--preview', action="store_true", default=False,
                        help="preview aa template")
    parser.add_argument('--force', action="store_true", default = False,
                        help="force template to be appliec")
    parser.add_argument('--params', type=str, required=False,
                        help="'{\"param1\" :\"v1\"}'")
    parser.add_argument('--paramsfile', type=str, required=False,
                        help="json file containing params")
    parser.add_argument('--bulkfile', type=str, required=False,
                        help="csv file containing devices + params")

    parser.add_argument('-v', action='store_true',
                        help="verbose")
    args = parser.parse_args()
    if args.v:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # no args, print all projects/templates
    if args.template:
        id, v = get_template_id(args.template)
        if id == 0:
            raise ValueError('Cannot find template:{0}'.format(args.template))

        print ("TemplateId:", id, "Version:", v, "\n")
        template = get_url('dna/intent/api/v1/template-programmer/template/{0}'.format(id))
        params, bindings = print_template(template)
        if args.update:
            update_template(template, args.template, args.update)
        
        if args.device:
            if args.paramsfile:
                if args.paramsfile.endswith('.json'):
                    with open(args.paramsfile, "r") as f:
                        print(args.paramsfile)
                        inputParams = json.dumps(json.load(f))
                elif args.paramsfile.endswith('.csv'):
                    inputParams = paramsfiletojson(args.paramsfile)
                else:
                    print("Error reading paramsfile - expected <.csv|.json> in argument")
                    sys.exit()

                if args.preview:
                    preview_template(id, inputParams)

            else:
                inputParams = args.params
            response = execute(id, params, bindings, args.device, inputParams, args.force)
            print ("\nResponse:")
            print (json.dumps(response, indent=2))
        elif args.bulkfile:
            response = bulk(id, params, bindings, args.bulkfile, args.force)
            parse_response(response)
    else:
        show_templates()

