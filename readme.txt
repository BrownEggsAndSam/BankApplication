@Field String registeredByEmail = ""

String resolveRegisteredByEmail() {
    try {
        def userOptional = userApi.getCurrentUser()
        if (userOptional.isPresent()) {
            def user = userOptional.get()
            return user.getEmailAddress() ?: ""
        } else {
            loggerApi.warn("[PDD Template Export] No current user found.")
            return ""
        }
    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Error while resolving registered by email: ${e.getMessage()}")
        return ""
    }
}



resolveRegisteredByEmail()

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)
if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
