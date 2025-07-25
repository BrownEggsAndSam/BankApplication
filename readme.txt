User initiator = execution.getVariable("user$initiator")
String registeredBy = initiator?.getEmailAddress() ?: ""

Cell mdRegisteredByCell = mdRow.createCell(mdHeaderMap.get("Registered By"))
mdRegisteredByCell.setCellValue(registeredBy)

if (registeredBy.trim().isEmpty()) {
    mdRegisteredByCell.setCellStyle(infoNeededCellStyle)
}
