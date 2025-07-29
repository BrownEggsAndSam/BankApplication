String registeredByEmail = ""
try {
    User currentUser = userApi.getCurrentUser()
    registeredByEmail = currentUser?.getEmailAddress() ?: ""
} catch (Exception e) {
    loggerApi.warn("[PDD Template Export] Could not retrieve email from current user: ${e.getMessage()}")
}

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)

if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
