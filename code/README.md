
# Kuber

### Contents

- [Installation](#Installation)
- [Configuration](#system-component)
- [Experiments](#system-dataflow)
- [Application format](#system-component)
- [Kuber](#how-to-start)
- [Results](#installation)

## Installation

Store OpenNebula password, username, and userid at enviroment variables USERNAME, PASSWORD, USERID

## system-component 

![dataflow](https://raw.githubusercontent.com/resess/athena_paper/master/kali_code/img/dataflow.jpg?token=AGLP5QT3LY4FZHKDYZCYCPS5IYETI)

The system consists of two main modules: *Spearmint and SDK*. </br>
<b>Spearmint</b> is responsible for using Bayesian optimization to calculate the next configuration when given an input(last configuration's cost). </br>
<b>SDK</b> Refer to the configuration file for virtual machine creation and micro service deployment.

## system-dataflow
1.Each loop the Spearmint will execute the main function in SDK/start.py and send the new configuration to get the cost.<br>

```
	BO -> main(job_id, params)
``` 

2.The SDK gets the configuration then it refers to the config file in SDK/conf to verify the configuration is validate or not.  <br>
e.g. the input: cpu_count = 1,disk =10,ram=4 is a invalid type 

```json
{
  "vms":[
    {
      "name"          : "r5.large",
      "cpu_count"     : "2",
      "disk"          : "10",
      "ram"           : "16",
      "computer"      : "newton",
      "price"         : 0.126
    },
    {
      "name"          : "r5.xlarge",
      "cpu_count"     : "4",
      "disk"          : "10",
      "ram"           : "32",
      "computer"      : "newton",
      "price"         : 0.252
    }
  ]
}
```

3.Then the SDK uses **deploy Method** Module to create the correspond VM and deploy the microservice which has already been described in the configuration file. 

```json
{ 
    "deploy":{
        "method":"ECEnew",
        "task":"flaskDemo"
    }
}
```

4.Finally, it uses the **cost detection** module to send a certain number of concurrent request to the API which written in the config file and get the response time. If the response time is under 5s(example), it will send the configuration's cost back to BO.<br>

```
{
  "apis": [
    {
        "url": ":5000/hello",
        "method": "GET",
        "parameter":[],
        "weight": 1
    },
    {
        "url": ":5000/compute",
        "method": "GET",
        "parameter":[],
        "weight": 1
    }
   ]
}
```
Then the system will start a loop to caculate the new configration until find the best configuration.


## how-to-start

Just run the start.sh on leibnitz newton or other machine.<br>
notes: you can uncomment those comments to install dependencies

```bash
#!/usr/bin/env bash
#pip install protobuf==2.6.1
#pip install wave
#sudo apt-get install python-protobuf
#pip install --user cryptography --upgrade
#sudo python -m easy_install --upgrade pyOpenSSL
python2.7 spearmint/main.py --driver=local --method=GPEIOptChooser --method-args=noiseless=1 SDK/sdk.pb

```

notes: After finish the experiment, you are supposed to run the **cleanup.sh** to clean all the out file.

## testing

now we can use the system to find the best configuration for the flaskDemo task in six types of VMs. 
