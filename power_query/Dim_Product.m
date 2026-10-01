let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "\Dim_Product.csv"), [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"ProductKey", Int64.Type},
        {"SKU", type text},
        {"ProductName", type text},
        {"Department", type text},
        {"Category", type text},
        {"SubCategory", type text},
        {"Brand", type text},
        {"BrandTier", type text},
        {"BaseUnitCostAED", type number},
        {"BaseRetailPriceAED", type number},
        {"ElasticityCoefficient", type number}
    })
in
    #"Changed Type"
