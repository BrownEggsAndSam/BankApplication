
for (attributePhysId in attributePhysIds) {
    Asset attribute = assetApi.getAsset(string2Uuid(attributePhysId))
    Map attributeData = allAttributeData.get(attributePhysId)

    if (attribute == null || attributeData == null) continue

    def seqNum = attributeData.get("sequenceNumber") ?: "0"

    allAttributeRows.add(new AttributeRow(
        selectedTable: selectedTable,
        sequenceNumber: seqNum.toInteger(),
        attribute: attribute,
        attributeData: attributeData
    ))
}

// Sort collected attributes by table name and sequence number
allAttributeRows.sort { a, b ->
    a.selectedTable <=> b.selectedTable ?: a.sequenceNumber <=> b.sequenceNumber
}

// Write sorted data to Attribute Metadata sheet
for (row in allAttributeRows) {
    Row amdRow = amdSheet.createRow(amdSheet.getLastRowNum() + 1)

    amdRow.createCell(amdHeaderMap.get("Attribute Registry ID")).setCellValue(row.attributeData.get("attributeRegId"))
    amdRow.createCell(amdHeaderMap.get("Physical Attribute Name")).setCellValue(row.attribute.getDisplayName())

    Cell amdDescCell = amdRow.createCell(amdHeaderMap.get("Logical Attribute Name + Description/Definition"))
    amdDescCell.setCellValue(row.attributeData.get("logicalNamePlusDescription"))
    amdDescCell.setCellStyle(infoNeededCellStyle)

    Cell amdDataSetNameCell = amdRow.createCell(amdHeaderMap.get("Dataset Registry ID"))
    amdDataSetNameCell.setCellValue(row.selectedTable)
    amdDataSetNameCell.setCellStyle(infoNeededCellStyle)

    amdRow.createCell(amdHeaderMap.get("Attribute Schema Version")).setCellValue("1")
    amdRow.createCell(amdHeaderMap.get("Attribute Sequence Number")).setCellValue(row.sequenceNumber)
    amdRow.createCell(amdHeaderMap.get("Data Type")).setCellValue(row.attributeData.get("dataType"))
    amdRow.createCell(amdHeaderMap.get("Length / Precision")).setCellValue(row.attributeData.get("lengthPrecision"))
    amdRow.createCell(amdHeaderMap.get("Scale")).setCellValue(row.attributeData.get("scale"))
    amdRow.createCell(amdHeaderMap.get("Format")).setCellValue(row.attributeData.get("format"))

    Cell amdDateCell = amdRow.createCell(amdHeaderMap.get("Expected Production Date"))
    amdDateCell.setCellValue("")
    amdDateCell.setCellStyle(defaultDateCellStyle)

    amdRow.createCell(amdHeaderMap.get("Dataset Type")).setCellValue(execution.getVariable("datasetType"))
}
