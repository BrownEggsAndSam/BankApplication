String resolveRegisteredByEmail() {
    String email = ""

    try {
        def initiator = execution.getVariable("user\$initiator")
        if (initiator != null) {
            loggerApi.info("[PDD Template Export] Retrieved user\$initiator: ${initiator}")
            email = initiator.getEmailAddress()
            loggerApi.info("[PDD Template Export] Retrieved user\$initiator email: ${email}")
        } else {
            loggerApi.warn("[PDD Template Export] user\$initiator is null")
        }

    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Exception while getting user\$initiator email: ${e.getMessage()}")
    }

    return email ?: ""
}
