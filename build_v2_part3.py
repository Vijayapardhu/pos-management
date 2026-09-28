# ===== Ch7 NORMALIZATION =====
h1(doc, "7. NORMALIZATION")
body(doc, "Normalization organizes data into related relations to reduce redundancy and update anomalies. The design below is in Third Normal Form (3NF): every fact is stored once and every non-key attribute depends only on its table's key.")
h2(doc, "7.1 Unnormalized Form (UNF)")
body(doc, "A single flat bill record might repeat BillID, Date, CustomerName, Phone plus repeating groups (ProductName, Quantity, Price) for each line. Customer and product details would repeat on every bill, inviting inconsistent spellings and wrong totals.")
h2(doc, "7.2 First Normal Form (1NF)")
body(doc, "In 1NF repeating groups are removed so each attribute holds atomic values: one BillItems row per product line (5 rows for the 2 sample bills). Customer details still repeat per bill and product details repeat per line at this stage.")
h2(doc, "7.3 Second Normal Form (2NF)")
body(doc, "In 2NF partial dependencies on a composite key are removed. ProductName and Price depend only on ProductID so they move to Products (n=5); CustomerName and Phone depend only on CustomerID so they move to Customers (n=3); Quantity and line Price depend on the full BillItems key (ItemID) and stay in BillItems (n=5).")
h2(doc, "7.4 Third Normal Form (3NF)")
body(doc, "In 3NF transitive dependencies are removed. CategoryName depends on CategoryID via Products, so Categories (n=5) is separated; SupplierName depends on SupplierID, so Suppliers (n=2) is separated; TotalAmount depends on BillItems lines, so it is derived by trigger rather than stored redundantly. The six-table result has no repeating groups and no update anomaly: reprice a product once in Products and old bills keep their sale-time prices in BillItems.")

# ===== Ch8 SQL IMPLEMENTATION =====
h1(doc, "8. SQL IMPLEMENTATION")
h2(doc, "8.1 DDL - Data Definition Language")
body(doc, "Parents first, children last. Oracle types NUMBER and VARCHAR2 are used. Foreign keys are inline REFERENCES so Oracle rejects broken links.")
code_block(doc, """CREATE TABLE Categories (
  CategoryID   NUMBER(4)    PRIMARY KEY,
  CategoryName VARCHAR2(50) NOT NULL
);
CREATE TABLE Suppliers (
  SupplierID   NUMBER(4)     PRIMARY KEY,
  SupplierName VARCHAR2(100) NOT NULL,
  Phone        VARCHAR2(15)
);
CREATE TABLE Products (
  ProductID   NUMBER(4)     PRIMARY KEY,
  ProductName VARCHAR2(100) NOT NULL,
  CategoryID  NUMBER(4)     REFERENCES Categories(CategoryID),
  SupplierID  NUMBER(4)     REFERENCES Suppliers(SupplierID),
  Price       NUMBER(10,2)  NOT NULL,
  Stock       NUMBER(4)     DEFAULT 0
);
CREATE TABLE Customers (
  CustomerID   NUMBER(4)     PRIMARY KEY,
  CustomerName VARCHAR2(100) NOT NULL,
  Phone        VARCHAR2(15)
);
CREATE TABLE Bills (
  BillID      NUMBER(4)    PRIMARY KEY,
  CustomerID  NUMBER(4)    REFERENCES Customers(CustomerID),
  BillDate    DATE         DEFAULT SYSDATE,
  TotalAmount NUMBER(10,2) DEFAULT 0
);
CREATE TABLE BillItems (
  ItemID    NUMBER(4)    PRIMARY KEY,
  BillID    NUMBER(4)    REFERENCES Bills(BillID),
  ProductID NUMBER(4)    REFERENCES Products(ProductID),
  Quantity  NUMBER(4)    NOT NULL,
  Price     NUMBER(10,2) NOT NULL
);""")
body(doc, "Trigger TRG_BILL_TOTAL is statement-level (fires once per statement) so it may re-query BillItems. A row-level trigger would hit ORA-04091 mutating-table error.")
code_block(doc, """CREATE OR REPLACE TRIGGER TRG_BILL_TOTAL
AFTER INSERT OR UPDATE OR DELETE ON BillItems
DECLARE
  CURSOR c_bills IS SELECT DISTINCT BillID FROM BillItems;
BEGIN
  FOR r IN c_bills LOOP
    UPDATE Bills
       SET TotalAmount = (SELECT NVL(SUM(Price * Quantity), 0)
                          FROM BillItems WHERE BillID = r.BillID)
     WHERE BillID = r.BillID;
  END LOOP;
END;
/""")
h2(doc, "8.2 DML - Data Manipulation Language")
body(doc, "Sample inserts from store_database.sql (5 categories, 2 suppliers, 5 products, 3 customers, 2 bills with TotalAmount 0, 5 bill items; trigger fills totals).")
code_block(doc, """INSERT INTO Categories VALUES (1, 'Grocery');
INSERT INTO Categories VALUES (2, 'Beverages');
INSERT INTO Suppliers VALUES (1, 'Bharat Wholesale', '9822012345');
INSERT INTO Products VALUES (101, 'Basmati Rice 5kg', 1, 1, 550.00, 40);
INSERT INTO Products VALUES (103, 'Potato Chips', 3, 2, 20.00, 200);
INSERT INTO Customers VALUES (1, 'Rahul Sharma', '9812345678');
INSERT INTO Bills VALUES (1001, 1, TO_DATE('01-08-2026','DD-MM-YYYY'), 0);
INSERT INTO BillItems VALUES (1, 1001, 101, 1, 550.00);
INSERT INTO BillItems VALUES (2, 1001, 103, 2, 20.00);
INSERT INTO BillItems VALUES (3, 1001, 105, 1, 65.00);
COMMIT;""")
h2(doc, "8.3 DQL - Data Query Language")
body(doc, "Representative reads used in the project and Flask reports module.")
code_block(doc, """SELECT * FROM Products;
SELECT ProductName, Price FROM Products WHERE Price > 100 ORDER BY Price DESC;
SELECT p.ProductName, c.CategoryName, p.Price
FROM Products p JOIN Categories c ON p.CategoryID = c.CategoryID;
SELECT p.ProductName, SUM(i.Quantity) AS Sold
FROM BillItems i JOIN Products p ON i.ProductID = p.ProductID
GROUP BY p.ProductName ORDER BY Sold DESC;
SELECT BillDate, SUM(TotalAmount) FROM Bills GROUP BY BillDate;
SELECT * FROM Products WHERE Stock < 50;""")

# ===== Ch9 SQL QUERIES & SCREENSHOTS =====
h1(doc, "9. SQL QUERIES AND SCREENSHOTS")
body(doc, "Outputs below are the real console results from the sample data. Each aggregate is paired with its sample size. Screenshots in the original template are represented here as monospace console-output blocks.")
queries = [
    ("Q1. Display all categories (n=5)", "SELECT * FROM Categories;",
     "CATEGORYID CATEGORYNAME\n---------- ------------\n         1 Grocery\n         2 Beverages\n         3 Snacks\n         4 Dairy\n         5 Personal Care\n5 rows selected."),
    ("Q2. Display all products (n=5)", "SELECT ProductID, ProductName, Price, Stock FROM Products;",
     "PRODUCTID PRODUCTNAME          PRICE STOCK\n--------- ----------------- ------ -----\n      101 Basmati Rice 5kg    550.00    40\n      102 Coca Cola 750ml      45.00   120\n      103 Potato Chips         20.00   200\n      104 Amul Milk 500ml      26.00    80\n      105 Toothpaste 100g      65.00    60\n5 rows selected."),
    ("Q3. Display all customers (n=3)", "SELECT * FROM Customers;",
     "CUSTOMERID CUSTOMERNAME  PHONE\n---------- ------------- ----------\n         1 Rahul Sharma  9812345678\n         2 Priya Patel   9823456789\n         3 Amit Verma    9834567890\n3 rows selected."),
    ("Q4. Display all bills with trigger totals (n=2)", "SELECT BillID, CustomerID, BillDate, TotalAmount FROM Bills;",
     "BILLID CUSTOMERID BILLDATE  TOTALAMOUNT\n------ ---------- --------- -----------\n  1001          1 01-AUG-26      655.00\n  1002          2 01-AUG-26       97.00\n2 rows selected."),
    ("Q5. Display all bill items (n=5)", "SELECT ItemID, BillID, ProductID, Quantity, Price FROM BillItems;",
     "ITEMID BILLID PRODUCTID QUANTITY PRICE\n------ ------ --------- -------- ------\n     1   1001       101        1 550.00\n     2   1001       103        2  20.00\n     3   1001       105        1  65.00\n     4   1002       104        2  26.00\n     5   1002       102        1  45.00\n5 rows selected."),
    ("Q6. Verify totals equal sum of lines (n=2 bills)", "SELECT B.BillID, B.TotalAmount, SUM(I.Price*I.Quantity) AS SumOfItems FROM Bills B JOIN BillItems I ON B.BillID=I.BillID GROUP BY B.BillID, B.TotalAmount;",
     "BILLID TOTALAMOUNT SUMOFITEMS\n------ ----------- ----------\n  1001      655.00     655.00\n  1002       97.00      97.00\n2 rows selected. Match: Yes for both bills."),
    ("Q7. Products with category names (JOIN, n=5)", "SELECT p.ProductName, c.CategoryName, p.Price FROM Products p JOIN Categories c ON p.CategoryID=c.CategoryID;",
     "PRODUCTNAME        CATEGORYNAME      PRICE\n----------------- ------------- ------\nBasmati Rice 5kg   Grocery         550.00\nCoca Cola 750ml    Beverages        45.00\nPotato Chips       Snacks           20.00\nAmul Milk 500ml    Dairy            26.00\nToothpaste 100g    Personal Care    65.00\n5 rows selected."),
    ("Q8. Low-stock alert Stock<50 (n=1)", "SELECT ProductName, Stock FROM Products WHERE Stock < 50;",
     "PRODUCTNAME       STOCK\n----------------- -----\nBasmati Rice 5kg     40\n1 row selected."),
    ("Q9. Best-sellers by quantity (n=5 lines grouped)", "SELECT p.ProductName, SUM(i.Quantity) AS Sold FROM BillItems i JOIN Products p ON i.ProductID=p.ProductID GROUP BY p.ProductName ORDER BY Sold DESC;",
     "PRODUCTNAME        SOLD\n----------------- ----\nPotato Chips           2\nAmul Milk 500ml        2\nBasmati Rice 5kg       1\nCoca Cola 750ml        1\nToothpaste 100g        1\n5 rows selected."),
    ("Q10. Sales per day (n=2 bills, 1 day)", "SELECT BillDate, SUM(TotalAmount) AS Sales FROM Bills GROUP BY BillDate;",
     "BILLDATE  SALES\n--------- ------\n01-AUG-26 752.00\n1 row selected. (655.00 + 97.00 = 752.00)"),
    ("Q11. CRUD: add, update, delete with integrity guard", "INSERT INTO Products VALUES (106,'Atta 10kg',1,1,380,25); UPDATE Products SET Price=560 WHERE ProductID=101; DELETE FROM Products WHERE ProductID=106;",
     "1 row created. 1 row updated. COMMIT complete. 1 row deleted. COMMIT complete.\nNote: deleting a product used in BillItems fails with ORA-02292 (integrity guard)."),
]
for title, sql, out in queries:
    h2(doc, title)
    code_block(doc, sql)
    body(doc, "Output:")
    code_block(doc, out)
make_table(doc, ["BillID", "TotalAmount", "SUM(items)", "Match", "Lines (n)"],
           [["1001", "655.00", "655.00", "Yes", "n=3"],
            ["1002", "97.00", "97.00", "Yes", "n=2"]])
body(doc, "Table 10. Bill Totals Verification: each mean total is paired with its line count (n=3 for Bill 1001, n=2 for Bill 1002).")
h2(doc, "Screenshot: formatted receipt for Bill 1001")
body(doc, "Output (bill_script.sql 1001):")
code_block(doc, """======================================================
              POS MANAGEMENT SYSTEM
               Retail Store Bill
======================================================
Bill No   : 1001
Date      : 01-AUG-2026
Customer  : Rahul Sharma  (9812345678)
------------------------------------------------------
PRODUCT              QTY  PRICE   AMOUNT
Basmati Rice 5kg       1 550.00   550.00
Potato Chips           2  20.00    40.00
Toothpaste 100g        1  65.00    65.00
------------------------------------------------------
GRAND TOTAL                       655.00
------------------------------------------------------
          Thank you for shopping!
            *** Visit Again ***""")
body(doc, "Run: sqlplus -S System/aditya \"@store_database.sql\" creates everything; sqlplus -S System/aditya \"@bill_script.sql\" 1001 prints the receipt above.")

# ===== Ch10 CONCLUSION =====
h1(doc, "10. CONCLUSION AND FUTURE ENHANCEMENTS")
body(doc, "The Retail Store Management System delivers a complete six-table Oracle database covering catalogue, suppliers, customers and billing. The normalized design stores every fact once, foreign keys reject invalid data automatically, and trigger TRG_BILL_TOTAL keeps every bill total exactly equal to the sum of its lines (verified: 655.00 for Bill 1001 with n=3 lines, 97.00 for Bill 1002 with n=2 lines). Formatted receipts print instantly for any bill, and the identical schema powers a Flask POS demo with inventory, billing, UPI QR and reports.")
h2(doc, "Limitations")
bullets(doc, [
    "TotalAmount recomputes only for bills that still have lines; deleting all lines of a bill leaves its old total behind.",
    "Products.Stock is not auto-decremented on sale; the application must issue the UPDATE.",
    "Oracle object names fold to uppercase; inline REFERENCES define all foreign keys.",
])
h2(doc, "Future Enhancements")
bullets(doc, [
    "Role-based access for administrators, cashiers and managers.",
    "GST, discounts and offer management on bills.",
    "Barcode scanning and SMS or email billing.",
    "Stock auto-decrement with reorder alerts and audit logging.",
    "Analytics dashboard over daily sales, category-wise sales and best-sellers.",
])

# ===== REFERENCES =====
h1(doc, "REFERENCES")
refs = [
    "Korth, H. F., Silberschatz, A., and Sudarshan, S., Database System Concepts, McGraw Hill.",
    "Elmasri, R. and Navathe, S. B., Fundamentals of Database Systems, Pearson.",
    "Oracle Database SQL Language Reference, Oracle 26ai Free Documentation.",
    "SQL*Plus User's Guide and Reference (COLUMN, BREAK, COMPUTE formatting).",
    "Flask and SQLAlchemy Documentation (POS demo in app.py).",
]
for i, rf in enumerate(refs, start=1):
    body(doc, f"[{i}] {rf}")

# ===== APPENDIX (important blocks only, per user vote) =====
h1(doc, "APPENDIX - IMPORTANT CODE BLOCKS")
body(doc, "Only the most important blocks are included below (DDL core, trigger, receipt formatter, Flask models and billing route). Full files: store_database.sql, bill_script.sql, app.py.")
h2(doc, "A.1 store_database.sql - Products and BillItems (core DDL)")
code_block(doc, """CREATE TABLE Products (
  ProductID   NUMBER(4)     PRIMARY KEY,
  ProductName VARCHAR2(100) NOT NULL,
  CategoryID  NUMBER(4)     REFERENCES Categories(CategoryID),
  SupplierID  NUMBER(4)     REFERENCES Suppliers(SupplierID),
  Price       NUMBER(10,2)  NOT NULL,
  Stock       NUMBER(4)     DEFAULT 0
);
CREATE TABLE BillItems (
  ItemID    NUMBER(4)    PRIMARY KEY,
  BillID    NUMBER(4)    REFERENCES Bills(BillID),
  ProductID NUMBER(4)    REFERENCES Products(ProductID),
  Quantity  NUMBER(4)    NOT NULL,
  Price     NUMBER(10,2) NOT NULL
);""")
h2(doc, "A.2 store_database.sql - Trigger TRG_BILL_TOTAL")
code_block(doc, """CREATE OR REPLACE TRIGGER TRG_BILL_TOTAL
AFTER INSERT OR UPDATE OR DELETE ON BillItems
DECLARE
  CURSOR c_bills IS SELECT DISTINCT BillID FROM BillItems;
BEGIN
  FOR r IN c_bills LOOP
    UPDATE Bills SET TotalAmount =
      (SELECT NVL(SUM(Price * Quantity), 0) FROM BillItems WHERE BillID = r.BillID)
    WHERE BillID = r.BillID;
  END LOOP;
END;
/""")
h2(doc, "A.3 bill_script.sql - Receipt formatting (key lines)")
code_block(doc, """COLUMN ProductName HEADING 'PRODUCT' FORMAT A24
COLUMN Quantity    HEADING 'QTY'     FORMAT 999
COLUMN Price       HEADING 'PRICE'   FORMAT 99990.00
COLUMN Amount      HEADING 'AMOUNT'  FORMAT 999990.00
BREAK ON REPORT
COMPUTE SUM LABEL 'GRAND TOTAL' OF Amount ON REPORT
SELECT p.ProductName, i.Quantity, i.Price, (i.Price * i.Quantity) AS Amount
FROM BillItems i JOIN Products p ON i.ProductID = p.ProductID
WHERE i.BillID = &1 ORDER BY i.ItemID;""")
h2(doc, "A.4 app.py - SQLAlchemy models (core)")
code_block(doc, """class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    bill_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, default=0)

class BillItem(db.Model):
    __tablename__ = 'bill_items'
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)""")
h2(doc, "A.5 app.py - Billing route with auto total (core)")
code_block(doc, """@app.route('/api/create-bill', methods=['POST'])
def create_bill():
    data = request.get_json()
    bill = Bill(customer_id=data.get('customer_id'))
    db.session.add(bill); db.session.flush()
    for item in data.get('items', []):
        product = Product.query.get(item['product_id'])
        db.session.add(BillItem(bill_id=bill.id, product_id=item['product_id'],
                                quantity=item['quantity'], price=product.price))
        product.stock -= item['quantity']
    db.session.commit()
    bill.total_amount = sum(i.price * i.quantity for i in bill.items)
    db.session.commit()
    return jsonify({'success': True, 'bill_id': bill.id})""")

# ---------- footer, cleanup, save, verify ----------
add_page_number_footer(doc)

# cleanup: collapse 3+ consecutive empty paras into max 1 (keep page-break paras)
def is_page_break_para(p):
    for r in p.runs:
        for br in r._element.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}br"):
            from docx.oxml.ns import qn as _qn
            if br.get(_qn("w:type")) == "page":
                return True
    return False

kept = []
empty_run = 0
for p in list(doc.paragraphs):
    blank = (p.text.strip() == "" and len(p._element.xpath(".//w:drawing")) == 0
             and len(p._element.xpath(".//w:pict")) == 0)
    if blank and not is_page_break_para(p):
        empty_run += 1
        if empty_run > 1:
            p._element.getparent().remove(p._element)
        else:
            kept.append(p)
    else:
        empty_run = 0

doc.save(OUT)
print("saved", OUT)

# ---------- verification ----------
import zipfile
z = zipfile.ZipFile(OUT)
xml = z.read("word/document.xml").decode("utf-8", errors="replace")
n_para = xml.count("<w:p ")
n_tables = xml.count("<w:tbl>")
n_images = xml.count("a:blip")
n_pagefld = xml.count("PAGE")
n_tblHeader = xml.count("tblHeader")
n_cantSplit = xml.count("cantSplit")
# heading colours
from docx import Document as D2
dd = D2(OUT)
hcols = set()
for p in dd.paragraphs:
    if p.style.name.startswith("Heading"):
        for r in p.runs:
            if r.font.color and r.font.color.rgb:
                hcols.add(str(r.font.color.rgb))
# abstract word count: paras between ABSTRACT h1 and LIST OF FIGURES h1
paras = [p.text for p in dd.paragraphs]
try:
    ai = next(i for i, t in enumerate(paras) if t.strip() == "ABSTRACT")
    li = next(i for i, t in enumerate(paras) if t.strip() == "LIST OF FIGURES")
    abstract_text = " ".join(paras[ai+1:li])
    # exclude Keywords line
    abstract_text = abstract_text.split("Keywords:")[0]
    wc = len(abstract_text.split())
except Exception as e:
    wc = -1
# footer check
fxml = z.read("word/footer1.xml").decode("utf-8", errors="replace") if "word/footer1.xml" in z.namelist() else ""
only_page = ("PAGE" in fxml) and ("Page" not in fxml.replace("PAGE", ""))
moji = xml.count("\uFFFD")
print("=== VERIFICATION SUMMARY ===")
print(f"paragraphs={n_para} tables={n_tables} images={n_images}")
print(f"PAGE fields in document={n_pagefld}; footer has PAGE-only={only_page}")
print(f"tblHeader flags={n_tblHeader} (expect >= tables), cantSplit rows={n_cantSplit}")
print(f"heading colours used={hcols} (expect black 000000 only)")
print(f"abstract words (excl Keywords)={wc} (must be <=160)")
print(f"mojibake U+FFFD remaining={moji}")
print(f"table count via python-docx={len(dd.tables)}; heading1 count={sum(1 for p in dd.paragraphs if p.style.name=='Heading 1')}")
