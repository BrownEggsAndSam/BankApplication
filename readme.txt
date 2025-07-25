List selectedTablesMapList = execution.getVariable("selectedTables")
List selectedTables = new ArrayList<String>()
List batches = new ArrayList<List<String>>()
int curBatchCount = 0

// File size estimation parameters
final int TEMPLATE_BASE_SIZE_MB = 1
final int MAX_FILE_SIZE_MB = 20
final int ESTIMATED_TABLE_SIZE_KB = 300
final int MAX_ADDITIONAL_MB = MAX_FILE_SIZE_MB - TEMPLATE_BASE_SIZE_MB
final int MAX_ADDITIONAL_KB = MAX_ADDITIONAL_MB * 1024

// Dynamically compute new batch size based on estimate
int estimatedBatchSizeLimit = Math.floor(MAX_ADDITIONAL_KB / ESTIMATED_TABLE_SIZE_KB) as int

if(verboseLogs) {
    loggerApi.info("[PDD Template Export] Assumed file size per dataset: ${ESTIMATED_TABLE_SIZE_KB} KB")
    loggerApi.info("[PDD Template Export] Estimated max batch size: ${estimatedBatchSizeLimit} datasets (to stay under ${MAX_FILE_SIZE_MB}MB)")
}

// Handle fallback to all tables if user selected none
if(verboseLogs) loggerApi.info("[PDD Template Export] User selected Tables: ${selectedTablesMapList}")
if(selectedTablesMapList == null || selectedTablesMapList.isEmpty()) {
    List tableNames = execution.getVariable("tableNameMapping")

    for(int i = 0; i < tableNames.size(); i++) {
        selectedTables.add(tableNames.get(i).value)
    }
} else {
    for(Map tableMapping : selectedTablesMapList) {
        selectedTables.add(tableMapping.get("value"))
    }
}

if(verboseLogs) loggerApi.info("[PDD Template Export] Final list of selected tables: ${selectedTables}")
if(verboseLogs) loggerApi.info("[PDD Template Export] Total number of selected Tables: ${selectedTables.size()}")

// Build batches using new size limit
for(String table : selectedTables) {
    if(curBatchCount == 0) {
        batches.add(new ArrayList<String>())
    }

    batches.get(batches.size() - 1).add(table)
    curBatchCount++

    if(curBatchCount == estimatedBatchSizeLimit) {
        curBatchCount = 0
    }
}

// Log batches
if(verboseLogs) {
    loggerApi.info("[PDD Template Export] Number of batches created: ${batches.size()}")
    for(int i = 0; i < batches.size(); i++) {
        loggerApi.info("[PDD Template Export] Batch ${i+1} contains ${batches[i].size()} tables: ${batches[i]}")
        if(batches[i].size() >= (estimatedBatchSizeLimit * 0.9)) {
            loggerApi.info("[PDD Template Export] Warning: Batch ${i+1} is near the estimated size limit.")
        }
    }
}

// Store for downstream subprocess loop
execution.setVariable("batches", batches)
execution.setVariable("numBatches", batches.size())
