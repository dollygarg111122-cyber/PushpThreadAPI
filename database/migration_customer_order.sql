IF COL_LENGTH('ProductSizeMapping', 'AvailableQuantity') IS NULL
BEGIN
    EXEC(N'ALTER TABLE ProductSizeMapping ADD AvailableQuantity int NOT NULL CONSTRAINT DF_ProductSizeMapping_AvailableQuantity DEFAULT 1');
END;

IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE name = 'CK_ProductSizeMapping_AvailableQuantity'
)
BEGIN
    EXEC(N'ALTER TABLE ProductSizeMapping ADD CONSTRAINT CK_ProductSizeMapping_AvailableQuantity CHECK (AvailableQuantity >= 0)');
END;

IF OBJECT_ID('CustomerOrder', 'U') IS NULL
BEGIN
    EXEC(N'CREATE TABLE CustomerOrder (
        ID int IDENTITY(1,1) NOT NULL CONSTRAINT PK_CustomerOrder PRIMARY KEY,
        CustomerName nvarchar(100) NOT NULL,
        PhoneNo nvarchar(15) NOT NULL,
        ProductID int NOT NULL,
        SizeID int NOT NULL,
        [Date] datetime NOT NULL CONSTRAINT DF_CustomerOrder_Date DEFAULT GETDATE(),
        CONSTRAINT FK_CustomerOrder_Product FOREIGN KEY (ProductID) REFERENCES Product (id),
        CONSTRAINT FK_CustomerOrder_Size FOREIGN KEY (SizeID) REFERENCES ProductSizeMaster (ID)
    )');
END;