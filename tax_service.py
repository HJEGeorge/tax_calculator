from tax_tools import generate_tax_code

def take_home_pay(income, student_loan_amount=0, pension_eligible=True):
    if student_loan_amount > 0: student = True
    else: student = False
    tax_code = generate_tax_code(student, pension=pension_eligible)
    return tax_code.take_home_pay(income)
