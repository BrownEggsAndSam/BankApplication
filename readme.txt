Map getCloudRegistryDataByDbUrl(String dbUrl) {
    Map result = [:]

    String tvc = """{
        "TableViewConfig": {
            "displayLength": -1,
            "Resources": {
                "Term": {
                    "Signifier": { "name": "AssetName" },
                    "Vocabulary": { "Name": { "name": "Domain_Name" } },
                    "StringAttribute": [
                        { "labelId": "6d5614df-4cd2-4098-b04c-9da52f6401c0", "LongExpression": { "name": "ApplicationEndpointUrl" }},
                        { "labelId": "a5d1ffa8-b9d7-439f-9e93-f2ebd6d3c41", "LongExpression": { "name": "ApplicationShortName" }}
                    ]
                }
            },
            "Filter": {
                "AND": [
                    { "Field": { "name": "ApplicationEndpointUrl", "operator": "EQUALS", "caseInsensitive": true, "value": "${dbUrl}" }}
                ]
            },
            "Columns": [
                { "Column": { "fieldName": "ApplicationEndpointUrl" }},
                { "Column": { "fieldName": "ApplicationShortName" }}
            ]
        }
    }"""

    def json = new JsonSlurper().parseText(runOutputJSON(tvc))
    def res = json.aaData

    if (res?.size() > 0) {
        result.put("ApplicationShortName", res[0].ApplicationShortName ?: "")
        result.put("ApplicationEndpointUrl", res[0].ApplicationEndpointUrl ?: "")
    } else {
        loggerApi.warn("[CloudRegistry Lookup] No match found for ApplicationEndpointUrl: ${dbUrl}")
    }

    return result
}

String dbUrl = execution.getVariable("dbUrl")
Map registryMatch = getCloudRegistryDataByDbUrl(dbUrl)
String appShortName = registryMatch.get("ApplicationShortName")

mdAppShortNameCell = mdRow.createCell(mdHeaderMap.get("App Short Name"))
mdAppShortNameCell.setCellValue(appShortName ?: "")
if (!appShortName) {
    mdAppShortNameCell.setCellStyle(infoNeededCellStyle)
    loggerApi.warn("[PDD Template Export] No Application Short Name found for DB URL: ${dbUrl}")
} else {
    loggerApi.info("[PDD Template Export] Found App Short Name '${appShortName}' for DB URL: ${dbUrl}")
}
