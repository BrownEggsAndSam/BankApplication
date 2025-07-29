String resolveRegisteredByEmail() {
    String email = ""

    try {
        loggerApi.info("[PDD Template Export] Attempting to resolve registeredBy email using getCurrentUser()")

        def user = userApi.getCurrentUser()
        user.ifPresent { currentUser ->
            loggerApi.info("[PDD Template Export] Retrieved user object: $currentUser")
            email = currentUser.getEmailAddress()
            loggerApi.info("[PDD Template Export] Retrieved user email: $email")
        }

    } catch (Exception e) {
        loggerApi.warn("[PDD Template Export] Exception occurred while resolving registeredByEmail: ${e.getMessage()}")
    }

    return email ?: ""
}
