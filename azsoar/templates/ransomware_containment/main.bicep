param workspaceId string
param location string = resourceGroup().location
param playbookName string = 'azsoar-ransomware-containment'

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: playbookName
  location: location
  tags: {
    CreatedBy: 'AzSOAR'
    Template: 'Ransomware-Containment'
    Severity: 'Critical'
    Purpose: 'Automated ransomware containment'
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
output principalId string = logicApp.identity.principalId
