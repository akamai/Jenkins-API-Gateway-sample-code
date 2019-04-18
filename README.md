# API Gateway CI Toolkit

The *API Gateway CI Toolkit* contains a series of sample scripts which can be used to quickly implement an API Governance CI process for the [Akamai API Gateway](https://www.akamai.com/us/en/products/web-performance/api-gateway.jsp). API developers can use the *API Gateway CI Toolkit* to reconcile changes to API specification (using Swagger or RAML) with their Akamai API Gateway definition.
Such a CI process eliminates much of the administration overhead associated with the management of your Akamai API Gateway configuration state, allowing developers to focus on core services development.

The scripts contained in this project perform the following functions within a simple CI process:

1. Create a new version of an existing Akamai API Gateway configuration. Sanity checking logic is built in to understand the activation state of the target API gateway property version (updating if not activated, creating a new version if activated)
2. Update the Akamai API Gateway configuration using either a RAML or Swagger API definition artifact. This step also performs a high level comparison of the exiting API Gateway resource state and the new API definition.
3. Activate a new Akamai API Gateway configuration on either PRODUCTION or STAGING networks.

The above three steps can be orchestrated by some process workflow framework (Jenkins, Bamboo, Rundeck, etc) and triggered by some external event (such as a VCS event like commit or push) to automate the process of reconciling API definition updates with the Akamai API Gateway configuration state.

### Prerequisites

The *API Gateway CI Toolkit* requires the following to be in place prior to initial use:

1. An Akamai API client with 'API Definition' READ-WRITE authorizations https://developer.akamai.com/api/getting-started.
2. An existing API Gateway property created, keeping note of the name of the Gateway Instance (found in Luna Control Center, in the API Gateway configuration section).

## Installation

All package dependencies are maintained in the requirements.txt file. Use pip to install:

```
pip install -r requirements.txt
```

### Runtime Environment

Each script was developed and tested using a python 3 (3.6.2) interpeter.

It should also be noted that the scripts assume the runtime environment will be a Linux/Unix OS. Some scripts expect Linux specific directory structures.

## Script Execution

All scripts must be invoked using the python3 interpreter directly.

**Example**

```
python3 <script> <arguments>
```

The arguments supported by each script will be defined below, and can be identified by calling the script with a '--help' or no argument:

```
python3 activateApiVersion.py --help

usage: activateApiVersion.py [-h] [--config CONFIG] [--section SECTION]
                             [--version VERSION] [--name NAME [NAME ...]]
                             [--network NETWORK] [--email EMAIL]

API GW CI demo toolkit -> activateApiVersion.py

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Full or relative path to .edgerc file
                        (default: $HOME/.edgerc)
  --section SECTION     The section of the edgerc file with the proper {OPEN} API credentials.
                        (default: default)

required arguments:
  --version VERSION     The version of the API Gateway definition, which will be compared with the new external API definition.
                        (default: latest)
  --name NAME [NAME ...]
                        The Gateway property name for the target API Gateway.
                        (default: None)
  --network NETWORK     The target network to activate the version of the Akamai API Gateway on (PRODUCTION or STAGING)
                        (default: staging)
  --email EMAIL         A comma-seperated list of e-mails for which activation statuses will be sent.
                        (default: None)
```

While all scripts expect a series of required arguments (listed below), each script can support the following optional arguments:

- '--config': The absolute or relative path of the .edgerc file containing the Akamai API credentials
- '--section': The specific section within the .edgerc file containing the Akamai API credentials

## Script Detail

### createNewApiVersion.py

Creates a new API definition version. If the target API Gateway Definition version is not active, the script will detect this and perform no action on the property.

**Required Arguments**

- '--name': The Gateway property name for the target API Gateway (ex: My API Gateway).
- '--version': The target version to update (numeric or 'latest')

### updateEndpointFromDefinition.py

Updates an existing Akamai API Gateway resources using either a Swagger or RAML file definition. The script is responsive to detect both RAML and Swagger definition file types.

**Required Arguments**

- '--name': The Gateway property name for the target API Gateway (ex: My API Gateway).
- '--file': The relative or absolute path of the Swagger or RAML API definition which will be used to update the Akamai API Gateway definition.

### activateApiVersion.py

Activates a version of the Akamai API Gateway property version on either PRODUCTION or STAGING networks.

**Required Arguments**

- '--version': The version of the Akamai API Gateway property to activate.
- '--name': The Gateway property name for the target API Gateway (ex: My API Gateway).
- '--network': The target network to activate the version of the Akamai API Gateway on (PRODUCTION or STAGING).
- '--email': A comma-seperated list of e-mails for which activation statuses will be sent.