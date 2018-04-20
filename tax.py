#!/usr/bin/env python

import sys
from argparse import ArgumentParser

from tax_methods import get_income_tax, get_ni, get_slr

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
    slr = get_slr(gross)
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
