import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

def calculate_mortgage():
    try:
        P = float(loan_var.get()) if loan_var.get() else 0
        annual_rate = float(rate_var.get()) if rate_var.get() else 0
        years = float(years_var.get()) if years_var.get() else 0
        annual_insurance = float(insurance_var.get()) if insurance_var.get() else 0
        annual_pmi = float(pmi_var.get()) if pmi_var.get() else 0
        annual_taxes = float(taxes_var.get()) if taxes_var.get() else 0
        
        r = (annual_rate / 100) / 12 if annual_rate else 0
        n = years * 12 if years else 0
        M = P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r and n else 0
        
        monthly_insurance = annual_insurance / 12 if annual_insurance else 0
        monthly_pmi = annual_pmi / 12 if annual_pmi else 0
        monthly_taxes = annual_taxes / 12 if annual_taxes else 0
        
        total_monthly = M + monthly_insurance + monthly_pmi + monthly_taxes
        total_annual = total_monthly * 12 if total_monthly else 0
        
        mortgage_result.config(text=f"Monthly Mortgage: ${M:.2f}")
        total_monthly_result.config(text=f"Total Monthly Payment: ${total_monthly:.2f}")
        total_annual_result.config(text=f"Total Annual Payment: ${total_annual:.2f}")
        
    except ValueError:
        mortgage_result.config(text="Please enter valid numbers")

def calculate_amortization():
    try:
        P = float(loan_var.get()) if loan_var.get() else 0
        annual_rate = float(rate_var.get()) if rate_var.get() else 0
        years = float(years_var.get()) if years_var.get() else 0
        r = (annual_rate / 100) / 12 if annual_rate else 0
        n = years * 12 if years else 0
        M = P * (r * (1 + r)**n) / ((1 + r)**n - 1) if r and n else 0
        extra_payment = float(extra_payment_var.get()) if extra_payment_var.get() else 0
        
        remaining_balance = P
        amort_output.delete(1.0, tk.END)  # Clear previous output
        
        for month in range(1, int(n) + 1):
            interest_payment = remaining_balance * r
            principal_payment = M - interest_payment
            total_payment = M + extra_payment
            
            remaining_balance -= (principal_payment + extra_payment)
            if remaining_balance < 0:
                remaining_balance = 0
                
            amort_output.insert(tk.END, f"Month {month}: Total Payment = ${total_payment:.2f}, Remaining Balance = ${remaining_balance:.2f}\n")
            
            if remaining_balance <= 0:
                break
        
    except ValueError:
        amort_output.insert(tk.END, "Please enter valid numbers")

root = tk.Tk()
root.geometry("800x600")
root.title("Mortgage Calculator")

frame = ttk.Frame(root, padding="10")
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the frame

loan_var = tk.StringVar()
rate_var = tk.StringVar()
years_var = tk.StringVar()
insurance_var = tk.StringVar()
pmi_var = tk.StringVar()
taxes_var = tk.StringVar()
extra_payment_var = tk.StringVar()

ttk.Label(frame, text="Loan Amount:").grid(row=0, column=0)
ttk.Entry(frame, textvariable=loan_var).grid(row=0, column=1)

ttk.Label(frame, text="Annual Interest Rate (%):").grid(row=1, column=0)
ttk.Entry(frame, textvariable=rate_var).grid(row=1, column=1)

ttk.Label(frame, text="Loan Term (years):").grid(row=2, column=0)
ttk.Entry(frame, textvariable=years_var).grid(row=2, column=1)

ttk.Label(frame, text="Annual Insurance:").grid(row=3, column=0)
ttk.Entry(frame, textvariable=insurance_var).grid(row=3, column=1)

ttk.Label(frame, text="Annual PMI:").grid(row=4, column=0)
ttk.Entry(frame, textvariable=pmi_var).grid(row=4, column=1)

ttk.Label(frame, text="Annual Property Taxes:").grid(row=5, column=0)
ttk.Entry(frame, textvariable=taxes_var).grid(row=5, column=1)

ttk.Button(frame, text="Calculate", command=calculate_mortgage).grid(row=6, columnspan=2)

mortgage_result = ttk.Label(frame, text="Monthly Mortgage: ")
mortgage_result.grid(row=7, columnspan=2)

total_monthly_result = ttk.Label(frame, text="Total Monthly Payment: ")
total_monthly_result.grid(row=8, columnspan=2)

total_annual_result = ttk.Label(frame, text="Total Annual Payment: ")
total_annual_result.grid(row=9, columnspan=2)

ttk.Label(frame, text="Extra Monthly Principal:").grid(row=10, column=0)
ttk.Entry(frame, textvariable=extra_payment_var).grid(row=10, column=1)

ttk.Button(frame, text="Calculate Amortization", command=calculate_amortization).grid(row=11, columnspan=2)

amort_output = scrolledtext.ScrolledText(frame, width=70, height=20)
amort_output.grid(row=12, columnspan=2)

root.mainloop()
