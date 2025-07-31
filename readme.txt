import com.collibra.dgc.core.api.dto.instance.user.FindUsersRequest

String initiatorId = execution.getVariable("initiator")
String registeredByEmail = ""

if (initiatorId) {
    try {
        def foundUsers = userApi.findUsers(FindUsersRequest.builder()
            .username(initiatorId)
            .build()
        ).getResults()

        if (!foundUsers.isEmpty()) {
            registeredByEmail = foundUsers[0].email ?: ""
            loggerApi.info("[PDD Template Export] Setting Registered By: ${registeredByEmail}")
        } else {
            loggerApi.warn("[PDD Template Export] No user found with username: ${initiatorId}")
        }

    } catch (Exception e) {
        loggerApi.error("[PDD Template Export] Could not fetch initiator user by username ${initiatorId}: ${e.message}")
    }
} else {
    loggerApi.warn("[PDD Template Export] No initiator variable found")
}
