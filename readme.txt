Map getCmdbDerivedOwners(String cmdbAssetId) {
    String tvc = String.format(filterCmdbAssetRegistryByCmdbAssetIdTemplate, cmdbAssetId)
    def json = new JsonSlurper().parseText(runOutputJSON(tvc))
    def results = json.aaData

    def derivedBusinessOwner = ""
    def derivedTechnologyOwner = ""
    def derivedCmdbAssetName = ""

    if (results.size() > 0) {
        def cmdbAsset = results.first()

        derivedCmdbAssetName = cmdbAsset["DisplayName"]

        def businessOwnerList = cmdbAsset["StringAttribute_" + businessOwnerUuid]
        if (businessOwnerList?.size() > 0)
            derivedBusinessOwner = businessOwnerList.first()["StringAttribute_" + businessOwnerUuid + "_Value"]

        def techOwnerList = cmdbAsset["StringAttribute_" + technologyOwnerUuid]
        if (techOwnerList?.size() > 0)
            derivedTechnologyOwner = techOwnerList.first()["StringAttribute_" + technologyOwnerUuid + "_Value"]
    }

    return [
        "derivedCmdbAssetName": derivedCmdbAssetName,
        "derivedBusinessOwner": derivedBusinessOwner,
        "derivedTechnologyOwner": derivedTechnologyOwner
    ]
}


============
Map derivedOwnerData = getCmdbDerivedOwners(cloudAssetId)

String derivedBusinessOwner = derivedOwnerData.derivedBusinessOwner
String derivedTechnologyOwner = derivedOwnerData.derivedTechnologyOwner
String derivedCmdbAssetName = derivedOwnerData.derivedCmdbAssetName

if (verboseLogs) {
    loggerApi.info("[PDD Template Export] Derived CMDB Asset Name: ${derivedCmdbAssetName}")
    loggerApi.info("[PDD Template Export] Derived Business Owner: ${derivedBusinessOwner}")
    loggerApi.info("[PDD Template Export] Derived Technology Owner: ${derivedTechnologyOwner}")
}

============
mdBusinessOwnerOrSmeCell = mdRow.createCell(mdHeaderMap.get("Business Owner or Data SME"))
mdBusinessOwnerOrSmeCell.setCellValue(derivedBusinessOwner)
mdBusinessOwnerOrSmeCell.setCellStyle(infoNeededCellStyle)

mdTechnicalPocCell = mdRow.createCell(mdHeaderMap.get("Technical POC"))
mdTechnicalPocCell.setCellValue(derivedTechnologyOwner)
mdTechnicalPocCell.setCellStyle(infoNeededCellStyle)
