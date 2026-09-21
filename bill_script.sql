-- =============================================
-- Print a formatted bill receipt
-- Usage  : @bill_script <BillID>
-- Example: @bill_script 1001
-- =============================================

SET LINESIZE 58
SET PAGESIZE 60
SET FEEDBACK OFF
SET VERIFY OFF
SET ECHO OFF
SET HEADING OFF
SET UNDERLINE OFF
SET TRIMSPOOL ON

CLEAR COLUMNS
CLEAR BREAKS
CLEAR COMPUTES

PROMPT
PROMPT ======================================================
PROMPT                     POS MANAGEMENT SYSTEM
PROMPT                  Retail Store Bill
PROMPT ======================================================

SELECT 'Bill No   : ' || b.BillID
    || CHR(10) || 'Date      : ' || TO_CHAR(b.BillDate, 'DD-MON-YYYY')
    || CHR(10) || 'Customer  : ' || c.CustomerName || '  (' || c.Phone || ')'
FROM Bills b
JOIN Customers c ON b.CustomerID = c.CustomerID
WHERE b.BillID = &1;

PROMPT ------------------------------------------------------

SET HEADING ON

COLUMN ProductName HEADING 'PRODUCT' FORMAT A24
COLUMN Quantity    HEADING 'QTY'     FORMAT 999
COLUMN Price       HEADING 'PRICE'   FORMAT 99990.00
COLUMN Amount      HEADING 'AMOUNT'  FORMAT 999990.00

BREAK ON REPORT
COMPUTE SUM LABEL 'GRAND TOTAL' OF Amount ON REPORT

SELECT p.ProductName, i.Quantity, i.Price, (i.Price * i.Quantity) AS Amount
FROM BillItems i
JOIN Products p ON i.ProductID = p.ProductID
WHERE i.BillID = &1
ORDER BY i.ItemID;

CLEAR BREAKS
CLEAR COMPUTES

SET HEADING OFF
SELECT '------------------------------------------------------' || CHR(10) ||
       '             Thank you for shopping!' || CHR(10) ||
       '           *** Visit Again ***' || CHR(10)
FROM DUAL;

EXIT;
