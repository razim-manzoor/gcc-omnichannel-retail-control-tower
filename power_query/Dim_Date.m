let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "\Dim_Date.csv"), [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"DateKey", Int64.Type},
        {"FullDate", type date},
        {"FiscalYear", Int64.Type},
        {"FiscalQuarter", type text},
        {"FiscalMonthNum", Int64.Type},
        {"FiscalMonthName", type text},
        {"RetailWeekNum", Int64.Type},
        {"DayOfWeekName", type text},
        {"DayOfWeekNum", Int64.Type},
        {"IsWeekendGCC", type logical},
        {"IsRetailPeakSeason", type logical}
    })
in
    #"Changed Type"
