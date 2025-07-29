String getRegisteredByEmail() {
    String email = ""
    try {
        def initiator = execution.getVariable("user$initiator")
        if (initiator != null) {
            email = initiator.getEmailAddress()
            loggerApi.info("[PDD Template Export] Registered By email resolved from user\$initiator: ${email}")
        } else {
            loggerApi.warn("[PDD Template Export] user\$initiator is null — no email will be populated")
        }
    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Exception while retrieving user\$initiator email: ${e.getMessage()}")
    }
    return email ?: ""
}
