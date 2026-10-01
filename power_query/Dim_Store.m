let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "\Dim_Store.csv"), [Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"StoreKey", Int64.Type},
        {"StoreCode", type text},
        {"StoreName", type text},
        {"Channel", type text},
        {"Emirate", type text},
        {"Country", type text},
        {"GrossLeasableAreaSqFt", Int64.Type},
        {"ClusterTier", type text},
        {"HubFulfillmentEligible", type logical}
    })
in
    #"Changed Type"
