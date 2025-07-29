@Field String registeredByEmail = ""

void resolveRegisteredByEmail() {
    try {
        def currentUser = userApi.getCurrentUser().get()
        registeredByEmail = currentUser?.getEmailAddress() ?: ""
        if (verboseLogs) {
            loggerApi.info("[PDD Template Export] Registered By email resolved: ${registeredByEmail}")
        }
    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Failed to retrieve Registered By email: ${e.getMessage()}")
    }
}

resolveRegisteredByEmail()

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)
if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
