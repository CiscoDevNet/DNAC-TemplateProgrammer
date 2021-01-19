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

## Bulk application - Variable Lists
Sometimes it is necessary to supply series of values for a set of predefined variables in Jinja2 a template.
We can have a '.csv' or a '.json' formatted source file that we can have the template iterate over for each of those variables.

Sample 'paramsfile.csv':

```buildoutcfg
SITE_CODE,DESCRIPTION
CAN01,CDN_SITE_01
CAN02,CDN_SITE_02
CAN03,CDN_SITE_03
```

And Jinja2 Template hosted on DNAC (you will find it in 'work_files' dir in .json format which you can import int DNAC, 'WLC9800-DayN-Provisioning' project for purposes of this example):

```buildconfig
{% SET SITE_CODE_LIST = SITE_CODE %}
{% SET DESCRIPTION_LIST = DESCRIPTION %}

{% FOR ITEM in SITE_CODE_LIST %}
{% SET SITE = SITE_CODE_LIST[loop.index-1] %}
{% SET DESCRIPTION = DESCRIPTION_LIST[loop.index-1] %}

wireless profile flex FP_{{SITE}}
 acl-policy CAPTIVE_PORTAL_REDIRECT
  central-webauth
 no arp-caching
 no local-auth ap radius
 native-vlan-id 2
 vlan-name data
  acl Flex_Profile_Allow_All
  vlan-id 10
 vlan-name byod
  acl Flex_Profile_Allow_All
  vlan-id 20
 vlan-name guest
  acl Flex_Profile_Allow_All
  vlan-id 30

wireless tag site ST_{{SITE}}
 ap-profile MyApProfile
 description {{DESCRIPTION}}
 no local-site
 flex-profile FP_{{SITE}}
{% ENDFOR %}
```

J2 template above accepts two lists of variables, and creates a nested set of configlets for each row of values in the supplied '.csv' or '.json' paramsfile

```buildconfig
./template.py --template WLC9800-DayN-Provisioning/Guest-Wireless-Tag-Profile --device 10.85.54.99 --preview --force --paramsfile 'work_files/paramsfile.csv'
```

or

```buildconfig
./template.py --template WLC9800-DayN-Provisioning/Guest-Wireless-Tag-Profile --device 10.85.54.99 --preview --force --paramsfile 'work_files/paramsfile.json'
```

with output

```buildconfig
...
{% SET SITE_CODE_LIST = SITE_CODE %}
{% SET DESCRIPTION_LIST = DESCRIPTION %}

{% FOR ITEM in SITE_CODE_LIST %}
{% SET SITE = SITE_CODE_LIST[loop.index-1] %}
{% SET DESCRIPTION = DESCRIPTION_LIST[loop.index-1] %}

wireless profile flex FP_{{SITE}}
 acl-policy CAPTIVE_PORTAL_REDIRECT
  central-webauth
 no arp-caching
 no local-auth ap radius
 native-vlan-id 2
 vlan-name data
  acl Flex_Profile_Allow_All
  vlan-id 10
 vlan-name byod
  acl Flex_Profile_Allow_All
  vlan-id 20
 vlan-name guest
  acl Flex_Profile_Allow_All
  vlan-id 30

wireless tag site ST_{{SITE}}
 ap-profile MyApProfile
 description {{DESCRIPTION}}
 no local-site
 flex-profile FP_{{SITE}}
{% ENDFOR %}

Required Parameters for template body: {"SITE_CODE":"","SITE":"","DESCRIPTION":""}

Bindings []
Previewing template


wireless profile flex FP_CAN01
 acl-policy CAPTIVE_PORTAL_REDIRECT
  central-webauth
 no arp-caching
 no local-auth ap radius
 native-vlan-id 2
 vlan-name data
  acl Flex_Profile_Allow_All
  vlan-id 10
 vlan-name byod
  acl Flex_Profile_Allow_All
  vlan-id 20
 vlan-name guest
  acl Flex_Profile_Allow_All
  vlan-id 30

wireless tag site ST_CAN01
 ap-profile MyApProfile
 description CDN_SITE_01
 no local-site
 flex-profile FP_CAN01

wireless profile flex FP_CAN02
 acl-policy CAPTIVE_PORTAL_REDIRECT
  central-webauth
 no arp-caching
 no local-auth ap radius
 native-vlan-id 2
 vlan-name data
  acl Flex_Profile_Allow_All
  vlan-id 10
 vlan-name byod
  acl Flex_Profile_Allow_All
  vlan-id 20
 vlan-name guest
  acl Flex_Profile_Allow_All
  vlan-id 30

wireless tag site ST_CAN02
 ap-profile MyApProfile
 description CDN_SITE_02
 no local-site
 flex-profile FP_CAN02

wireless profile flex FP_CAN03
 acl-policy CAPTIVE_PORTAL_REDIRECT
  central-webauth
 no arp-caching
 no local-auth ap radius
 native-vlan-id 2
 vlan-name data
  acl Flex_Profile_Allow_All
  vlan-id 10
 vlan-name byod
  acl Flex_Profile_Allow_All
  vlan-id 20
 vlan-name guest
  acl Flex_Profile_Allow_All
  vlan-id 30

wireless tag site ST_CAN03
 ap-profile MyApProfile
 description CDN_SITE_03
 no local-site
 flex-profile FP_CAN03


Executing template on:10.85.54.99, with Params:{"SITE_CODE": ["CAN01", "CAN02", "CAN03"], "DESCRIPTION": ["CDN_SITE_01", "CDN_SITE_02", "CDN_SITE_03"]}
...
Response:
{
  "deploymentId": "458e81b1-7095-402b-b8cb-735119543e2c",
  "templateName": "Guest-Wireless-Tag-Profile",
  "templateVersion": "2",
  "projectName": "WLC9800-DayN-Provisioning",
  "status": "SUCCESS",
  "startTime": "22:44:01 19/01/2021",
  "endTime": "22:44:38 19/01/2021",
  "duration": "0 minutes 36 seconds",
  "devices": [
    {
      "deviceId": "b57b4ca1-4b7c-4e07-bafc-f60b4b6d163d",
      "name": "",
      "status": "SUCCESS",
      "detailedStatusMessage": "Provisioning success for template Guest-Wireless-Tag-Profile",
      "startTime": "22:44:01 19/01/2021",
      "endTime": "22:44:38 19/01/2021",
      "ipAddress": "b57b4ca1-4b7c-4e07-bafc-f60b4b6d163d",
      "identifier": "b57b4ca1-4b7c-4e07-bafc-f60b4b6d163d",
      "targetType": "MANAGED_DEVICE_IP",
      "duration": "0 minutes 36 seconds"
    }
  ]
}
```
