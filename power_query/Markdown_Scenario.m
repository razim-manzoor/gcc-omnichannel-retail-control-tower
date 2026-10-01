let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "\Markdown_Scenario.csv"), [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"ScenarioDiscountPct", type number},
        {"DiscountDisplayLabel", type text},
        {"SimulationSortOrder", Int64.Type}
    })
in
    #"Changed Type"
