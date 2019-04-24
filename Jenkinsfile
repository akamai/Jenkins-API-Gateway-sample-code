pipeline { 
    agent any 
    options {
        skipStagesAfterUnstable()
        disableConcurrentBuilds()
    }
    environment {
        /*
            Change these environment variables based on your specific project
        */

        // Assumes you have defined a Jenkins environment variable 'PATH+EXTRA'
        PROJ = "/bin:/usr/local/bin:/usr/bin"

        // Name of CSV file containing network list
        APIDEFFILE = "api.yaml"

        // Name of network list to update
        APIGWNAME = "API Gateway Demo"

        // Link to VCS project containing network list
        APISCM = "git@github.com:dmcallis1/rapid-definition.git"

        // Comma-seperated e-mail list
        APIGWEMAIL = "dmcallis@akamai.com"

        // Path to python project, if pipeline script are not in PATH
        APIPATH = "/var/lib/jenkins/Jenkins-API-Gateway-sample-code"
    }
    parameters {
        choice(name: 'NETWORK', choices: ['staging', 'production'], description: 'The network to activate the network list.')
        string(name: 'VERSION', defaultValue: 'latest', description: 'Append to or overwrite the target list based on the supplied file contents.')
    }
    stages {
     stage('Pull API Definition') {
            steps {
                git "${env.APISCM}"

                archiveArtifacts "${env.APIDEFFILE}"

            }
        }
        stage('Create API Version') {
            steps {
                step([  $class: 'CopyArtifact',
                        filter: '*.yaml',
                        fingerprintArtifacts: true,
                        projectName: '${JOB_NAME}',
                        selector: [$class: 'SpecificBuildSelector', buildNumber: '${BUILD_NUMBER}']
                ])
                withEnv(["PATH+EXTRA=$PROJ"]) {
                    sh 'python3 $APIPATH/createNewApiVersion.py --name $APIGWNAME --version ${VERSION}'
                }

                archiveArtifacts "${env.APIDEFFILE}"

            }
        }
        stage('Update API Definition'){
            steps {
                step([  $class: 'CopyArtifact',
                        filter: '*.yaml',
                        fingerprintArtifacts: true,
                        projectName: '${JOB_NAME}',
                        selector: [$class: 'SpecificBuildSelector', buildNumber: '${BUILD_NUMBER}']
                ])
                withEnv(["PATH+EXTRA=$PROJ"]) {
                    sh 'python3 $APIPATH/updateEndpointFromDefinition.py --name $APIGWNAME --file $APIDEFFILE'
                }
            }
        }
        stage('Activate API Definition'){
            steps {
                withEnv(["PATH+EXTRA=$PROJ"]) {
                    sh 'python3 $APIPATH/activateApiVersion.py --name $APIGWNAME --network ${NETWORK} --version ${VERSION} --email $APIGWEMAIL'
                }
            }
        }
    }
}