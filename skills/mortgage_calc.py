#!/usr/bin/env python3
"""
Mortgage Calculator
- 30-year fixed rate: 6.22% (Freddie Mac PMMS, 3/19/2026)
- Down payment: $30,000
- Assumes property taxes ~1.0% of home value/year (WA avg)
- Assumes homeowner's insurance ~$1,200/year
- PMI estimated at 0.5% of loan/year (since <20% down)
"""
import sys
import json

# --- Inputs ---
home_price = 475000  # Default; override via CLI arg
if len(sys.argv) > 1:
    home_price = float(sys.argv[1])

down_payment = 30000
annual_rate = 6.22 / 100
term_years = 30

# --- Derived ---
loan_amount = home_price - down_payment
monthly_rate = annual_rate / 12
num_payments = term_years * 12
down_pct = (down_payment / home_price) * 100

# Monthly P&I (standard amortization formula)
if monthly_rate > 0:
    monthly_pi = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
else:
    monthly_pi = loan_amount / num_payments

total_paid = monthly_pi * num_payments
total_interest = total_paid - loan_amount

# Estimated extras
property_tax_monthly = (home_price * 0.01) / 12
insurance_monthly = 1200 / 12

# PMI (required when down < 20%)
if down_pct < 20:
    pmi_monthly = (loan_amount * 0.005) / 12
else:
    pmi_monthly = 0

total_monthly = monthly_pi + property_tax_monthly + insurance_monthly + pmi_monthly

# --- Amortization schedule summary (year-by-year) ---
balance = loan_amount
yearly_summary = []
for year in range(1, term_years + 1):
    year_interest = 0
    year_principal = 0
    for m in range(12):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_pi - interest_payment
        balance -= principal_payment
        year_interest += interest_payment
        year_principal += principal_payment
    yearly_summary.append({
        "year": year,
        "principal_paid": round(year_principal, 2),
        "interest_paid": round(year_interest, 2),
        "remaining_balance": round(max(balance, 0), 2)
    })

# --- Output ---
print("="*60)
print("MORTGAGE ANALYSIS")
print("="*60)
print(f"Home Price:              ${home_price:>12,.2f}")
print(f"Down Payment:            ${down_payment:>12,.2f} ({down_pct:.1f}%)")
print(f"Loan Amount:             ${loan_amount:>12,.2f}")
print(f"Interest Rate:           {annual_rate*100:>11.2f}% (30-yr fixed)")
print(f"Loan Term:               {term_years:>8d} years")
print("="*60)
print(f"Monthly Principal & Int: ${monthly_pi:>12,.2f}")
print(f"Est. Property Tax/mo:    ${property_tax_monthly:>12,.2f}")
print(f"Est. Insurance/mo:       ${insurance_monthly:>12,.2f}")
if pmi_monthly > 0:
    print(f"Est. PMI/mo:             ${pmi_monthly:>12,.2f}")
print("-"*60)
print(f"TOTAL Monthly Payment:   ${total_monthly:>12,.2f}")
print("="*60)
print(f"Total Paid (P&I only):   ${total_paid:>12,.2f}")
print(f"Total Interest Paid:     ${total_interest:>12,.2f}")
print(f"Interest-to-Loan Ratio:  {(total_interest/loan_amount)*100:>11.1f}%")
print("="*60)

# Show first 5 years and last 2 years of amortization
print("\nAMORTIZATION HIGHLIGHTS:")
print(f"{'Year':>4} | {'Principal':>12} | {'Interest':>12} | {'Balance':>14}")
print("-"*50)
for ys in yearly_summary[:5]:
    print(f"{ys['year']:>4} | ${ys['principal_paid']:>11,.2f} | ${ys['interest_paid']:>11,.2f} | ${ys['remaining_balance']:>13,.2f}")
print("  ...")
for ys in yearly_summary[-2:]:
    print(f"{ys['year']:>4} | ${ys['principal_paid']:>11,.2f} | ${ys['interest_paid']:>11,.2f} | ${ys['remaining_balance']:>13,.2f}")

# Equity milestones
print("\nEQUITY MILESTONES:")
for ys in yearly_summary:
    equity_pct = ((home_price - ys['remaining_balance']) / home_price) * 100
    if equity_pct >= 20 and ys['year'] == next(y['year'] for y in yearly_summary if ((home_price - y['remaining_balance'])/home_price)*100 >= 20):
        print(f"  → 20% equity reached in Year {ys['year']} (PMI can be removed)")
        break

print("\nSource: Freddie Mac PMMS, 30-yr fixed rate 6.22% as of 3/19/2026")
print("Note: Property tax & insurance are estimates. Actual may vary.")
