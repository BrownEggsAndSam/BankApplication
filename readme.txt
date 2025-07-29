@Field String registeredByEmail = ""

@Field String registeredByEmail = ""

void resolveRegisteredByEmail() {
    loggerApi.info("[PDD Template Export] Attempting to resolve registeredByEmail using userApi.getCurrentUser()")

    try {
        def user = userApi.getCurrentUser()

        if (user == null) {
            loggerApi.warn("[PDD Template Export] userApi.getCurrentUser() returned null.")
            registeredByEmail = ""
        } else {
            registeredByEmail = user.getEmailAddress()
            if (registeredByEmail == null || registeredByEmail.trim().isEmpty()) {
                loggerApi.warn("[PDD Template Export] Current user object found, but email address is null or blank.")
            } else {
                loggerApi.info("[PDD Template Export] Successfully resolved registeredByEmail: ${registeredByEmail}")
            }

            // Log entire user object for debugging (if needed)
            loggerApi.debug("[PDD Template Export] User object details: ${user}")
        }

    } catch (Exception e) {
        loggerApi.error("[PDD Template Export] Exception occurred while resolving registeredByEmail: ${e.message}")
        registeredByEmail = ""
    }
}


resolveRegisteredByEmail()

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)
if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
