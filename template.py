#!/usr/bin/env python

from __future__ import print_function
import sys
import json
import logging
from argparse import ArgumentParser
from util import get_url, post_and_wait

def show_templates():
    print("Available Templates:")
    result = get_url("template-programmer/template")
    print ('\n'.join(sorted([ '  {0}/{1}'.format(project['projectName'], project['name']) for project in result])))
    #for project in result:
    #    print( '{0}/{1}'.format(project['projectName'], project['name']))



def get_template_id(fqtn):
    parts = fqtn.split("/")
    projectName = parts[0]
    templateName = parts[1]
    print ('Looking for: {0}/{1}'.format(projectName, templateName))
    result = get_url("template-programmer/template")

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

def execute(id, reqparams, device, params, doForce):
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
    print ("payload", payload)
    return post_and_wait("template-programmer/template/deploy", payload)

if __name__ == "__main__":
    parser = ArgumentParser(description='Select options.')
    parser.add_argument('--template', type=str, required=False,
                        help="tempate name (project/template")
    parser.add_argument('--device', type=str, required=False,
                        help="deviceIp  e.g 1.1.1.1")
    parser.add_argument('--force', action="store_true", default = False,
                        help="force template to be appliec")
    parser.add_argument('--params', type=str, required=False,
                        help="'{\"param1\" :\"v1\"}'")

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
        template = get_url('template-programmer/template/{0}'.format(id))
        print("Showing Template Body:")
        print(template['templateContent'])
        params = ['"{0}":""'.format(p['parameterName']) for p in template['templateParams']]
        params = ",".join(params)
        params = '{' + params + '}'
        print("\nRequired Parameters for template body:",params)
        if args.device:
            response = execute(id, params, args.device, args.params, args.force)
            print ("\nResponse:")
            print (json.dumps(response, indent=2))
    else:
        show_templates()

