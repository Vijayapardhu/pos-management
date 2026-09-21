# Medium-Sized Store Database (DMS Project)

An Oracle database for a medium-sized retail store — 6 tables, sample data,
auto-calculated bill totals via a trigger, and a formatted bill receipt printer.
Built and tested with SQL\*Plus (Oracle 26ai Free).

---

## 1. Database Design

```
Categories (1) ───< Products >─── (1) Suppliers
                      │
                      │
                 BillItems
                      │
                      ▼
Customers (1) ───< Bills
```

| Table      | Purpose                          | Key Relationships                              |
| ---------- | -------------------------------- | ---------------------------------------------- |
| Products   | Store items                      | CategoryID → Categories, SupplierID → Suppliers |
| Categories | Organize products                |                                                |
| Suppliers  | Who supplies the products        |                                                |
| Customers  | Buyer details                    |                                                |
| Bills      | Each purchase                    | CustomerID → Customers                         |
| BillItems  | Products included in each bill   | BillID → Bills, ProductID → Products           |

---

## 2. How the Tables Were Created (DDL explained)

Oracle types are used (`NUMBER` / `VARCHAR2` instead of `INT` / `VARCHAR`).
Parent tables are created **first**, children last, so foreign keys can
reference tables that already exist.

```sql
-- 2. Categories (no dependencies)
CREATE TABLE Categories (
  CategoryID   NUMBER(4)     PRIMARY KEY,        -- PK: unique, not null
  CategoryName VARCHAR2(50)  NOT NULL
);

-- 6. Suppliers (no dependencies)
CREATE TABLE Suppliers (
  SupplierID   NUMBER(4)     PRIMARY KEY,
  SupplierName VARCHAR2(100) NOT NULL,
  Phone        VARCHAR2(15)
);

-- 1. Products (child of Categories and Suppliers)
CREATE TABLE Products (
  ProductID   NUMBER(4)     PRIMARY KEY,
  ProductName VARCHAR2(100) NOT NULL,
  CategoryID  NUMBER(4)     REFERENCES Categories(CategoryID),  -- FK
  SupplierID  NUMBER(4)     REFERENCES Suppliers(SupplierID),    -- FK
  Price       NUMBER(10,2)  NOT NULL,   -- up to 8 digits, 2 decimals
  Stock       NUMBER(4)     DEFAULT 0
);

-- 3. Customers (no dependencies)
CREATE TABLE Customers (
  CustomerID   NUMBER(4)     PRIMARY KEY,
  CustomerName VARCHAR2(100) NOT NULL,
  Phone        VARCHAR2(15)
);

-- 4. Bills (child of Customers)
CREATE TABLE Bills (
  BillID      NUMBER(4)     PRIMARY KEY,
  CustomerID  NUMBER(4)     REFERENCES Customers(CustomerID),  -- FK
  BillDate    DATE          DEFAULT SYSDATE,
  TotalAmount NUMBER(10,2)  DEFAULT 0     -- filled by trigger, never typed by hand
);

-- 5. BillItems (child of Bills and Products)
CREATE TABLE BillItems (
  ItemID    NUMBER(4)    PRIMARY KEY,
  BillID    NUMBER(4)    REFERENCES Bills(BillID),     -- FK
  ProductID NUMBER(4)    REFERENCES Products(ProductID), -- FK
  Quantity  NUMBER(4)    NOT NULL,
  Price     NUMBER(10,2) NOT NULL    -- price at the time of sale
);
```

**Key points**

- `PRIMARY KEY` = unique + not null; every row is identified by it.
- `REFERENCES` = foreign key; Oracle **rejects** inserts/deletes that break
  the link (e.g., a `Product` whose `CategoryID` doesn't exist, or deleting a
  `Customer` who already has `Bills`).
- Drop order is the reverse (children first): in `store_database.sql` the
  `DROP TABLE` statements run `BillItems` → `Bills` → `Customers` → `Products`
  → `Categories` → `Suppliers`.
- `BillItems.Price` stores the price **at sale time**, separate from
  `Products.Price`, so old bills don't change when you reprice a product.

---

## 3. Files

| File                 | Purpose                                            |
| -------------------- | -------------------------------------------------- |
| `store_database.sql` | Drops old tables, creates all 6, creates trigger, loads sample data, runs verification queries |
| `bill_script.sql`    | Prints a formatted bill receipt for any BillID     |
| `README.md`          | This document                                      |

---

## 4. Prerequisites

- Oracle installed (SQL\*Plus on PATH)
- User `System`, password `aditya`

---

## 5. How to Run

All commands are run directly in SQL\*Plus.

### Step 1 — Create the database (run once, or anytime to reset)

```powershell
sqlplus -S System/aditya "@C:\college\DMS\projects\store_database.sql"
```

What it does, in order:

1. **Drop** all 6 tables (children first, to satisfy FK constraints).
2. **Create** the 6 tables as in Section 2.
3. **Create trigger** `TRG_BILL_TOTAL` (see Section 6).
4. **Insert sample data** — 5 categories, 2 suppliers, 5 products, 3 customers,
   2 bills (with `TotalAmount = 0` — the trigger fills it), 5 bill items.
5. **Verify** — lists tables and prints `Products`, `Bills`, plus a check query
   proving `TotalAmount = SUM(Price × Quantity)` per bill.

### Step 2 — Print a bill receipt

```powershell
sqlplus -S System/aditya "@C:\college\DMS\projects\bill_script.sql" 1001
```

Replace `1001` with any `BillID`. Output looks like:

```
======================================================
                    SHREE MART
                 Retail Store Bill
======================================================

Bill No   : 1001
Date      : 01-AUG-2026
Customer  : Rahul Sharma  (9812345678)

-----------------------------------------------------

PRODUCT             QTY  PRICE   AMOUNT
Basmati Rice 5kg      1 550.00   550.00
Potato Chips          2  20.00    40.00
Toothpaste 100g       1  65.00    65.00
                                ----------
GRAND TOTAL                      655.00

------------------------------------------------------
            Thank you for shopping!
          *** Visit Again ***
```

---

## 6. How the Trigger Works

`TRG_BILL_TOTAL` is a **statement-level** trigger on `BillItems`:

```sql
AFTER INSERT OR UPDATE OR DELETE ON BillItems
```

- Fires **once per statement** (not per row), so it is allowed to re-query
  `BillItems` — a row-level trigger fails here with
  `ORA-04091: mutating table`.
- After any change, it loops over every `BillID` that appears in `BillItems`,
  computes `SUM(Price * Quantity)`, and updates `Bills.TotalAmount`.

**Result:** you never type a total by hand. Insert/update/delete a line item
and the bill's `TotalAmount` stays correct automatically.

---

## 7. Basic Operations (CRUD)

Run these directly at the SQL\*Plus `SQL>` prompt, or save them in a `.sql`
file and run with `@filename`. Always `COMMIT;` after changes, or `ROLLBACK;`
to undo.

### 7.1 Add a product

```sql
INSERT INTO Products (ProductID, ProductName, CategoryID, SupplierID, Price, Stock)
VALUES (106, 'Aashirvaad Atta 10kg', 1, 1, 380.00, 25);
COMMIT;
```

### 7.2 View products

```sql
SELECT * FROM Products;                                    -- everything
SELECT ProductName, Price, Stock FROM Products;            -- only some columns
SELECT ProductName, Price FROM Products WHERE Price > 100; -- filter
SELECT ProductName, Price FROM Products ORDER BY Price DESC; -- cheapest to costliest
```

### 7.3 Update a product (price or stock)

```sql
UPDATE Products SET Price = 560.00 WHERE ProductID = 101;  -- reprice
UPDATE Products SET Stock = Stock - 3 WHERE ProductID = 102; -- stock went down
UPDATE Products SET Price = 400.00, Stock = 20 WHERE ProductID = 106;
COMMIT;
```

### 7.4 Remove a product

```sql
DELETE FROM Products WHERE ProductID = 106;
COMMIT;
```

**Careful:** deleting a product that appears in `BillItems` fails with a
foreign-key error (`ORA-02292`). Old bills must stay intact, so you cannot
delete it — instead reduce stock to 0, or delete its `BillItems` rows first.

### 7.5 Categories and Suppliers (same pattern)

```sql
INSERT INTO Categories VALUES (6, 'Bakery');                          -- add
UPDATE Categories SET CategoryName = 'Bakery & Bread' WHERE CategoryID = 6;
DELETE FROM Categories WHERE CategoryID = 6;                          -- remove
SELECT * FROM Categories;
```

A category that still has products cannot be deleted (FK rule). The same
applies to `Suppliers` — and deleting a supplier also fails if products
reference it.

### 7.6 Customers (same pattern)

```sql
INSERT INTO Customers VALUES (4, 'Sneha Gupta', '9845098450');
UPDATE Customers SET Phone = '9855098550' WHERE CustomerID = 4;
DELETE FROM Customers WHERE CustomerID = 4;
SELECT * FROM Customers;
```

A customer who already has bills cannot be deleted until those bills are
removed first.

### 7.7 Sell to a customer (new bill + items)

```sql
INSERT INTO Bills (BillID, CustomerID, BillDate) VALUES (1003, 3, SYSDATE);
INSERT INTO BillItems (ItemID, BillID, ProductID, Quantity, Price)
VALUES (6, 1003, 101, 2, 550.00);
INSERT INTO BillItems (ItemID, BillID, ProductID, Quantity, Price)
VALUES (7, 1003, 102, 3, 45.00);
COMMIT;
```

After these inserts the trigger sets `Bills.TotalAmount` for bill 1003 to
1235.00 automatically. Print it with `@bill_script.sql 1003`.

### 7.8 Change an item on an existing bill

```sql
UPDATE BillItems SET Quantity = 1 WHERE ItemID = 7;  -- total auto-updates
DELETE FROM BillItems WHERE ItemID = 7;              -- remove an item, total auto-updates
COMMIT;
```

### 7.9 Remove a whole bill (items first!)

```sql
DELETE FROM BillItems WHERE BillID = 1003;   -- child rows first
DELETE FROM Bills WHERE BillID = 1003;       -- then the bill itself
COMMIT;
```

### 7.10 Common report queries

```sql
-- Which products are low in stock?
SELECT * FROM Products WHERE Stock < 50;

-- All bills of one customer
SELECT * FROM Bills WHERE CustomerID = 1;

-- Products and the name of their category (join)
SELECT p.ProductName, c.CategoryName, p.Price
FROM Products p JOIN Categories c ON p.CategoryID = c.CategoryID;

-- Total sales per day
SELECT BillDate, SUM(TotalAmount) FROM Bills GROUP BY BillDate;

-- Best-selling products (by quantity)
SELECT p.ProductName, SUM(i.Quantity) AS Sold
FROM BillItems i JOIN Products p ON i.ProductID = p.ProductID
GROUP BY p.ProductName
ORDER BY Sold DESC;
```

---

## 8. Notes & Known Limits

- `TotalAmount` recomputes only for bills that still have items; deleting **all**
  items of a bill leaves its old total behind.
- Foreign keys are defined inline (`REFERENCES`); primary keys are column-level
  `PRIMARY KEY` constraints.
- All object names are uppercase by default (Oracle behavior).
- `Products.Stock` is not auto-decremented when you sell — the app is expected
  to `UPDATE Products SET Stock = Stock - 1 ...` when billing.
