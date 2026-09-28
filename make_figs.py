"""Generate ER + architecture figures with proper margins (bbox_inches=tight)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import textwrap

def er_diagram(path="fig_er.png"):
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis("off")
    boxes = {
        "CATEGORIES\nCategoryID (PK)\nCategoryName": (0.4, 4.6),
        "SUPPLIERS\nSupplierID (PK)\nSupplierName, Phone": (0.4, 1.4),
        "PRODUCTS\nProductID (PK)\nCategoryID (FK)\nSupplierID (FK)\nPrice, Stock": (3.6, 3.0),
        "CUSTOMERS\nCustomerID (PK)\nCustomerName, Phone": (7.0, 4.6),
        "BILLS\nBillID (PK)\nCustomerID (FK)\nBillDate, TotalAmount*": (7.0, 1.4),
        "BILLITEMS\nItemID (PK)\nBillID (FK)\nProductID (FK)\nQuantity, Price": (4.6, 0.2),
    }
    drawn = {}
    for label, (x, y) in boxes.items():
        b = FancyBboxPatch((x, y), 2.6, 1.5, boxstyle="round,pad=0.08",
                           facecolor="white", edgecolor="black", linewidth=1.6)
        ax.add_patch(b)
        ax.text(x + 1.3, y + 0.75, label, ha="center", va="center", fontsize=8,
                family="monospace", color="black", linespacing=1.4)
        drawn[label.split("\n")[0]] = (x + 1.3, y + 0.75, x, y)
    def link(a, b, lab, side="top"):
        import numpy as np
        x1, y1, bx1, by1 = drawn[a]
        x2, y2, bx2, by2 = drawn[b]
        ax.annotate("", xy=(bx2 + 1.3, by2 + 1.5 if y2 > y1 else by2),
                    xytext=(bx1 + 1.3, by1 if y2 < y1 else by1 + 1.5),
                    arrowprops=dict(arrowstyle="-", color="black", linewidth=1.3,
                                    connectionstyle="arc3,rad=0.05"))
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 + 0.15
        ax.text(mx, my, lab, fontsize=7.5, ha="center", va="center",
                family="monospace", color="white",
                bbox=dict(facecolor="black", edgecolor="black", boxstyle="round,pad=0.25"))
    link("CATEGORIES", "PRODUCTS", "1 : M")
    link("SUPPLIERS", "PRODUCTS", "1 : M")
    link("CUSTOMERS", "BILLS", "1 : M")
    link("BILLS", "BILLITEMS", "1 : M")
    link("PRODUCTS", "BILLITEMS", "1 : M")
    ax.text(5.5, 6.5, "ER Diagram - Retail Store Management System (6 tables, 5 FK links)",
            ha="center", fontsize=10, weight="bold", family="sans-serif")
    ax.text(5.5, 0.05, "* Bills.TotalAmount is maintained by trigger TRG_BILL_TOTAL, never typed by hand.",
            ha="center", fontsize=7, style="italic")
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print("saved", path)

def arch_diagram(path="fig_arch.png"):
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    layers = [
        ("PRESENTATION\nSQL*Plus receipts\nFlask POS UI (app.py)", 0.5, 2.9, 2.6, 1.5),
        ("APPLICATION LOGIC\nBilling flow\nUPI QR (qrcode)", 3.7, 2.9, 2.6, 1.5),
        ("DATABASE (Oracle)\n6 tables + TRG_BILL_TOTAL\nFK integrity", 6.9, 2.9, 2.6, 1.5),
    ]
    for label, x, y, w, h in layers:
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                           facecolor="white", edgecolor="black", linewidth=1.6)
        ax.add_patch(b)
        ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=8,
                family="monospace", color="black", linespacing=1.5)
    for i in range(2):
        x1 = layers[i][1] + layers[i][3]
        x2 = layers[i+1][1]
        ax.annotate("", xy=(x2, 3.65), xytext=(x1, 3.65),
                    arrowprops=dict(arrowstyle="<->", color="black", linewidth=1.4))
    ax.text(5, 4.85, "Three-Layer Database Application Architecture", ha="center",
            fontsize=10, weight="bold")
    ax.text(5, 2.2, "Flow: POS UI / SQL*Plus  ->  Bill + BillItems inserts  ->  trigger recomputes Bills.TotalAmount  ->  receipt / QR",
            ha="center", fontsize=7.5, family="monospace",
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))
    ax.text(5, 1.35, "Sample proof: Bill 1001 = 550x1 + 20x2 + 65x1 = 655.00  |  Bill 1002 = 26x2 + 45x1 = 97.00",
            ha="center", fontsize=7.5, family="monospace",
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))
    ax.text(5, 0.6, "Files: store_database.sql (DDL + trigger + data)  |  bill_script.sql (receipt)  |  app.py (Flask POS)",
            ha="center", fontsize=7.5, family="monospace",
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print("saved", path)

if __name__ == "__main__":
    er_diagram()
    arch_diagram()
