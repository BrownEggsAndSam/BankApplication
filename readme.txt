String initiatorEmail = ""
try {
    String initiatorId = execution.getProcessInstance().getStartUserId()
    if (initiatorId != null) {
        User initiatorUser = userApi.findUserByUsername(initiatorId)
        initiatorEmail = initiatorUser?.getEmailAddress()
    }
} catch (Exception e) {
    loggerApi.warn("[PDD Template Export] Could not retrieve initiator email: " + e.getMessage())
}

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(initiatorEmail)

if (initiatorEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
