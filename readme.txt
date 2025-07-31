String initiatorId = execution.getVariable("initiator")
String registeredByEmail = ""

if (initiatorId) {
    try {
        def user = userApi.getUser(string2Uuid(initiatorId))
        registeredByEmail = user?.email ?: ""
        loggerApi.info("[PDD Template Export] Setting Registered By: ${registeredByEmail}")
    } catch (Exception e) {
        loggerApi.error("[PDD Template Export] Could not fetch initiator user: ${e.message}")
    }
} else {
    loggerApi.warn("[PDD Template Export] No initiator variable found")
}

mdRegisteredByCell.setCellValue(registeredByEmail)
