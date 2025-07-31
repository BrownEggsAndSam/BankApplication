String initiatorId = execution.getVariable("initiator")
String registeredByEmail = ""

if (initiatorId) {
    try {
        def foundUsers = userApi.findUsers(
            com.collibra.dgc.core.api.dto.instance.user.FindUsersRequest.builder()
                .username(initiatorId)
                .build()
        ).getResults()

        if (!foundUsers.isEmpty()) {
            def initiatorUser = foundUsers[0]
            registeredByEmail = initiatorUser?.getEmailAddress() ?: ""
            loggerApi.info("[PDD Template Export] Resolved initiator email: ${registeredByEmail}")
        } else {
            loggerApi.warn("[PDD Template Export] No user found with username: ${initiatorId}")
        }

    } catch (Exception e) {
        loggerApi.error("[PDD Template Export] Failed to get initiator email from username ${initiatorId}: ${e.message}")
    }
} else {
    loggerApi.warn("[PDD Template Export] 'initiator' variable is null or missing")
}
