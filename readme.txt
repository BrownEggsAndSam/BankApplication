String registeredByEmail = ""
try {
    def optionalUser = userApi.getCurrentUser()  // Returns Optional<User>
    if (optionalUser.isPresent()) {
        def currentUser = optionalUser.get()
        registeredByEmail = currentUser?.getEmailAddress() ?: ""
    } else {
        loggerApi.warn("[PDD Template Export] No user present in optional for getCurrentUser()")
    }
} catch (Exception e) {
    loggerApi.warn("[PDD Template Export] Could not retrieve email from current user: ${e.getMessage()}")
}

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)

if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
