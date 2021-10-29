
# Kuber

### Configuration

Kuber needs the following information from the application developer:

#### Data about the application

1. We need Kubernetes deployment files (.yamls) for deploying services and their dependencies.
   - place all the deployment files in /apps/app_name/deploy folder.
2. Load test that needs to be executed to test a combination
   - Copy existing load_test folder from /apps/sock-shop/load_test
   - update /apps/app_name/load_test/locustfile.py with required test scenario.
3. Initial configuration such as loading databases
   - Create a folder apps/app_name/load_test/init_scripts/
   - place the required code and invoke it with script run.sh

#### SSOT: Single Source Of Truth

Application developers have to configure VM types and services that need to be tested in file SSOT/config.json.
Example config.json file in SSOT folder:

``` json
{
  "Application": 
      {
          "name": "app_name",
          "services": ["service1", "service2"],
          "front-end": "service1",
          "port": "5000"
      },
  "Profiling":
      {
        "load_gen":
          {
           "time_limit":"2m",
           "concurrent":"100"
          }
      },
  "Infrastructure":
      {
        "Cloud_provider": "opennebula",
        "vm_types":[
                {
                  "name"          : "m4.large",
                  "cpu_count"     : "2",
                  "ram"           : "8",
                  "computer"      : "leibnitz",
                  "price"         : 0.10
                },
                {
                  "name"          : "m4.xlarge",
                  "cpu_count"     : "4",
                  "ram"           : "16",
                  "computer"      : "leibnitz",
                  "price"         : 0.20
                },
              ]
      }
}
```
Below we explain in detail each of the config options:
1. Application
   - name: Name of the application, should be same as the namespace given in Kubernetes deployment files, and folder name in /apps.
   - services: names of each microservice, should be the same as Kubernetes services in /apps/app_name/deploy.
   - front-end: service that receives external traffic into the application.
   - port: port exposed by front-end.
2. Profiling 
   - time_limit: the amount of time to run a load test.
   - concurrent: number of concurrent users that run the test.
3. VM types
   - Each entry in this list corresponds to a VM type
   - name: user-given name for the VM type
   - cpu_count: number of CPU cores
   - ram: RAM size in GB
   - computer: physical machine to place the VM type in.
   - price: cost per hour in $.
   
---
### Running the Kuber with Docker container
1. Download the docker container from the DockerHub repo and the code from Github.
2. Run the docker container with code using the following command:
```sh
docker run -it -v /code:/wd/code kuberload/kuber:latest /bin/bash
```
3. Then execute the Kuber inside the container:
```sh
cd /wd/code/kuber
python run.py
```
