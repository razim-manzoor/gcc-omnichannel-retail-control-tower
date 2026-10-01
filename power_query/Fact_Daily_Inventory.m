let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "\Fact_Daily_Inventory.csv"), [Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"InventorySnapshotKey", Int64.Type},
        {"SnapshotDateKey", Int64.Type},
        {"StoreKey", Int64.Type},
        {"ProductKey", Int64.Type},
        {"OnHandUnits", Int64.Type},
        {"InTransitUnits", Int64.Type},
        {"ReservedUnits", Int64.Type},
        {"AvailableUnits", Int64.Type},
        {"UnitCostSnapshotAmt", type number},
        {"InventoryCostValueAmt", type number}
    })
in
    #"Changed Type"
