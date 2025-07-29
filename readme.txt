@Field String registeredByEmail = ""

void resolveRegisteredByEmail() {
    try {
        def optionalUser = userApi.getCurrentUser()
        if (optionalUser.isPresent()) {
            def user = optionalUser.get()
            registeredByEmail = user?.getEmailAddress() ?: ""
            if (verboseLogs) loggerApi.info("[PDD Template Export] Registered By email: ${registeredByEmail}")
        } else {
            loggerApi.warn("[PDD Template Export] No current user found.")
        }
    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Failed to get current user email: ${e.getMessage()}")
    }
}

resolveRegisteredByEmail()

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)
if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
