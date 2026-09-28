# ===== p4 TABLE OF CONTENTS (table with Page column filled) =====
h1(doc, "TABLE OF CONTENTS")
toc_rows = [
    ["Cover Page", "1"],
    ["Certificate", "2"],
    ["Declaration and Acknowledgement", "3"],
    ["Table of Contents", "4"],
    ["Abstract", "5"],
    ["List of Figures, List of Tables, Abbreviations", "6"],
    ["1. Introduction", "7"],
    ["2. System Analysis", "8"],
    ["3. Database Design", "9"],
    ["4. ER Diagram", "10"],
    ["5. Relational Schema", "11"],
    ["6. Table Design", "12"],
    ["7. Normalization", "14"],
    ["8. SQL Implementation", "15"],
    ["9. SQL Queries and Screenshots", "16"],
    ["10. Conclusion and Future Enhancements", "18"],
    ["References", "19"],
    ["Appendix - Important Code Blocks", "20"],
]
make_table(doc, ["Contents", "Page"], toc_rows)

# ===== p5 ABSTRACT (2 short paras + italic Keywords, <=160 words) =====
h1(doc, "ABSTRACT")
a1 = "The Retail Store Management System is a centralized Oracle relational database for a medium-sized retail store. Six related tables manage categories, suppliers, products, customers, bills and bill items. A statement-level PL/SQL trigger recomputes every bill total automatically as SUM(Price x Quantity), so totals are never typed by hand."
a2 = "Sample data of 5 categories, 2 suppliers, 5 products, 3 customers, 2 bills and 5 bill items verifies correctly: Bill 1001 totals 655.00 and Bill 1002 totals 97.00, each exactly equal to the sum of its lines. Any bill prints instantly as a formatted SQL*Plus receipt, and the same schema backs a Flask POS web application."
body(doc, a1)
body(doc, a2)
pk = doc.add_paragraph(); pk.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
rk = pk.add_run("Keywords: retail store, Oracle SQL, PL/SQL trigger, billing, POS, referential integrity.")
rk.italic = True; rk.font.size = Pt(12); rk.font.name = "Times New Roman"

# ===== p6 LOF / LOT / ABBREVIATIONS =====
h1(doc, "LIST OF FIGURES")
body(doc, "Fig. 1: ER Diagram of Retail Store Management System (p. 10). Fig. 2: Three-Layer Database Application Architecture (p. 10).")
h1(doc, "LIST OF TABLES", page_break=False)
body(doc, "Table 1. Major Database Entities (p. 9). Table 2. Categories Table Structure (p. 12). Table 3. Suppliers Table Structure (p. 12). Table 4. Products Table Structure (p. 12). Table 5. Customers Table Structure (p. 13). Table 6. Bills Table Structure (p. 13). Table 7. BillItems Table Structure (p. 13). Table 8. Keys and Constraints (p. 13). Table 9. Sample Data and Verification Counts (p. 13). Table 10. Bill Totals Verification (p. 16).")
h1(doc, "ABBREVIATIONS", page_break=False)
bullets(doc, [
    "DBMS - Database Management System",
    "ER - Entity Relationship",
    "SQL - Structured Query Language",
    "DDL - Data Definition Language",
    "DML - Data Manipulation Language",
    "DQL - Data Query Language",
    "PK - Primary Key",
    "FK - Foreign Key",
    "1NF - First Normal Form",
    "2NF - Second Normal Form",
    "3NF - Third Normal Form",
    "POS - Point of Sale",
    "UPI - Unified Payments Interface",
])

# ===== Ch1 INTRODUCTION =====
h1(doc, "1. INTRODUCTION")
h2(doc, "1.1 Brief Information about the Project")
body(doc, "The Retail Store Management System is a DBMS cornerstone project that computerizes daily retail work: the product catalogue, suppliers, customers and billing. Six Oracle tables replace registers and loose Excel sheets. A PL/SQL trigger keeps every bill total mathematically correct, and a SQL*Plus script prints any bill as a formatted receipt. The same schema also backs a Flask POS web application (app.py) with inventory, billing, UPI QR and reports modules.")
h2(doc, "1.2 Motivation and Contribution of Project")
body(doc, "Small stores lose money to repeated names, wrong hand-computed totals, no record of who bought what, and slow manual billing. This project contributes a single normalized database where each fact is stored once, foreign keys reject invalid links, totals are derived rather than entered, and receipts are reproducible for any BillID.")
bullets(doc, [
    "Centralizing catalogue, supplier, customer and billing records in one relational database.",
    "Eliminating hand-computed totals through trigger TRG_BILL_TOTAL.",
    "Maintaining referential integrity using primary and foreign keys.",
    "Supporting faster queries and reports such as low-stock alerts and best-sellers.",
    "Providing a Flask POS front end plus SQL*Plus receipts over the same backend.",
])
h2(doc, "1.3 Objectives of the Project")
bullets(doc, [
    "Design six related tables with primary keys, foreign keys, NOT NULL, UNIQUE and DEFAULT rules.",
    "Implement a statement-level trigger that auto-computes Bills.TotalAmount.",
    "Load realistic sample data: 5 categories, 2 suppliers, 5 products, 3 customers, 2 bills, 5 bill items.",
    "Verify each bill total equals SUM(Price x Quantity): 655.00 for Bill 1001 (n=3 lines), 97.00 for Bill 1002 (n=2 lines).",
    "Print formatted receipts for any BillID and support CRUD plus reporting queries.",
])
h2(doc, "1.4 Scope of the Project")
body(doc, "The scope covers the complete store workflow: catalogue (Categories, Suppliers, Products), sales parties (Customers), and transactions (Bills, BillItems). Out of scope are GST computation, discounts, barcode scanning and SMS billing, which are listed as future enhancements. The Oracle SQL core is complete and tested; the Flask app reuses the identical six-table logic in SQLite for demonstration.")

# ===== Ch2 SYSTEM ANALYSIS =====
h1(doc, "2. SYSTEM ANALYSIS")
h2(doc, "2.1 Existing System")
bullets(doc, [
    "Paper registers or disconnected Excel sheets per counter.",
    "Product names and prices retyped on every bill, causing duplicates.",
    "Totals computed on calculators, with frequent arithmetic errors.",
    "No link between who bought what; consolidated reports take hours.",
    "Higher possibility of data-entry errors with no constraint checking.",
])
h2(doc, "2.2 Proposed System")
body(doc, "The proposed system uses a centralized Oracle relational database with six tables and five foreign-key links. BillItems resolves the many-to-many link between Bills and Products. The trigger TRG_BILL_TOTAL fires after any insert, update or delete on BillItems and rewrites Bills.TotalAmount from the current lines. Receipts are generated by bill_script.sql joining Bills, Customers, BillItems and Products.")
bullets(doc, ["Centralized database", "Product and catalogue management", "Supplier management",
              "Customer and billing management", "Automatic total computation", "SQL-based receipt printing and reporting", "Referential integrity"])
h2(doc, "2.3 Functional Requirements")
make_table(doc, ["Module", "Functional Requirement"],
           [["Catalogue Management", "Add, update, search and display products with category and supplier links."],
            ["Supplier Management", "Store supplier details; each product references exactly one supplier."],
            ["Customer Management", "Store buyer details; each bill references exactly one customer."],
            ["Billing Management", "Create bills with multiple BillItems lines; totals auto-computed."],
            ["Receipt Generation", "Print formatted receipt for any BillID with grand total."],
            ["Search and Reporting", "Low-stock alert, sales per day, best-sellers, category-wise sales."]])
h2(doc, "2.4 Non-Functional Requirements")
bullets(doc, [
    "Performance - queries return results efficiently for normal retail workloads (sample n=5 products, 2 bills).",
    "Integrity - invalid references and duplicate key values are rejected by constraints.",
    "Reliability - trigger keeps Bills.TotalAmount consistent after every BillItems change.",
    "Usability - SQL*Plus receipts and Flask forms are understandable to shop staff.",
    "Scalability - design supports growth in products, customers and bills without schema change.",
])
h2(doc, "2.5 Requirements Specification")
make_table(doc, ["Category", "Suggested Requirement"],
           [["Hardware", "Intel i3 or above; 4 GB RAM minimum; adequate storage; standard display and keyboard."],
            ["Operating System", "Windows 10/11 with Oracle 26ai Free and SQL*Plus; Python 3 with Flask for POS demo."],
            ["Database", "Oracle Database (NUMBER/VARCHAR2 types); SQLite used only inside Flask demo with identical logic."]])

# ===== Ch3 DATABASE DESIGN =====
h1(doc, "3. DATABASE DESIGN")
h2(doc, "3.1 Major Entities")
make_table(doc, ["Entity", "Description"],
           [["Categories", "Lookup of product groups; 5 rows: Grocery, Beverages, Snacks, Dairy, Personal Care."],
            ["Suppliers", "Who supplies products; 2 rows: Bharat Wholesale, Fresh Foods Co."],
            ["Products", "Central catalogue; 5 rows with price and stock."],
            ["Customers", "Buyer details; 3 rows: Rahul Sharma, Priya Patel, Amit Verma."],
            ["Bills", "One row per purchase; 2 rows (1001, 1002); TotalAmount set by trigger."],
            ["BillItems", "One row per product line on a bill; 5 rows; junction between Bills and Products."]])
body(doc, "Table 1. Major Database Entities with sample sizes (n=5 categories, n=2 suppliers, n=5 products, n=3 customers, n=2 bills, n=5 bill items).")
h2(doc, "3.2 ER Model")
body(doc, "The ER model has six entities and five one-to-many relationships: Categories 1-M Products, Suppliers 1-M Products, Customers 1-M Bills, Bills 1-M BillItems, Products 1-M BillItems. Every link is enforced by a FOREIGN KEY constraint so invalid ids are rejected automatically (for example deleting a customer who has bills fails with ORA-02292).")
h2(doc, "3.3 Relationships")
make_table(doc, ["Relationship", "Description"],
           [["Categories 1 - M Products", "One category holds many products; every product belongs to exactly one category."],
            ["Suppliers 1 - M Products", "One supplier provides many products; each product has one supplier."],
            ["Customers 1 - M Bills", "One customer creates many bills; every bill belongs to one customer."],
            ["Bills 1 - M BillItems", "One bill has many lines; each line belongs to one bill."],
            ["Products 1 - M BillItems", "One product appears in many bills; BillItems resolves the many-to-many link."]])

# ===== Ch4 ER DIAGRAM =====
h1(doc, "4. ER DIAGRAM")
figure(doc, "fig_er.png", "Fig. 1: ER Diagram of Retail Store Management System - six entities and five foreign-key links.")
body(doc, "Figure 1 shows the six entities with keys and the five relationships. Products carries CategoryID and SupplierID; Bills carries CustomerID; BillItems carries BillID and ProductID. Bills.TotalAmount is derived and never entered by hand.")
figure(doc, "fig_arch.png", "Fig. 2: Proposed Three-Layer Database Application Architecture - presentation, logic and Oracle database.")
body(doc, "Figure 2 shows presentation (SQL*Plus receipts and Flask POS UI), application logic (billing flow and UPI QR generation), and the Oracle database with six tables plus trigger TRG_BILL_TOTAL.")

# ===== Ch5 RELATIONAL SCHEMA =====
h1(doc, "5. RELATIONAL SCHEMA")
make_table(doc, ["Relation", "Relational Schema"],
           [["CATEGORIES", "CategoryID (PK), CategoryName"],
            ["SUPPLIERS", "SupplierID (PK), SupplierName, Phone"],
            ["PRODUCTS", "ProductID (PK), ProductName, CategoryID (FK), SupplierID (FK), Price, Stock"],
            ["CUSTOMERS", "CustomerID (PK), CustomerName, Phone"],
            ["BILLS", "BillID (PK), CustomerID (FK), BillDate, TotalAmount (set by trigger)"],
            ["BILLITEMS", "ItemID (PK), BillID (FK), ProductID (FK), Quantity, Price (at sale time)"]])
body(doc, "Parents are created before children (Categories, Suppliers, Customers before Products, Bills before BillItems) and dropped in reverse order (BillItems, Bills, Customers, Products, Categories, Suppliers). BillItems.Price stores the price at sale time so old bills do not change when Products.Price is revised.")

# ===== Ch6 TABLE DESIGN =====
h1(doc, "6. TABLE DESIGN")
h2(doc, "6.1 Categories Table")
make_table(doc, ["Attribute", "Data Type", "Constraint", "Description"],
           [["CategoryID", "NUMBER(4)", "PK, NOT NULL", "Unique category id (n=5 rows)"],
            ["CategoryName", "VARCHAR2(50)", "NOT NULL", "Group name: Grocery, Beverages, Snacks, Dairy, Personal Care"]])
h2(doc, "6.2 Suppliers Table")
make_table(doc, ["Attribute", "Data Type", "Constraint", "Description"],
           [["SupplierID", "NUMBER(4)", "PK", "Unique supplier id (n=2 rows)"],
            ["SupplierName", "VARCHAR2(100)", "NOT NULL", "Bharat Wholesale, Fresh Foods Co."],
            ["Phone", "VARCHAR2(15)", "-", "Contact number"]])
h2(doc, "6.3 Products Table")
make_table(doc, ["Attribute", "Data Type", "Constraint", "Description"],
           [["ProductID", "NUMBER(4)", "PK", "Unique product id (n=5 rows: 101-105)"],
            ["ProductName", "VARCHAR2(100)", "NOT NULL", "Basmati Rice 5kg, Coca Cola 750ml, Potato Chips, Amul Milk 500ml, Toothpaste 100g"],
            ["CategoryID", "NUMBER(4)", "FK", "References Categories"],
            ["SupplierID", "NUMBER(4)", "FK", "References Suppliers"],
            ["Price", "NUMBER(10,2)", "NOT NULL", "Unit price in Rs"],
            ["Stock", "NUMBER(4)", "DEFAULT 0", "Units on hand"]])
h2(doc, "6.4 Customers Table")
make_table(doc, ["Attribute", "Data Type", "Constraint", "Description"],
           [["CustomerID", "NUMBER(4)", "PK", "Unique customer id (n=3 rows)"],
            ["CustomerName", "VARCHAR2(100)", "NOT NULL", "Rahul Sharma, Priya Patel, Amit Verma"],
            ["Phone", "VARCHAR2(15)", "-", "Contact number"]])
h2(doc, "6.5 Bills Table")
make_table(doc, ["Attribute", "Data Type", "Constraint", "Description"],
           [["BillID", "NUMBER(4)", "PK", "Unique bill id (n=2 rows: 1001, 1002)"],
            ["CustomerID", "NUMBER(4)", "FK", "References Customers"],
            ["BillDate", "DATE", "DEFAULT SYSDATE", "01-AUG-2026 for both sample bills"],
            ["TotalAmount", "NUMBER(10,2)", "set by TRIGGER", "655.00 (Bill 1001, n=3 lines); 97.00 (Bill 1002, n=2 lines)"]])
h2(doc, "6.6 BillItems Table")
make_table(doc, ["Attribute", "Data Type", "Constraint", "Description"],
           [["ItemID", "NUMBER(4)", "PK", "Unique line id (n=5 rows)"],
            ["BillID", "NUMBER(4)", "FK", "References Bills"],
            ["ProductID", "NUMBER(4)", "FK", "References Products"],
            ["Quantity", "NUMBER(4)", "NOT NULL", "Units sold on that line"],
            ["Price", "NUMBER(10,2)", "NOT NULL", "Price at sale time"]])
h2(doc, "6.7 Keys and Constraints")
make_table(doc, ["Constraint Type", "Applied To / Purpose"],
           [["Primary Key", "CategoryID, SupplierID, ProductID, CustomerID, BillID, ItemID"],
            ["Foreign Key", "Products.CategoryID, Products.SupplierID, Bills.CustomerID, BillItems.BillID, BillItems.ProductID"],
            ["NOT NULL", "Names, prices, quantities and identifiers"],
            ["UNIQUE", "Enforced via primary keys; names kept unique in practice"],
            ["CHECK / DEFAULT", "Stock DEFAULT 0; BillDate DEFAULT SYSDATE; TotalAmount DEFAULT 0 before trigger"],
            ["Trigger", "TRG_BILL_TOTAL keeps Totals correct; FK blocks orphans (ORA-02292 on bad delete)"]])
body(doc, "Table 8. Keys and Constraints. Table 9. Sample data and verification counts: 5 categories, 2 suppliers, 5 products, 3 customers, 2 bills, 5 bill items.")
