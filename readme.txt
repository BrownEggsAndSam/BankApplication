/**
 * Returns the email address of the currently logged-in user (workflow initiator).
 * Falls back to empty string and logs a warning if not available.
 */
String getRegisteredByEmail() {
    try {
        def optionalUser = userApi.getCurrentUser() // Returns Optional<User>
        if (optionalUser.isPresent()) {
            def user = optionalUser.get()
            return user?.getEmailAddress() ?: ""
        } else {
            loggerApi.warn("[PDD Template Export] No user present in optional for getCurrentUser()")
        }
    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Could not retrieve email from current user: ${e.getMessage()}")
    }
    return ""
}


String registeredByEmail = getRegisteredByEmail()



mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)

if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
