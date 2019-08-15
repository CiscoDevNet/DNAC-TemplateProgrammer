# Template Programmer
These scripts demonstrate the template programmer API on Cisco DNA Center.
The scripts assume the templates have been setup on Cisco DNA center in advance.

The scripts are educational to illustrate the payload and API calls.

## Running the script
The script needs a DNAC to communicate to via a config file (dnac_config.py) or environmnent variables - 
(DNAC, DNAC_USER, DNAC_PASSWORD).

## get a list of templates
Run the script without argumnents to get a list of templates.

```buildoutcfg
$ ./template.py 
Available Templates:
https://10.66.104.121:443/api/v1/template-programmer/template
  Adam/int-vlan
  Adam/interface-des
  DB/prefix
  Onboarding Configuration/9300
  Onboarding Configuration/advanced
  Onboarding Configuration/basic

```

## look at body of a template
To find out the parameters and other attributes of a template, run the script with the --template option
The script automatically gets the latest version of the template.
It shows you the paramaters required ("vlan" and "interface")
```buildoutcfg
$ ./template.py --template Adam/int-vlan
Looking for: Adam/int-vlan
https://10.66.104.121:443/api/v1/template-programmer/template
TemplateId: 78742a98-7a8b-435a-a2f8-284a1f940df0 Version: 9 

https://10.66.104.121:443/api/v1/template-programmer/template/78742a98-7a8b-435a-a2f8-284a1f940df0
Showing Template Body:
interface $interface
  switchport access vlan $vlan
    

Required Parameters for template body: {"vlan":"","interface":""}
```
## apply a template
Then use the --device and --params options to apply a template to a device.  
This output is quite verbose as the API calls are shown in detail.

```buildoutcfg
$ ./template.py --template Adam/int-vlan --device 10.10.14.4 --params '{"vlan":"20","interface":"gig1/0/22"}' 
Looking for: Adam/int-vlan
https://10.66.104.121:443/api/v1/template-programmer/template
TemplateId: 78742a98-7a8b-435a-a2f8-284a1f940df0 Version: 9
<SNIP>

```
## force a template to be "reapplied"
If a template is re-applied with the same parameters, then an error is returned as DNAC will not reapply the same template 
by default.

to force the template to be reapplied, use the --force option

```buildoutcfg
$ ./template.py --template Adam/int-vlan --device 10.10.14.4 --params '{"vlan":"20","interface":"gig1/0/22"}' --force
Looking for: Adam/int-vlan
https://10.66.104.121:443/api/v1/template-programmer/template
TemplateId: 78742a98-7a8b-435a-a2f8-284a1f940df0 Version: 9
<SNIP>
```

## Bulk application
I also started to work on the bulk application of a template to a set of devices.
Use the --bulkfile option.  This is a csv file with a list of device_ip and variables for the given template

The following is an exmaple where the template has two varaibles, "do" and "ip".  "device_ip" is fixed and the ip addreess of the target
```buildoutcfg
device_ip,do,ip
10.10.15.100,1,10.10.10.250
10.10.50.2,1,10.10.10.251
```

```buildoutcfg
 ./template.py --template adam/simple --bulkfile work_files/test.csv
Looking for: adam/simple
https://10.66.104.121:443/dna/intent/api/v1/template-programmer/template
TemplateId: d26cc12d-27f3-4fd2-97cd-63f32b85e889 Version: 2 
<snip>

Response:
Deployment of template:adam/simple(v2) (id:e7301391-cc86-47ae-942d-ee625dde15ea)
10.10.50.2:SUCCESS:Provisioning success for template simple
10.10.15.100:SUCCESS:Provisioning success for template simple
```