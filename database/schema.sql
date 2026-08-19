CREATE TABLE ProductSupplier (
    ID int IDENTITY(1,1) NOT NULL CONSTRAINT PK_ProductSupplier PRIMARY KEY,
    Name nvarchar(100) NOT NULL,
    Address nvarchar(255) NULL,
    PhoneNo nvarchar(15) NULL
);

CREATE TABLE ProductSizeMaster (
    ID int IDENTITY(1,1) NOT NULL CONSTRAINT PK_ProductSizeMaster PRIMARY KEY,
    Size nvarchar(50) NOT NULL CONSTRAINT UQ_ProductSizeMaster_Size UNIQUE
);

CREATE TABLE Product (
    id int IDENTITY(1,1) NOT NULL CONSTRAINT PK_Product PRIMARY KEY,
    name nvarchar(100) NOT NULL,
    price decimal(18,2) NOT NULL,
    description nvarchar(max) NULL,
    image nvarchar(255) NULL,
    SupplierId int NOT NULL,
    CONSTRAINT FK_Product_ProductSupplier FOREIGN KEY (SupplierId)
        REFERENCES ProductSupplier (ID)
);

CREATE TABLE ProductSizeMapping (
    ID int IDENTITY(1,1) NOT NULL CONSTRAINT PK_ProductSizeMapping PRIMARY KEY,
    ProductId int NOT NULL,
    SizeID int NOT NULL,
    AvailableQuantity int NOT NULL CONSTRAINT DF_ProductSizeMapping_AvailableQuantity DEFAULT 1,
    CONSTRAINT CK_ProductSizeMapping_AvailableQuantity CHECK (AvailableQuantity >= 0),
    CONSTRAINT UQ_ProductSizeMapping_Product_Size UNIQUE (ProductId, SizeID),
    CONSTRAINT FK_ProductSizeMapping_Product FOREIGN KEY (ProductId)
        REFERENCES Product (id),
    CONSTRAINT FK_ProductSizeMapping_Size FOREIGN KEY (SizeID)
        REFERENCES ProductSizeMaster (ID)
);

CREATE TABLE CustomerOrder (
    ID int IDENTITY(1,1) NOT NULL CONSTRAINT PK_CustomerOrder PRIMARY KEY,
    CustomerName nvarchar(100) NOT NULL,
    PhoneNo nvarchar(15) NOT NULL,
    ProductID int NOT NULL,
    SizeID int NOT NULL,
    [Date] datetime NOT NULL CONSTRAINT DF_CustomerOrder_Date DEFAULT GETDATE(),
    CONSTRAINT FK_CustomerOrder_Product FOREIGN KEY (ProductID) REFERENCES Product (id),
    CONSTRAINT FK_CustomerOrder_Size FOREIGN KEY (SizeID) REFERENCES ProductSizeMaster (ID)
);