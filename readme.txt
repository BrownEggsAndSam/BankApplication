 def getCmdbAssetDataTemplate = """{
    "TableViewConfig": {
        "displayLength": 5,
        "Resources": {
            "Asset": {
                "DisplayName": { "name": "DisplayName" },
                "StringAttribute": [
                    {
                        "labelId": "0192e3cc-99f7-783c-b3d6-af7396f7af26",
                        "LongExpression": { "name": "BusinessOwner" }
                    },
                    {
                        "labelId": "8e362cd8-056d-4bde-8e362cd8d5b0",
                        "LongExpression": { "name": "TechnologyOwner" }
                    }
                ]
            }
        },
        "Filter": {
            "AND": [
                {
                    "Field": {
                        "name": "StringAttribute_03feee22-83af-4158-acb2-9660db25c4f2_Value",
                        "operator": "EQUALS",
                        "caseInsensitive": true,
                        "value": "%s"
                    }
                }
            ]
        },
        "Columns": [
            { "Column": { "fieldName": "DisplayName" }},
            { "Column": { "fieldName": "BusinessOwner" }},
            { "Column": { "fieldName": "TechnologyOwner" }}
        ]
    }
}"""


Map getCmdbAssetData(String selectedCmdbAssetId) {
    Map cmdbMetadata = new HashMap<String, String>()
    def response = executeExportJson(String.format(getCmdbAssetDataTemplate, selectedCmdbAssetId))
    def parsedData = new JsonSlurper().parseText(response)
    def res = parsedData.get("aaData")

    if (res.size() > 0) {
        def firstResult = res.first()
        cmdbMetadata.put("cmdbAssetName", firstResult.DisplayName ?: "")
        cmdbMetadata.put("businessOwner", firstResult["StringAttribute_0192e3cc-99f7-783c-b3d6-af7396f7af26_Value"] ?: "")
        cmdbMetadata.put("technologyOwner", firstResult["StringAttribute_8e362cd8-056d-4bde-8e362cd8d5b0_Value"] ?: "")

        if (verboseLogs) {
            loggerApi.info("[PDD Template Export] CMDB Asset Display Name: ${cmdbMetadata.get("cmdbAssetName")}")
            loggerApi.info("[PDD Template Export] Business Owner: ${cmdbMetadata.get("businessOwner")}")
            loggerApi.info("[PDD Template Export] Technical Owner: ${cmdbMetadata.get("technologyOwner")}")
        }
    } else {
        loggerApi.error("[PDD Template Export] No CMDB asset found for ID: ${selectedCmdbAssetId}")
    }

    return cmdbMetadata
}

Map cmdbData = getCmdbAssetData(cloudAssetId)
String derivedCmdbAssetName = cmdbData.get("cmdbAssetName") ?: ""
String derivedBusinessOwner = cmdbData.get("businessOwner") ?: ""
String derivedTechnologyOwner = cmdbData.get("technologyOwner") ?: ""

String datasetName = derivedCmdbAssetName ? "${derivedCmdbAssetName}_${selectedTable}" : selectedTable
mdDatasetNameCell.setCellValue(datasetName)
mdBusinessOwnerOrSmeCell.setCellValue(derivedBusinessOwner)
mdTechnicalPocCell.setCellValue(derivedTechnologyOwner)

