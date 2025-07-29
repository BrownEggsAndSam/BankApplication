Map getCMDBData(String cloudAssetId) {
    Map cmdbData = [:]
    String tvc = """{
        "TableViewConfig": {
            "displayLength": -1,
            "Resources": {
                "Asset": {
                    "skipComplexRelationsViewPermissions": true,
                    "Signifier": { "name": "FullName" },
                    "Vocabulary": { "Name": { "name": "Domain_Name" } },
                    "StringAttribute": [
                        {
                            "labelId": "0191e176-0309-73cd-bf48-08132ae0450a",
                            "LongExpression": { "name": "TOD" }
                        },
                        {
                            "labelId": "0191e175-d927-71a3-af97-310f10c88cc8",
                            "LongExpression": { "name": "BOD" }
                        }
                    ]
                }
            },
            "Filter": {
                "AND": [
                    {
                        "Field": {
                            "name": "Domain_Name",
                            "operator": "EQUALS",
                            "caseInsensitive": true,
                            "value": "CMDB Asset Registry"
                        }
                    },
                    {
                        "Field": {
                            "name": "AssetName",
                            "operator": "EQUALS",
                            "value": "${cloudAssetId}"
                        }
                    }
                ]
            },
            "Columns": [
                { "Column": { "fieldName": "AssetName" }},
                { "Column": { "fieldName": "TOD" }},
                { "Column": { "fieldName": "BOD" }}
            ]
        }
    }"""

    try {
        if (verboseLogs) loggerApi.info("[PDD Template Export] Querying CMDB Asset Registry for CloudAssetId = ${cloudAssetId}")
        def json = new JsonSlurper().parseText(runOutputJSON(tvc))
        def res = json?.aaData

        if (res == null || res.isEmpty()) {
            loggerApi.warn("[PDD Template Export] No CMDB asset found for CloudAssetId = ${cloudAssetId}")
            return [TOD: "", BOD: ""]
        }

        def row = res[0]
        String tod = row?.TOD ?: ""
        String bod = row?.BOD ?: ""

        cmdbData.put("TOD", tod)
        cmdbData.put("BOD", bod)

        loggerApi.info("[PDD Template Export] Retrieved TOD='${tod}' and BOD='${bod}' for CloudAssetId = ${cloudAssetId}")
        return cmdbData

    } catch (Exception e) {
        loggerApi.error("[PDD Template Export] Error retrieving CMDB metadata for ${cloudAssetId}: ${e.message}")
        return [TOD: "", BOD: ""]
    }
}



Map cmdbData = getCMDBData(cloudAssetId)
mdTechnicalPocCell.setCellValue(cmdbData.TOD)
mdBusinessOwnerOrSmeCell.setCellValue(cmdbData.BOD)
