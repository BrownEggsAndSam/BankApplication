IF [Interface NPI] = 'Yes'
AND [Producer Confidentiality] = 'Confidential - Restricted'
AND [Consumer Confidentiality] = 'Confidential - Restricted'
AND [DSET NPI] IN ('NPI Dataset','NPI Dataset - SSN')
AND [Consumer NPI] = 'No'
THEN 'CRS PO - CRS Non NPI CC'

ELSEIF [Interface NPI] = 'Yes'
AND [Producer Confidentiality] = 'Confidential - Highly Restricted'
AND [Consumer Confidentiality] = 'Confidential - Restricted'
AND [Consumer NPI] = 'No'
THEN 'CHR PO - CRS Non NPI CC'

ELSEIF [Interface NPI] = 'Yes'
AND [Producer Confidentiality] = 'Confidential - Highly Restricted'
AND [Consumer Confidentiality] = 'Confidential - Restricted'
AND [DSET Confidentiality] = 'CHR - Confidential Highly Restricted'
AND [Consumer NPI] = 'Yes'
THEN 'CHR PO - CRS NPI CC'

ELSEIF [Interface NPI] = 'Yes'
AND [Producer Confidentiality] = 'Confidential - Highly Restricted'
AND [Consumer Confidentiality] = 'Confidential - Internal Distribution'
THEN 'CHR PO - CIN Non NPI'

ELSEIF [Interface NPI] = 'Yes'
AND [Producer Confidentiality] = 'Confidential - Restricted'
AND [Consumer Confidentiality] = 'Confidential - Internal Distribution'
THEN 'CRS PO - CIN Non NPI'

ELSE 'Other'
END
