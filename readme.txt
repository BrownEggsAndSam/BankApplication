/*
*
*
*
*
*
*
*
*
*
*
*
*
*
*/
import org.flowable.engine.delegate.BpmnError

import java.util.Date

import com.collibra.dgc.core.api.dto.query.outputmodule.ExportJSONRequest
import com.collibra.dgc.workflow.api.exception.WorkflowException
import com.collibra.dgc.core.api.dto.PagedResponse
import com.collibra.dgc.core.api.dto.instance.attachment.FindAttachmentsRequest
import com.collibra.dgc.core.api.model.instance.Asset
import com.collibra.dgc.core.api.model.instance.User
import com.collibra.dgc.core.api.dto.file.AddFileRequest

import groovy.transform.Field
import groovy.json.JsonSlurper

import org.apache.poi.ss.usermodel.*
import org.apache.poi.ss.usermodel.DateUtil
import org.apache.poi.ss.usermodel.CellType
import org.apache.poi.ss.usermodel.CellStyle
import org.apache.poi.ss.usermodel.Color
import org.apache.poi.ss.usermodel.Row
import org.apache.poi.ss.usermodel.MissingCellPolicy
import org.apache.poi.ss.usermodel.Sheet
import org.apache.poi.xssf.usermodel.XSSFWorkbook
import org.apache.poi.xssf.usermodel.XSSFFont
import org.apache.poi.xssf.usermodel.XSSFColor
import org.apache.poi.ss.usermodel.FillPatternType
import org.apache.commons.io.IOUtils

/****************************************
 *              Global vars             *
 ****************************************/
@Field Map<String,Integer> mdHeaderMap = new HashMap<String,Integer>()
@Field Map<String,Integer> amdHeaderMap = new HashMap<String,Integer>()
@Field CellStyle defaultDateCellStyle
@Field CellStyle infoNeededCellStyle
@Field String trgtAssetName
@Field String trgtType
@Field String domainName
@Field boolean verboseLogs

class AttributeRow{
    String selectedTable
    Integer sequenceNumber
    Asset attribute
    Map attributeData
}

/****************************************
 *           Helper functions           *
 ****************************************/
 /**
 *
 *
 *
 */
String mdHeaderSearch(String s) {
    String key = mdHeaderMap.keySet().stream().find { 1 -> 1.contains(s) }
    if(key == null) throw new Exception("Error: Could not find the \"${s}\" column in the Dataset Metadata worksheet.")
    return key
}

String amdHeaderSearch(String s) {
    String key = amdHeaderMap.keySet().stream().find { 1 -> 1.contains(s) }
    if(key == null) throw new Exception("Error: Could not find the \"${s}\" column in the Attribute Metadata worksheet.")
    return key
}

String normalizeDataType(String inputDataType) {
    if (inputDataType == null || inputDataType.trim().isEmpty()) {
        return ""
    }
    // Convert input to uppercase for normalization
    String normalizedType = inputDataType.trim().toUpperCase()

    // Apply known type fixes
    if (normalizedType.equals("FLOATA")) {
        normalizedType = "FLOAT"
    }
    if (normalizedType.equals("DOUBLE PRECISION")) {
        normalizedType = "DOUBLE"
    }
    if (normalizedType.equals("TIMESTAMPTZ")) {
        normalizedType = "TIMESTAMP"
    }

    // List of allowable data types - hard coded for now... 07242025
    List<String> allowed = [
        "BIGINT","BLOB","BOOLEAN","CHAR","DATE","DATETIME","DECIMAL",
        "DOUBLE","FLOAT","INT","INTEGER","NUMBER","NUMERIC","NVARCHAR",
        "SMALLINT","STRING","TEXT","TIMESTAMP","VARCHAR","VARCHAR2"
    ]

    // Flag invalid types
    if (!allowed.contains(normalizedType)) {
        return normalizedType + " - INVALID TYPE"
    }

    return normalizedType
}
/**
*
*
*
*
*/
void getMetadataHeaders(Workbook workbook, Sheet sheet) {
    Iterator<Cell> cellIterator
    Iterator<Row> iterator = sheet.iterator()
    final int HEADER_LINE = 2
    Map headerMap
    String sheetName = sheet.getSheetName()

    if (sheet == null) throw new Exception("\"${sheetName}\" sheet not found in workbook")

    if(sheetName.toUpperCase().contains("DATASET")) {
        mdHeaderMap = new HashMap<String, Integer>()
        headerMap = mdHeaderMap
    } else {
        amdHeaderMap = new HashMap<String, Integer>()
        headerMap = amdHeaderMap
    }

    //Seek to header line
    for(int i = 0; i < HEADER_LINE; i++) {
        nextRow = iterator.next()
    }

    //Get headers
    cellIterator = nextRow.cellIterator()

    while (cellIterator.hasNext()) {
        Cell nextCell = cellIterator.next()
        int columnIndex = nextCell.getColumnIndex()
        String columnHeader = readCell(nextCell).trim()
        headerMap.put(columnHeader, columnIndex)
    }

    if(headerMap.size() == 0) 
        throw new WorkflowException("Header map not populated, check headers of file")
}
/**
*
*
*
*
*/
Cell fetchCell(Row r , String key) {
    if(key == null)
        throw new WorkflowException("HeaderMap Key ${key} is null")

    Integer idx = headerMap.get(key)

    if(idx == null)
        throw new WorkflowException("HeaderMap Key ${key} has null index. Check headers of file.")

    return r.getCell(idx, MissingCellPolicy.CREATE_NULL_AS_BLANK)
}

/**
*
*
*
*/
String readCell(Cell c) {
    if (c == null || CellType.BLANK.equals(c.getCellType())) return "" //empty string for null cell 
    switch(c.getCellType()) {
        case CellType.NUMERIC:
            if(DateUtil.isCellDateFormatted(c)) {
                return c.getDateCellValue().toString()
            } 
            else {
                def val = c.getNumericCellValue()
                if (val == (int) val) {
                    return String.valueOf((int) val)
                }
                else {
                    return String.valueOf(val.toString())
                }
            }
        case CellType.BOOLEAN:
            return String.valueOf(c.getBooleanCellValue())
        case CellType.FORMULA:
            try {
                switch(c.getCachedFormulaResultType()) {
                    case CellType.NUMERIC: 
                        return String.valueOf((int) c.getNumericCellValue())
                    case CellType.STRING: 
                        return c.getRichStringCellValue().toString()
                }
            } 
            catch(IllegalStateException e){
                return c.getCellFormula()
            }
        case CellType.ERROR:
            return FormulaError.forInt(c.getErrorCellValue()).toString()
        default:
            return c.getStringCellValue()
    
    }
}
/**
*
*
*
*
*/
String cleanCollibraData(String s) {
    StringBuilder sb = new StringBuilder()
    String cleanedString
    boolean replaceQuotes

    if(s == null) return null

    //Check if s is json
    //Do not replace quotes if json (Needed for DB ref checks)
    replaceQuotes = ! (s.contains("{") && s.contains("\"") && s.contains(":") && s.contains("}"))

    if(replaceQuotes) cleanedString = s.replaceAll(/<[^>]*>/, "").replaceAll(/"/, "`").trim()
    else cleanedString = s.replaceAll(/<[^>]*>/, "").trim()

    for(char c in cleanedString.toCharArray()) {
        int ascii = (int) c
        
        //Only append printable chars. (Uppercase and lowercase alphanumeric, punctuation, and whitespace)
        if(ascii >= 32 && ascii <= 126) sb.append(c)
    }

    return sb.toString()
}

/**
*
*
*
*/
def runOutputJSON(String templateString) {
    outputModuleApi.exportJSON(ExportJSONRequest.builder()
        .validationEnabled(true).viewConfig(templateString).build())
}

/**
* Fetches the File (attachment) from a given Asset ID. Returns Filename and File UUID as File Info
*/
Map getFileFromAsset() {
    List results
    UUID fileID
    UUID assetID = string2Uuid(execution.getVariable("templateAssetId"))
    Map fileInfo = new HashMap<String, String>()

    PagedResponse foundAttachments = attachmentApi.findAttachments(FindAttachmentsRequest.builder()
        .baseResourceId(assetID)
        .build()
    )
    results = foundAttachments.getResults()

    //Get ID of latest file attached
    for(int i = 0; i < results.size(); i++) {
        def file = results[i].getFile()
        if(verboseLogs) loggerApi.info("[PDD Template Export] Selected file: ${file.getName()}")
        fileInfo.put("name", file.getName())
        fileInfo.put("uuid", file.getId())
        return fileInfo
    }
}

/**
* Given a list of things, return a string of the list
*/
String stringifyList(List things) {
    StringBuilder sb = new StringBuilder()

    for(int i = 0; i < things.size(); i++) {
        if (i==0)
            sb.append("\"${things[i]}\"")
        else
            sb.append(",\"${things[i]}\"")
    }

    return sb.isEmpty() ? "?" : sb.toString()
}

/*
*
*
*/
String stringifyListFixAssetNames(List tableNames) {
    StringBuilder sb = new StringBuilder()
    
    for(int i = 0; i < tableNames.size(); i++) {
        if (i==0)
            sb.append("\"${cmdbAssetId}.${containerType}.${tableNames[i]}\"") 
        else
            sb.append(",\"${cmdbAssetId}.${containerType}.${tableNames[i]}\"")
    }
    
    return sb.isEmpty() ? "?" : sb.toString()
}

/*
*
*/



/*
*
*/
Map getDsetData(String domainName, List batch) {
    Map dsets = new HashMap<String,Map>()
    String tvc = """{
    "TableViewConfig": {
        "displayLength": -1,
        "Resources": {
        "Term": {
            "Signifier": { "name": "AssetName" },
            "Vocabulary": { "Name": { "name": "Domain_Name" } },
            "Relation": [{
            "typeId": "00000000-0000-0000-0000-000000007042",
            "type": "TARGET",
            "Source": { "Id": { "name": "AttributePhysId" } }
            }],
            "StringAttribute": [
            { "labelId": "00000000-0000-0000-0000-000000000202", "LongExpression": { "name": "Definition" }},
            { "labelId": "c68c5cd0-605e-46f5-ac14-69b354805615", "LongExpression": { "name": "BusinessOwner" }},
            { "labelId": "ea873e02-9483-4620-bf9f-9b1d4e4858e6", "LongExpression": { "name": "TechnicalPOC" }}
            ]
        }
        },
        "Filter": {
        "AND": [
            { "Field": { "name": "Domain_Name", "operator": "EQUALS", "caseInsensitive": true, "value": "${domainName}" }},
            { "Field": { "name": "AssetName", "operator": "IN", "caseInsensitive": true, "values": [${stringifyListFixAssetNames(batch)}] }}
        ]
        },
        "Columns": [
        { "Column": { "fieldName": "AssetName" }},
        { "Column": { "fieldName": "Definition" }},
        { "Column": { "fieldName": "BusinessOwner" }},
        { "Column": { "fieldName": "TechnicalPOC" }},
        { "Group": { "name": "AttributePhysNames", "Columns": [{ "Column": { "fieldName": "AttributePhysId" }}] }}
        ]
    }
    }"""

    def json = new JsonSlurper().parseText(runOutputJSON(tvc))
    def res = json.aaData

    if (verboseLogs) loggerApi.info("[PDD Template Export] Fetching dataset data for ${batch}")

    for(int i = 0; i < res.size(); i++) {
        Map dsetData = new HashMap<String,Object>()
        List attributePhysIds = new ArrayList<String>()
        String tableName = res[i].AssetName
        String definition = res[i].Definition
        String businessOwner = res[i].BusinessOwner ?: "" 
        String technicalPOC = res[i].TechnicalPOC ?: ""
        int indexOfLastDilimiter = tableName.indexOf(".", tableName.indexOf(execution.getVariable("containerType"))) //table name might have dot in it. Get the first dot after the container name
        
        if (definition == null) definition = ""
        if (indexOfLastDilimiter != -1) tableName = tableName.substring(indexOfLastDilimiter + 1)
        
        for(int j = 0; j < res[i].AttributePhysNames.size(); j++) {
            attributePhysIds.add(res[i].AttributePhysNames[j].AttributePhysId)
        }
        
        dsetData.put("definition", definition)
        dsetData.put("attributePhysIds", attributePhysIds)
        dsetData.put("businessOwner", businessOwner)
        dsetData.put("technicalPOC", technicalPOC)
        dsets.put(tableName, dsetData)
        
    }
    
    return dsets
}

/*
*
*/
Map getAttributeData(List attributePhysId, String domainName, String tableName) {
    Map attributes = new HashMap<String,Map>()
    String tvc = """{ "TableViewConfig": { "displayLength": -1, "Resources": { "Term": { "Id": { "name": "Id" }, "Vocabulary": { "Name": { "name": "Domain_Name" } }, "Relation": [{ "typeId": "e5a27c09-ab98-4200-907a-bade6ddf53ac", "type": "SOURCE", "Target": { "Signifier": { "name": "AttributeRegId" }} }], "StringAttribute": [ { "labelId": "5a4124b7-e7d2-4e81-ad5d-505832123d1e", "LongExpression": { "name": "DataType" }}, { "labelId": "00000000-0000-0000-0001-000050000043", "LongExpression": { "name": "LengthPrecision" }}, { "labelId": "4b229986-ad76-412e-9837-014abc27bb18", "LongExpression": { "name": "Scale" }}, { "labelId": "3754b636-8883-4728-8d2b-89557bab3ed4", "LongExpression": { "name": "Format" }}, { "labelId": "f5dfd59b-f287-45bd-9736-75ea3355680a", "LongExpression": { "name": "SequenceNumber" }}, { "labelId": "29d4091d-1d98-4563-ba6f-b67815529986", "LongExpression": { "name": "LogicalName" }}, { "labelId": "00000000-0000-0000-0000-000000000202", "LongExpression": { "name": "ModelAttrId" }}, { "labelId": "f5dfd59b-f287-45bd-9736-75ea3355680a", "LongExpression": { "name": "Definition" }} ] } }, "Filter": { "AND": [ { "Field": { "name": "Domain_Name", "operator": "EQUALS", "caseInsensitive": true, "value": "${domainName}" }}, { "Field": { "name": "Id", "operator": "IN", "values": [${stringifyList(attributePhysIds)}] }} ] }, "Columns": [ { "Column": { "fieldName": "Id" }}, { "Column": { "fieldName": "DataType" }}, { "Column": { "fieldName": "LengthPrecision" }}, { "Column": { "fieldName": "Scale" }}, { "Column": { "fieldName": "Format" }}, { "Column": { "fieldName": "SequenceNumber" }}, { "Column": { "fieldName": "AttributeRegId" }}, { "Column": { "fieldName": "LogicalName" }}, { "Column": { "fieldName": "ModelAttrId" }}, { "Column": { "fieldName": "Definition" }} ] } }"""
  
    def json = new JsonSlurper().parseText(runOutputJSON(tvc))
    def res = json.aaData

    for(int i = 0; i < res.size(); i++) {
        Map attributeData = new HashMap<String,String>()
        String dataType
        String lengthPrecision
        String scale
        String format
        String sequenceNumber
        String attributeRegId
        String logicalName
        String description
  
    // Extract values from response
        dataType = res[i].DataType
        dataType = normalizeDataType(dataType)
        lengthPrecision = res[i].LengthPrecision
        scale = res[i].Scale
        format = res[i].Format
        sequenceNumber = res[i].SequenceNumber
        attributeRegId = res[i].AttrID
        logicalName = res[i].LogicalName
        description = res[i].Definition

        if (dataType == null) dataType = ""
        if (lengthPrecision == null) lengthPrecision = ""
        if (scale == null) scale = ""
        if (format == null) format = ""
        if (sequenceNumber == null) sequenceNumber = ""
        if (attributeRegId == null) attributeRegId = ""
        if (logicalName == null) logicalName = ""
        if (description == null) description = ""
        if (logicalName.equals("")) logicalName = "(Provide Logical Name)"
        if (description.equals("")) description = "(Provide Description)"

        attributeData.put("dataType", dataType)
        attributeData.put("lengthPrecision", lengthPrecision)
        attributeData.put("scale", scale)
        attributeData.put("format", format)
        attributeData.put("sequenceNumber", sequenceNumber)
        attributeData.put("attributeRegId", attributeRegId)
        attributeData.put("logicalNamePlusDescription", logicalName + "^" + description)

        attributes.put(res[i].Id, attributeData)
    }

    return attributes
}

Map getCMDBAssetData(String assetId) {
    Map cmdbData = new HashMap<String, Object>()

    String tvc = """{
        "TableViewConfig": {
            "displayLength": -1,
            "Resources": {
                "Term": {
                    "Signifier": { "name": "AssetName" },
                    "Vocabulary": { "Name": { "name": "Domain_Name" } },
                    "StringAttribute": [
                        { "labelId": "0191e176-0309-73cd-bf48-08132aae4050", "LongExpression": { "name": "TOD" }},
                        { "labelId": "0191e175-d927-71a3-af97-310f10c08bcc", "LongExpression": { "name": "BOD" }}
                    ]
                }
            },
            "Filter": {
                "AND": [
                    { "Field": { "name": "Id", "operator": "EQUALS", "value": "${assetId}" }}
                ]
            },
            "Columns": [
                { "Column": { "fieldName": "AssetName" }},
                { "Column": { "fieldName": "TOD" }},
                { "Column": { "fieldName": "BOD" }}
            ]
        }
    }"""

    def json = new JsonSlurper().parseText(runOutputJSON(tvc))
    def res = json.aaData

    if (res?.size() > 0) {
        cmdbData.put("TOD", res[0].TOD ?: "")
        cmdbData.put("BOD", res[0].BOD ?: "")
    } else {
        loggerApi.warn("No CMDB asset data found for ID: ${assetId}")
    }

    return cmdbData
}


/****************************************
 *                 Main                *
 ****************************************/
try {
    Map fileInfo = getFileFromAsset()
    List selectedTables = execution.getVariable("batch")
    int batchNumber = execution.getVariable("batchNumber") + 1
    int numBatches = execution.getVariable("numBatches")
    def fInput = new File("in_${UUID.randomUUID()}.xlsm")
    new FileOutputStream(fInput).withCloseable { w -> fileApi.getFileAsStream(fileInfo.get("uuid")).withCloseable { is -> IOUtils.copy(is, w) }}
    def fOutput = numBatches > 1 ?
        new File("PDD-Export-${execution.getVariable("cmdbAssetId")}.${execution.getVariable("containerType")}-${(new Date()).format('yyyyMMddHHmmss')}.xlsm") :
        new File("PDD-Export-${execution.getVariable("cmdbAssetId")}.${execution.getVariable("containerType")}-${(new Date()).format('yyyyMMddHHmmss')}.xlsm")

    verboseLogs = execution.getVariable("verboseLogs")
    execution.setVariable("baseUrl", applicationApi.getInfo().getBaseUrl().replaceFirst(/\\/$/, ""))

    if (verboseLogs) loggerApi.info("[PDD Template Export] Writing batch ${batchNumber} of ${numBatches} to file")
    new XSSFWorkbook(fInput).withCloseable { workbook ->
        Sheet mdSheet = workbook.getSheet("Dataset Metadata")
        Sheet amdSheet = workbook.getSheet("Attribute Metadata")
        Map allDsetData
        String cloudAssetId = execution.getVariable("cmdbAssetId")
        Map cmdbData = getCMDBAssetData(cloudAssetId)
        String bod = cmdbData.get("BOD")
        String tod = cmdbData.get("TOD")
        loggerApi.info("[PDD Template Export] Retrieved CMDB Asset Data for ${cloudAssetId}: BOD = ${bod}, TOD = ${tod}")


        final int HEADER_LINE = 2

        domainName = cloudAssetId + '.' + execution.getVariable("containerType")
        allDsetData = getDsetData(domainName, selectedTables)

        if (verboseLogs) loggerApi.info("[PDD Template Export] Domain Name: ${domainName}")

        // Create date cell style
        defaultDateCellStyle = workbook.createCellStyle()
        defaultDateCellStyle.setFillForegroundColor(new XSSFColor([170, 215, 245] as byte[]))
        defaultDateCellStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)
        defaultDateCellStyle.setDataFormat((short) 14)

        // Create info-needed cell style
        infoNeededCellStyle = workbook.createCellStyle()
        infoNeededCellStyle.setFillForegroundColor(new XSSFColor([170, 215, 245] as byte[]))
        infoNeededCellStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND)

        // Get headers
        getMetadataHeaders(workbook, mdSheet)
        getMetadataHeaders(workbook, amdSheet)

        List<AttributeRow> allAttributeRows = []

        // Fill in the workbook
        for (selectedTable in selectedTables) {
            String datasetAssetName = "${domainName}.${selectedTable}"
            Map dsetData = allDsetData.get(selectedTable)
            Map allAttributeData
            List attributePhysIds
            Row mdRow
            Cell mdDatasetNameCell
            Cell mdDescCell
            Cell mdDataSourceCell
            Cell mdDestLayerCell
            Cell mdConfidentialityCell
            Cell mdNpiDatasetCell
            Cell mdDatasetClassificationCell
            Cell mdTopic
            Cell mdTopicCategory
            Cell mdBusinessOwnerOrSmeCell
            Cell mdTechnicalPocCell
            Cell mdAppShortNameCell
            Cell mdRefreshTypeCell
            Cell mdRefreshFrequencyCell
            Cell mdDatasetRetentionPeriodCell
            Cell mdConsumerIndicatorCell
            Cell mdRegisteredByCell
            Cell mdDirectCopyCell

            if (dsetData == null) {
                loggerApi.error("[PDD Template Export] Error: Could not find dataset with name ${datasetAssetName} using table")
                continue
            }

            attributePhysIds = (List<String>) dsetData.get("attributePhysIds")
            mdRow = mdSheet.createRow(mdSheet.getLastRowNum() + 1)

            // Fill in the dataset metadata sheet
            mdRow.createCell(mdHeaderMap.get("Dataset Registry ID")).setCellValue("")
            mdDatasetNameCell = mdRow.createCell(mdHeaderMap.get("Dataset Name"))
            mdDatasetNameCell.setCellValue("${selectedTable}")
            mdDatasetNameCell.setCellStyle(infoNeededCellStyle)
            mdDescCell = mdRow.createCell(mdHeaderMap.get("Dataset Description"))
            mdDescCell.setCellValue((String) dsetData.get("definition"))
            mdDescCell.setCellStyle(infoNeededCellStyle)
            mdRow.createCell(mdHeaderMap.get("Dataset Type")).setCellValue("${execution.getVariable("datasetType")}")
            mdRow.createCell(mdHeaderMap.get("Cloud Asset ID")).setCellValue("${cloudAssetId}")
            mdDataSourceCell = mdRow.createCell(mdHeaderMap.get("Data Source System"))
            mdDataSourceCell.setCellValue("")
            mdDataSourceCell.setCellStyle(infoNeededCellStyle)
            mdDestLayerCell = mdRow.createCell(mdHeaderMap.get("Dataset Layer"))
            mdDestLayerCell.setCellValue("Not Applicable")
            mdDestLayerCell.setCellStyle(infoNeededCellStyle)
            mdConfidentialityCell = mdRow.createCell(mdHeaderMap.get("Confidentiality Level"))
            mdConfidentialityCell.setCellValue("")
            mdConfidentialityCell.setCellStyle(infoNeededCellStyle)
            mdNpiDatasetCell = mdRow.createCell(mdHeaderMap.get("NPI Dataset"))
            mdNpiDatasetCell.setCellValue("")
            mdNpiDatasetCell.setCellStyle(infoNeededCellStyle)
            mdDatasetClassificationCell = mdRow.createCell(mdHeaderMap.get("Dataset Classification Type"))
            mdDatasetClassificationCell.setCellValue("")
            mdDatasetClassificationCell.setCellStyle(infoNeededCellStyle)
            mdTopic = mdRow.createCell(mdHeaderMap.get("Topic"))
            mdTopic.setCellValue("")
            mdTopic.setCellStyle(infoNeededCellStyle)
            mdTopicCategory = mdRow.createCell(mdHeaderMap.get("Topic Category"))
            mdTopicCategory.setCellValue("")
            mdBusinessOwnerOrSmeCell = mdRow.createCell(mdHeaderMap.get("Business Owner or Data SME"))
            mdBusinessOwnerOrSmeCell.setCellValue(bod ? bod + "@gmail.com" : "")
            if (!bod) {
                mdBusinessOwnerOrSmeCell.setCellStyle(infoNeededCellStyle)
            }

            mdTechnicalPocCell = mdRow.createCell(mdHeaderMap.get("Technical POC"))
            mdTechnicalPocCell.setCellValue(tod ? tod + "@gmail.com" : "")
            if (!tod) {
                mdTechnicalPocCell.setCellStyle(infoNeededCellStyle)
            }

            mdAppShortNameCell = mdRow.createCell(mdHeaderMap.get("App Short Name"))
            mdAppShortNameCell.setCellValue("")
            mdAppShortNameCell.setCellStyle(infoNeededCellStyle)
            mdRow.createCell(mdHeaderMap.get("S3 Bucket Name / AWS Service")).setCellValue("${awsService}")
            mdRow.createCell(mdHeaderMap.get("Structured Data")).setCellValue("Structured Data")
            mdRow.createCell(mdHeaderMap.get("Database Endpoint")).setCellValue("${execution.getVariable("dbUrl")}")
            mdRow.createCell(mdHeaderMap.get("Cloud Database Name")).setCellValue("${execution.getVariable("dbName")}")
            mdRow.createCell(mdHeaderMap.get("Database Schema")).setCellValue("${execution.getVariable("dbSchema")}")
            mdRow.createCell(mdHeaderMap.get("Table Name")).setCellValue("${selectedTable}")
            mdRow.createCell(mdHeaderMap.get("File Format")).setCellValue("Not Applicable")
            mdRefreshTypeCell = mdRow.createCell(mdHeaderMap.get("Refresh Type"))
            mdRefreshTypeCell.setCellValue("")
            mdRefreshTypeCell.setCellStyle(infoNeededCellStyle)
            mdRefreshFrequencyCell = mdRow.createCell(mdHeaderMap.get("Refresh Frequency"))
            mdRefreshFrequencyCell.setCellValue("")
            mdRefreshFrequencyCell.setCellStyle(infoNeededCellStyle)
            mdDatasetRetentionPeriodCell = mdRow.createCell(mdHeaderMap.get("Dataset Data Retention Period"))
            mdDatasetRetentionPeriodCell.setCellValue("")
            mdDatasetRetentionPeriodCell.setCellStyle(infoNeededCellStyle)
            mdConsumerIndicatorCell = mdRow.createCell(mdHeaderMap.get("Consumer Data (Indicator)"))
            mdConsumerIndicatorCell.setCellValue("")
            mdConsumerIndicatorCell.setCellStyle(infoNeededCellStyle)
            String registeredBy = execution.getVariable("user$Intiator")
            mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
            mdRegisteredByCell.setCellValue("")
            mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
            mdRow.createCell(mdHeaderMap.get("Application Security Group")).setCellValue("dfit")
            mdRow.createCell(mdHeaderMap.get("Dataset Schema Version")).setCellValue("1")
            mdDirectCopyCell = mdRow.createCell(mdHeaderMap.get("Direct Copy Flag"))
            mdDirectCopyCell.setCellValue("")
            mdDirectCopyCell.setCellStyle(infoNeededCellStyle)

            // Fill in the attribute metadata sheet
            allAttributeData = attributePhysIds.isEmpty() ? null : getAttributeData(attributePhysIds, domainName, selectedTable)
            if (verboseLogs) loggerApi.info("[PDD Template Export] Filling in Attribute Metadata Sheet with ${attributePhysIds.size()} attributes")
            for (attributePhysId in attributePhysIds) {
                Asset attribute = assetApi.getAsset(string2Uuid(attributePhysId))
                Map attributeData = allAttributeData.get(attributePhysId)
                Row amdRow
                Cell amdDataSetNameCell
                Cell amdDescCell
                Cell amdDateCell

                if (attributeData == null || attribute == null) {
                    loggerApi.error("[PDD Template Export] Error: Could not find attribute with ID ${attributePhysId}. Skipping")
                    continue
                }

                Integer seq = 9999
                try {
                    seq = attributeData.get("sequenceNumber")?.toString()?.toInteger() ?: 9999
                } catch (Exception e) {
                    loggerApi.error("[PDD Template Export] Error: Invalid sequenceNumber for ${attribute.getDisplayName()}, defaulting to 9999")
                }

                allAttributeRows.add(new AttributeRow(
                    selectedTable: selectedTable,
                    sequenceNumber: seq,
                    attribute: attribute,
                    attributeData: attributeData
                ))
            }
            logger.info("[PDD Template Export] Sorting and writing Attribute Metadata rows")

            allAttributeRows.sort { a,b ->
                a.selectedTable <=> b.selectedTable ?: a.sequenceNumber <=> b.sequenceNumber
            }

            for (row in allAttributeRows) {
                amdRow = amdSheet.createRow(amdSheet.getLastRowNum() + 1)

                amdRow.createCell(amdHeaderMap.get("Attribute Registry ID")).setCellValue(row.attributeData.get("attributeRegId"))
                amdRow.createCell(amdHeaderMap.get("Physical Attribute Name")).setCellValue("${row.attribute.getDisplayName()}")

                amdDescCell = amdRow.createCell(amdHeaderMap.get("Logical Attribute Name + Description/Definition"))
                amdDescCell.setCellValue(row.attributeData.get("logicalNamePlusDescription"))
                amdDescCell.setCellStyle(infoNeededCellStyle)

                amdDataSetNameCell = amdRow.createCell(amdHeaderMap.get("Dataset Registry ID"))
                amdDataSetNameCell.setCellValue(row.selectedTable)
                amdDataSetNameCell.setCellStyle(infoNeededCellStyle)

                amdRow.createCell(amdHeaderMap.get("Attribute Schema Version")).setCellValue("1")
                amdRow.createCell(amdHeaderMap.get("Attribute Sequence Number")).setCellValue(attributeData.get("sequenceNumber"))
                amdRow.createCell(amdHeaderMap.get("Data Type")).with { 
                    setCellValue(row.attributeData.get("dataType"))
                    if (row.attributeData.get("dataType").contains("INVALID TYPE")) {
                        setCellStyle(infoNeededCellStyle)
                    }
                }
                amdRow.createCell(amdHeaderMap.get("Length / Precision")).setCellValue(attributeData.get("lengthPrecision"))
                amdRow.createCell(amdHeaderMap.get("Scale")).setCellValue(attributeData.get("scale"))
                amdRow.createCell(amdHeaderMap.get("Format")).setCellValue(attributeData.get("format"))

                amdDateCell = amdRow.createCell(amdHeaderMap.get("Expected Production Date"))
                amdDateCell.setCellValue("")
                amdDateCell.setCellStyle(defaultDateCellStyle)

                amdRow.createCell(amdHeaderMap.get("Dataset Type")).setCellValue("${execution.getVariable("datasetType")}")
            }
        }

        // Write output
        new FileOutputStream(fOutput).withCloseable { os -> workbook.write(os) }
        execution.setVariable("exportedTemplate", fOutput)

        loggerApi.inf("[PDD Template Export] DEBUG CHECKPOINT: End of Template Generation Script")
    }

} catch (Exception e) {
    loggerApi.info("[PDD Template Export] Exception: " + e)
    execution.setVariable("errorMsg", e.getMessage())
}
