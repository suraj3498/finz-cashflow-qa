import re
from typing import Optional, Tuple

# --- Cashflow classification patterns (deterministic) ---
TRANSFER_PATTERNS = [
    r"\bTRANSFER\b", r"\bACH\b", r"\bZELLE\b", r"\bVENMO\b", r"\bPAYPAL\b",
    r"\bTO\s+SAVINGS\b", r"\bTO\s+CHECKING\b", r"\bINTERNAL\s+TRANSFER\b",
]

WITHDRAWAL_PATTERNS = [
    r"\bATM\b", r"\bWITHDRAW(AL)?\b", r"\bCASH\s+WITHDRAWAL\b"
]

# Transfer subtype (must be handled before P&L)
TRANSFER_INTERNAL_PATTERNS = [
    r"\bINTERNAL\b", r"\bTO\s+SAVINGS\b", r"\bTO\s+CHECKING\b", r"\bOWN\s+ACCOUNT\b"
]
TRANSFER_EXTERNAL_PATTERNS = [
    r"\bZELLE\b", r"\bVENMO\b", r"\bPAYPAL\b", r"\bWIRE\b"
]

# Withdrawal subtype
WITHDRAWAL_ATM_PATTERNS = [r"\bATM\b"]
WITHDRAWAL_OWNER_DRAW_PATTERNS = [r"\bOWNER\s+DRAW\b", r"\bDRAW\b"]

# --- P&L outflow categories (keyword engine) ---
# Order matters: first match wins.
OUTFLOW_CATEGORY_RULES = [
    # COGS
    ("OUTFLOW_COGS_FOOD", [r"\bSYSCO\b", r"\bUS\s*FOODS?\b", r"\bFOOD\b", r"\bWHOLESALE\b"]),
    ("OUTFLOW_COGS_BEVERAGE", [r"\bBEVERAGE\b", r"\bLIQUOR\b", r"\bDISTRIBUT(OR|ION)\b"]),
    ("OUTFLOW_COGS_SUPPLIES", [r"\bSUPPL(Y|IES)\b", r"\bPACKAGING\b", r"\bNAPKIN\b", r"\bCONTAINER\b"]),
    ("OUTFLOW_COGS_OTHER", [r"\bCOGS\b", r"\bINGREDIENT\b"]),

    # Labor
    ("OUTFLOW_LABOR_PAYROLL", [r"\bPAYROLL\b", r"\bGUSTO\b", r"\bADP\b", r"\bPAYCHEX\b"]),
    ("OUTFLOW_LABOR_TAXES", [r"\bIRS\b", r"\bPAYROLL\s+TAX\b", r"\bDEPT\s+OF\s+REVENUE\b"]),
    ("OUTFLOW_LABOR_BENEFITS", [r"\bBENEFIT\b", r"\bINSURANCE\s+BENEFIT\b", r"\bHEALTH\s+PLAN\b"]),

    # Overhead / Opex
    ("OUTFLOW_RENT", [r"\bRENT\b", r"\bLEASE\b"]),
    ("OUTFLOW_UTILITIES", [r"\bELECTRIC\b", r"\bWATER\b", r"\bGAS\b", r"\bUTILITY\b", r"\bCOMCAST\b", r"\bVERIZON\b"]),
    ("OUTFLOW_INSURANCE", [r"\bINSURANCE\b", r"\bPREMIUM\b"]),
    ("OUTFLOW_SOFTWARE", [r"\bSAAS\b", r"\bSUBSCRIPTION\b", r"\bSOFTWARE\b", r"\bMICROSOFT\b", r"\bGOOGLE\b"]),
    ("OUTFLOW_PROFESSIONAL_FEES", [r"\bCPA\b", r"\bACCOUNTING\b", r"\bLEGAL\b", r"\bLAW\b", r"\bCONSULT(ING)?\b"]),
    ("OUTFLOW_MARKETING", [r"\bADS?\b", r"\bMARKETING\b", r"\bFACEBOOK\b", r"\bINSTAGRAM\b", r"\bGOOGLE\s+ADS\b"]),
    ("OUTFLOW_MAINTENANCE", [r"\bREPAIR\b", r"\bMAINT(ENANCE)?\b", r"\bSERVICE\s+CALL\b"]),
    ("OUTFLOW_MISC_OPEX", [r"\bOFFICE\b", r"\bSTATIONERY\b", r"\bMISC\b"]),

    # Vendors
    ("OUTFLOW_VENDOR_NONCOGS", [r"\bVENDOR\b", r"\bCONTRACTOR\b"]),

    # Financing
    ("OUTFLOW_DEBT_SERVICE", [r"\bDEBT\s+SERVICE\b"]),
    ("OUTFLOW_INTEREST", [r"\bINTEREST\b"]),
    ("OUTFLOW_LOAN_PAYMENT", [r"\bLOAN\b", r"\bLENDER\b", r"\bAMORTIZATION\b"]),

    # Taxes
    ("OUTFLOW_SALES_TAX", [r"\bSALES\s+TAX\b"]),
    ("OUTFLOW_BUSINESS_TAX", [r"\bBUSINESS\s+TAX\b", r"\bFRANCHISE\s+TAX\b"]),
    ("OUTFLOW_FEES", [r"\bFEE\b", r"\bCHARGE\b", r"\bSERVICE\s+FEE\b"]),
]

def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text) for p in patterns)

def classify_cashflow_type(description: str, amount: float) -> str:
    d = (description or "").upper()
    if _matches_any(d, TRANSFER_PATTERNS):
        return "TRANSFER"
    if _matches_any(d, WITHDRAWAL_PATTERNS):
        return "WITHDRAWAL"
    if amount > 0:
        return "INFLOW"
    return "OUTFLOW"

def classify_transfer_category(description: str) -> str:
    d = (description or "").upper()
    if _matches_any(d, TRANSFER_INTERNAL_PATTERNS):
        return "TRANSFER_INTERNAL"
    if _matches_any(d, TRANSFER_EXTERNAL_PATTERNS):
        return "TRANSFER_EXTERNAL"
    return "TRANSFER_EXTERNAL"

def classify_withdrawal_category(description: str) -> str:
    d = (description or "").upper()
    if _matches_any(d, WITHDRAWAL_ATM_PATTERNS):
        return "WITHDRAWAL_ATM"
    if _matches_any(d, WITHDRAWAL_OWNER_DRAW_PATTERNS):
        return "WITHDRAWAL_OWNER_DRAW"
    return "WITHDRAWAL_ATM"

def classify_outflow_category(description: str, vendor_name: Optional[str] = None) -> str:
    text = f"{(vendor_name or '')} {(description or '')}".upper()
    for cat, patterns in OUTFLOW_CATEGORY_RULES:
        if _matches_any(text, patterns):
            return cat
    # Required fallback
    return "OUTFLOW_VENDOR_NONCOGS"
