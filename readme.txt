IF [Interface NPI] = 'Yes'
AND [Producer Confidentiality] = 'Confidential - Restricted'
AND [Consumer Confidentiality] = 'Confidential - Restricted'
AND [Consumer NPI] = 'No'
AND (
    CONTAINS([Interface NPI Type], "Bank/Financial Account")
 OR CONTAINS([Interface NPI Type], "Credit Card")
 OR CONTAINS([Interface NPI Type], "Driver's License")
 OR CONTAINS([Interface NPI Type], "Passport")
 OR CONTAINS([Interface NPI Type], "SSN")
 OR CONTAINS([Interface NPI Type], "Highly Sensitive Algorithm/ & @ Model")
 OR CONTAINS([Interface NPI Type], "Highly Sensitive Document")
 OR CONTAINS([Interface NPI Type], "Highly Sensitive Source Code")
 OR CONTAINS([Interface NPI Type], "Other NPI")
)
THEN 'Legacy CRS Producer Asset with NPI Interface'

ELSEIF [Interface NPI] = 'Yes'
AND [Producer Confidentiality] = 'Confidential - Highly Restricted'
AND ([Consumer Confidentiality] = 'Confidential - Restricted'
  OR [Consumer Confidentiality] = 'Confidential - Internal Distribuition')
AND [Consumer NPI] = 'No'
THEN 'CHR NPI Producer - CRS/CIN Non-NPI Consumer'

ELSEIF [Interface NPI] = 'Yes'
AND [Producer Confidentiality] = 'Confidential - Highly Restricted'
AND [Consumer Confidentiality] = 'Confidential - Restricted'
AND [Consumer NPI] = 'Yes'
AND (
    CONTAINS([Interface NPI Type], "SSN")
 OR CONTAINS([Interface NPI Type], "Highly Sensitive Algorithm/ & @ Model")
 OR CONTAINS([Interface NPI Type], "Highly Sensitive Document")
 OR CONTAINS([Interface NPI Type], "Highly Sensitive Source Code")
 OR CONTAINS([Interface NPI Type], "Other NPI")
)
THEN 'CHR NPI Producer - CRS NPI Consumer'

ELSE 'Other'
END

