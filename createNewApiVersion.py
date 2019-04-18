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
requiredNamed.add_argument('--version', action="store", default="latest", help="The version of the API Gateway definition, which will be compared with the new external API definition.")
requiredNamed.add_argument('--name', action="store", nargs='+', help="The Gateway property name for the target API Gateway.")
args = parser.parse_args()

if len(sys.argv) <=3:
    parser.print_help()
    sys.exit(1)

# Command line arguments
version = args.version
name = ' '.join(args.name)



log.info('Using version passed from arguments: \'' + version + '\'')

for arg in sys.argv:
    log.debug('Argument: ' +  arg)

'''
    Edgegrid authentication Section
    Session and baseurl objects will be passed to helper methods.
'''

log.debug('Initializing Akamai {OPEN} client authentication. Edgerc: ' + args.config + ' Section: ' + args.section)

try:
    edgerc = EdgeRc(args.config)
    baseurl = 'https://%s' % edgerc.get(args.section, 'host')
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(edgerc, args.section)
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

if version == 'latest':
    log.info('Requested latest version.')
    version, apiName = apiGwHelper.getLatestVersion(session, baseurl, apiId)

log.info('Checking activation status for ' + apiName + ' version: ' + args.version)

networks = ['staging', 'production']

create = False

for network in networks:
    activeStatus, activeVersion = apiGwHelper.getActivationStatus(session, baseurl, apiId, version, network)

    log.info(network + ' network status: ' + activeStatus + ' version: ' + activeVersion + ' (current version: ' + version + ').')

    if version == activeVersion:
        create = True


if create == True:

    log.info('Creating new API version for ' + apiName + '. Based off version: ' + version)

    try:
        respCode = apiGwHelper.createApiVersion(session, baseurl, apiId, version)
    except Exception as e:
        log.error('Exception encountered creating new API endpoint version!')
        log.error(e)
        sys.exit(1)

    version, apiName = apiGwHelper.getLatestVersion(session, baseurl, apiId)
    log.info('Created new ' + apiName + ' API endpoint version: ' + version)

else:
    log.info('The latest ' + apiName + ' API Definition version ' + version + ' is not active in any network. Skipping create step.')