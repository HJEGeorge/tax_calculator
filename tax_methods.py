# Income tax brackets and rates
income_tax = [[ 11850,  46350,  150000],
              [  0.20,   0.40,    0.45]]

# National insurance brackets and rates
nation_ins = [[162*52,  892*52],
              [  0.12,    0.02]]

rate_student = 0.09     # Rate of student loan repayments
thres_student = 25000.  # Threshold before student loan repayments

def get_income_tax(salary):
    untaxed = salary
    tax = 0.
    for i in reversed(range(len(income_tax))):
        if salary > income_tax[0][i]:
            # Apply tax rate to amount within bracket
            tax += (untaxed - income_tax[0][i]) * income_tax[1][i]
            margin = income_tax[0][i]
    return tax

def get_ni(salary):
    uninsured = salary
    insurance = 0.
    for i in reversed(range(len(nation_ins))):
        if salary > nation_ins[0][i]:
            # Apply nation insurance rate to amount within bracket
            insurance += (uninsured - nation_ins[0][i]) * nation_ins[1][i]
            uninsured = nation_ins[0][i]
    return insurance

def get_slr(salary):
    return (salary - thres_student) * rate_student * int(salary > thres_student)
