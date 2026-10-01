let
    Source = Csv.Document(File.Contents(#"DataFolderPath" & "\Fact_POS_Transactions.csv"), [Delimiter=",", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"TransactionLineKey", Int64.Type},
        {"DateKey", Int64.Type},
        {"StoreKey", Int64.Type},
        {"ProductKey", Int64.Type},
        {"BasketID", type text},
        {"PaymentType", type text},
        {"UnitsSold", Int64.Type},
        {"GrossSalesAmt", type number},
        {"DiscountAmt", type number},
        {"NetSalesAmt", type number},
        {"ExtendedCostAmt", type number},
        {"TaxAmtAED", type number}
    })
in
    #"Changed Type"
