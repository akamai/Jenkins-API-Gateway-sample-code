import yaml
import os.path
import urllib.parse

def determineDefinitionType(definition):

    '''

    :param definition:
    :return: String containing definition type.
    '''

    with open(definition) as file:
        line = file.readline()

    if 'raml' in line.lower():
        return 'raml'
    elif 'swagger' in line.lower():
        return 'swagger'
    else:
        return None

def getApiGwID(session, baseurl, name):

    endpoint = baseurl + '/api-definitions/v2/endpoints?contains=' + urllib.parse.quote(name)
    result = session.get(endpoint).json()

    if result['totalSize'] != 1:
        return None
    else:
        return result['apiEndPoints'][0]['apiEndPointId']

def getLatestVersion(session, baseurl, apiId):

    '''

    Returns a string with the latest version number of the API Gateway definition.

    :param session: A python requests EdgeGrid session object.
    :param baseurl: The value of the host field in an Akamai API credentials block.
    :param apiId: The ID of the API gateway definition.
    :return:
    '''

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions'
    result = session.get(endpoint).json()

    # Latest version should always be at position 0
    version = str(result['apiVersions'][0]['versionNumber'])
    name = str(result['apiEndPointName'])


    return version, name

def getResourceFromVersion(session, baseurl, apiId, version):

    '''

    Returns a JSON object containing the API definition (as returned from the API Gateway) for a specific API version.

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :return:
    '''

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions/' + version + '/resources-detail'
    result = session.get(endpoint).json()

    return result

def uploadSwaggerDef(session, baseurl, apiId, version, swaggerFile):

    '''

    Updates a specific version of an API Definition using an external swagger file.

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :param swaggerFile:
    :return:
    '''

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions/' + version + '/file'

    #params = {'importFileFormat': 'swagger'}
    params = {'importFileFormat': determineDefinitionType(swaggerFile)}
    files = {'importFile': (os.path.basename(swaggerFile), open(swaggerFile, 'r'), 'application/x-yaml')}
    resp = session.post(endpoint, data=params, files=files)

    return resp.status_code, resp.content

def compareDefinitionCounts(session, baseurl, apiId, version, swaggerFile):

    '''

    Compares the number of API resources in a swagger file (provided) with a specific API version.

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :param swaggerFile:
    :return:
    '''

    result = getResourceFromVersion(session, baseurl, apiId, version)
    apiDefNum = len(result['apiResources'])

    fileDef = yaml.load(open(swaggerFile, 'r'))
    fileDefNum = str(len(fileDef['paths'].keys()))

    return apiDefNum, fileDefNum

def activateVersion(session, baseurl, apiId, version, network, emailList):

    '''

    Activates and API Gateway definition on an Akamai network (Production or Staging)

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :param network:
    :param emailList:
    :return:
    '''

    activationObject = {
        "networks": [
            network
        ],
        "notificationRecipients": emailList,
        "notes": "Activating endpoint on + " + network + " network."
    }

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions/' + version + '/activate'
    resp = session.post(endpoint, json=activationObject)

    return resp.status_code, resp.content

def getActivationStatus(session, baseurl, apiId, version, network):

    '''

    Returns the status for an activation object.

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :param network:
    :return:
    '''

    result = getResourceFromVersion(session, baseurl, apiId, version)
    network = network + 'Version'
    activationStatus = result[network]['status']
    activationVersion = str(result[network]['versionNumber'])
    return activationStatus, activationVersion

def createApiVersion(session, baseurl, apiId, version):

    '''

    Creates a new API Gateway definition version.

    :param session:
    :param baseurl:
    :param apiId:
    :param version:
    :return:
    '''

    endpoint = baseurl + '/api-definitions/v2/endpoints/' + apiId + '/versions/' + version + '/cloneVersion'
    resp = session.post(endpoint)
    return resp.status_code