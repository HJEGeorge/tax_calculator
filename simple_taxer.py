#!/usr/bin/env python

from argparse import ArgumentParser
import sys

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

parser = ArgumentParser()
parser.add_argument('gross', type=float, help='Gross income')
parser.add_argument('--no-student', dest='student', action='store_false', help='Has no student loan')
args = parser.parse_args()

gross = args.gross
total = gross
output = [('Gross Income', gross)]

tax = get_income_tax(gross)
total -= tax
output.append(('Income Tax', -tax))

ni = get_ni(gross)
total -= ni
output.append(('National Ins.', -ni))

if args.student:
    slr = (gross - thres_student) * rate_student
    output.append(('Student Loan', -slr))
else:
    slr = 0.
total -= slr

output.append(('Total', total))
output.append(('Monthly Pay', total/12.))
output.append(('Weekly Pay', total/52.))

for name, money in output:
    sys.stdout.write('{:>15}:   {:>12,.2f}\n'.format(name, money))
sys.stdout.flush()


