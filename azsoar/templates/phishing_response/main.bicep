param workspaceId string
param location string = resourceGroup().location
param playbookName string = 'azsoar-phishing-response'

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: playbookName
  location: location
  tags: {
    CreatedBy: 'AzSOAR'
    Template: 'Phishing-Response'
    Severity: 'Medium'
    Purpose: 'Automated phishing response'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    definition: loadJsonContent('workflow.json')
    parameters: {
      workspaceId: {
        value: workspaceId
      }
    }
    state: 'Enabled'
  }
}

output logicAppId string = logicApp.id
output logicAppName string = logicApp.name
output principalId string = logicApp.identity.principalId
