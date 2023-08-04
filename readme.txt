Sub MergeRowsBasedOnID()
    Dim r As Range
    Dim rng As Range
    Dim ws As Worksheet
    Dim dict As Object
    Dim arr As Variant
    Dim i As Long
    Dim temp As String
    Dim key As Variant
    
    ' Define the worksheet
    Set ws = ThisWorkbook.Sheets("Sheet1")  ' Change to your sheet name
    ' Define your range
    Set rng = ws.Range("A1:B3")  ' Change to your range
    
    ' Create a dictionary
    Set dict = CreateObject("Scripting.Dictionary")
    dict.CompareMode = 1  ' Make it case-insensitive
    
    arr = rng.Value  ' Get all values at once into an array
    For i = 1 To UBound(arr, 1)
        ' Concatenate values for each key
        dict(arr(i, 1)) = dict(arr(i, 1)) & ", " & arr(i, 2)
    Next i
    
    ' Loop through all keys in the dictionary and write back to the worksheet
    i = 1  ' Start from the first row
    For Each key In dict.keys
        ' Remove leading comma and space
        temp = Mid(dict(key), 3)
        ' Write back to the worksheet
        ws.Cells(i, 1).Value = key
        ws.Cells(i, 2).Value = temp
        i = i + 1
    Next key
    
    ' Clean up
    Set dict = Nothing
End Sub
