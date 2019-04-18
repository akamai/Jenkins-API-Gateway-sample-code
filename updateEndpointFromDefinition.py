import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
import logging
import sys
import argparse
import os
from lib import apiGwHelper

logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger()

# Source in command line arguments
parser = argparse.ArgumentParser(description='API GW CI demo toolkit -> ' + os.path.basename(__file__), formatter_class=argparse.ArgumentDefaultsHelpFormatter)
requiredNamed = parser.add_argument_group('required arguments')
parser.add_argument('--config', action="store", default=os.environ['HOME'] + "/.edgerc", help="Full or relative path to .edgerc file")
parser.add_argument('--section', action="store", default="default", help="The section of the edgerc file with the proper {OPEN} API credentials.")
requiredNamed.add_argument('--file', action="store", default=[], help="The relative or absolute path to the swagger or RAML file.")
requiredNamed.add_argument('--name', action="store", nargs='+', help="The Gateway property name for the target API Gateway.")
args = parser.parse_args()

# Full path to '.edgerc' file
edgeRcLoc = args.config
edgeRcSection = args.section
name = ' '.join(args.name)
swaggerFile = args.file

# Verify file exists
if os.path.isfile(swaggerFile) != True:
    log.error('The Swagger or RAML file argument provided is not a valid file, or it cannot be found.')
    log.error('Ensure the file is properly pathed and exists, with read permissions.')
    sys.exit(1)

fileFormat = apiGwHelper.determineDefinitionType(swaggerFile)
log.info('Using + ' + fileFormat + ' file: ' + swaggerFile)

'''
    Edgegrid authentication Section
    Session and baseurl objects will be passed to helper methods.
'''

log.debug('Initializing Akamai {OPEN} client authentication. Edgerc: ' + edgeRcLoc + ' Section: ' + edgeRcSection)

try:
    edgerc = EdgeRc(edgeRcLoc)
    baseurl = 'https://%s' % edgerc.get(edgeRcSection, 'host')
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(edgerc, edgeRcSection)
    log.debug('API Base URL: ' + baseurl)

except Exception as e:
    log.error('Error authenticating Akamai {OPEN} API client.')
    log.error(e)

result = apiGwHelper.getApiGwID(session, baseurl, name)

if result is None:
    log.error('No API definition could be found with the name: \'' + name + '\'')
    log.error('Please make sure the correct name is specified, or it exists on the contract tied to your Edgegrid API authorizations.')
    sys.exit(1)
else:
    apiId = str(result)

log.info('Retrieving version from API: ' + apiId)

try:
    version, apiName = apiGwHelper.getLatestVersion(session, baseurl, apiId)
except Exception as e:
    log.error('Error getting latest version!')
    log.error(e)

log.info('Using latest version Id: ' + version + ' for API definition: ' + apiName)

# Compare API Definition and Swagger resource count
log.info('Comparing API definition resources with Swagger definition...')
try:
    apiDefNum, fileDefNum = apiGwHelper.compareDefinitionCounts(session, baseurl, apiId, version, swaggerFile)
    log.info(fileFormat + ' file resources: ' + str(fileDefNum) + '. API Definition Resources: ' + str(apiDefNum) + '.')

except Exception as e:
    log.error('Error encountered obtaining API resource counts for version: ' + version)
    log.error('Proceeding...')

log.info('Importing new API definitions from file: ' + swaggerFile)
try:

    respCode, respContent = apiGwHelper.uploadSwaggerDef(session, baseurl, apiId, version, swaggerFile)

    if respCode != 200:
        log.error('API Gateway returned an error!')
        log.error('Error: ' + str(respContent))

    log.info('Import Success! Response code: ' + str(respCode))


except Exception as e:
    log.error('Error importing API definition!')
    log.error(e)