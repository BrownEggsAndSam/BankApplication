String resolveInitiatorEmail() {
    String registeredByEmail = ""

    try {
        String initiatorId = execution.getVariable("initiator")

        if (initiatorId != null) {
            User initiatorUser = userApi.getUser(string2Uuid(initiatorId))
            registeredByEmail = initiatorUser?.getEmailAddress() ?: ""
            loggerApi.info("[PDD Template Export] Registered By Email resolved: ${registeredByEmail}")
        } else {
            loggerApi.warn("[PDD Template Export] 'initiator' variable is null — did you forget to set it in the Start Event?")
        }

    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Failed to resolve initiator email: ${e.getMessage()}")
    }

    return registeredByEmail
}

String registeredByEmail = resolveInitiatorEmail()

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)

if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
