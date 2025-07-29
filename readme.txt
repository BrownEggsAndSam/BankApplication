@Field String registeredByEmail = ""


void resolveRegisteredByEmail() {
    try {
        String initiatorUsername = execution.getVariable("initiator")
        if (initiatorUsername == null || initiatorUsername.trim().isEmpty()) {
            loggerApi.warn("[PDD Template Export] No initiator username found in execution variables")
            registeredByEmail = ""
            return
        }

        User initiatorUser = userApi.findUserByUsername(initiatorUsername)
        registeredByEmail = initiatorUser?.getEmailAddress() ?: ""
        loggerApi.info("[PDD Template Export] Resolved initiator email: ${registeredByEmail}")
    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Could not retrieve Registered By email: ${e.getMessage()}")
        registeredByEmail = ""
    }
}


resolveRegisteredByEmail()


mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredByEmail)
if (registeredByEmail.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
