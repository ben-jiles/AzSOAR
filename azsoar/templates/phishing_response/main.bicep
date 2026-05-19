param workspaceId string
param location string = 'eastus'

resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: '${playbook_name}'
  location: location
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
  }
}

output logicAppId string = logicApp.id
