-- =============================================
-- Medium-Sized Store Database (Oracle)
-- Tables: Products, Categories, Customers,
--         Bills, BillItems, Suppliers
-- =============================================

DROP TABLE BillItems;
DROP TABLE Bills;
DROP TABLE Customers;
DROP TABLE Products;
DROP TABLE Categories;
DROP TABLE Suppliers;

-- 2. Categories
CREATE TABLE Categories (
  CategoryID   NUMBER(4)     PRIMARY KEY,
  CategoryName VARCHAR2(50)  NOT NULL
);

-- 6. Suppliers
CREATE TABLE Suppliers (
  SupplierID   NUMBER(4)     PRIMARY KEY,
  SupplierName VARCHAR2(100) NOT NULL,
  Phone        VARCHAR2(15)
);

-- 1. Products (FK to Categories and Suppliers)
CREATE TABLE Products (
  ProductID   NUMBER(4)     PRIMARY KEY,
  ProductName VARCHAR2(100) NOT NULL,
  CategoryID  NUMBER(4)     REFERENCES Categories(CategoryID),
  SupplierID  NUMBER(4)     REFERENCES Suppliers(SupplierID),
  Price       NUMBER(10,2)  NOT NULL,
  Stock       NUMBER(4)     DEFAULT 0
);

-- 3. Customers
CREATE TABLE Customers (
  CustomerID   NUMBER(4)     PRIMARY KEY,
  CustomerName VARCHAR2(100) NOT NULL,
  Phone        VARCHAR2(15)
);

-- 4. Bills (FK to Customers)
CREATE TABLE Bills (
  BillID      NUMBER(4)     PRIMARY KEY,
  CustomerID  NUMBER(4)     REFERENCES Customers(CustomerID),
  BillDate    DATE          DEFAULT SYSDATE,
  TotalAmount NUMBER(10,2)  DEFAULT 0
);

-- 5. BillItems (FK to Bills and Products)
CREATE TABLE BillItems (
  ItemID    NUMBER(4)    PRIMARY KEY,
  BillID    NUMBER(4)    REFERENCES Bills(BillID),
  ProductID NUMBER(4)    REFERENCES Products(ProductID),
  Quantity  NUMBER(4)    NOT NULL,
  Price     NUMBER(10,2) NOT NULL
);

-- =============================================
-- Trigger: Auto-calculate Bills.TotalAmount
-- from BillItems (Price * Quantity)
-- =============================================

CREATE OR REPLACE TRIGGER TRG_BILL_TOTAL
AFTER INSERT OR UPDATE OR DELETE ON BillItems
DECLARE
  CURSOR c_bills IS
    SELECT DISTINCT BillID FROM BillItems;
BEGIN
  FOR r IN c_bills LOOP
    UPDATE Bills
       SET TotalAmount = (SELECT NVL(SUM(Price * Quantity), 0)
                          FROM BillItems
                          WHERE BillID = r.BillID)
     WHERE BillID = r.BillID;
  END LOOP;
END;
/

-- =============================================
-- Sample Data
-- =============================================

INSERT INTO Categories VALUES (1, 'Grocery');
INSERT INTO Categories VALUES (2, 'Beverages');
INSERT INTO Categories VALUES (3, 'Snacks');
INSERT INTO Categories VALUES (4, 'Dairy');
INSERT INTO Categories VALUES (5, 'Personal Care');

INSERT INTO Suppliers VALUES (1, 'Bharat Wholesale', '9822012345');
INSERT INTO Suppliers VALUES (2, 'Fresh Foods Co.', '9923045678');

INSERT INTO Products VALUES (101, 'Basmati Rice 5kg', 1, 1, 550.00, 40);
INSERT INTO Products VALUES (102, 'Coca Cola 750ml', 2, 1, 45.00, 120);
INSERT INTO Products VALUES (103, 'Potato Chips', 3, 2, 20.00, 200);
INSERT INTO Products VALUES (104, 'Amul Milk 500ml', 4, 2, 26.00, 80);
INSERT INTO Products VALUES (105, 'Toothpaste 100g', 5, 1, 65.00, 60);

INSERT INTO Customers VALUES (1, 'Rahul Sharma', '9812345678');
INSERT INTO Customers VALUES (2, 'Priya Patel', '9823456789');
INSERT INTO Customers VALUES (3, 'Amit Verma', '9834567890');

-- TotalAmount starts at 0; trigger fills it from BillItems
INSERT INTO Bills VALUES (1001, 1, TO_DATE('01-08-2026','DD-MM-YYYY'), 0);
INSERT INTO Bills VALUES (1002, 2, TO_DATE('01-08-2026','DD-MM-YYYY'), 0);

INSERT INTO BillItems VALUES (1, 1001, 101, 1, 550.00);
INSERT INTO BillItems VALUES (2, 1001, 103, 2, 20.00);
INSERT INTO BillItems VALUES (3, 1001, 105, 1, 65.00);
INSERT INTO BillItems VALUES (4, 1002, 104, 2, 26.00);
INSERT INTO BillItems VALUES (5, 1002, 102, 1, 45.00);

COMMIT;

-- =============================================
-- Verification Queries
-- =============================================
SELECT table_name FROM user_tables ORDER BY table_name;
SELECT * FROM Products;
SELECT * FROM Bills;
-- Verify: TotalAmount must equal the sum of BillItems per bill
SELECT B.BillID, B.TotalAmount, SUM(I.Price * I.Quantity) AS SumOfItems
FROM Bills B JOIN BillItems I ON B.BillID = I.BillID
GROUP BY B.BillID, B.TotalAmount;

EXIT;
