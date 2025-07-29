String resolveRegisteredByEmail() {
    String email = ""

    try {
        def currentUser = userApi.getCurrentUser()
        if (currentUser != null) {
            email = currentUser.getEmailAddress()
            loggerApi.info("[PDD Template Export] Resolved current user email: $email")
        } else {
            loggerApi.warn("[PDD Template Export] currentUser is null")
        }
    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Exception while resolving current user email: ${e.getMessage()}")
    }

    return email
}
