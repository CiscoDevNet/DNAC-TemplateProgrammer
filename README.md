# Template Programmer
These scripts demonstrate the template programmer API on Cisco DNA Center.
The scripts assume the templates have been setup on Cisco DNA center in advance.

## Running the script
The script needs a DNAC to communicate to via a config file (dnac_config.py) or environmnent variables.

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
