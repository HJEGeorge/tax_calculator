#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser

from tax_methods import IncomeTax, NationalInsurance, StudentFinance

parser = ArgumentParser()
parser.add_argument('gross', type=float, help='Gross income')
parser.add_argument('--no-student', dest='student', action='store_false', help='Has no student loan')
args = parser.parse_args()

gross = args.gross
takehome = gross
output = [('Gross Income', ' ', gross)]

it = IncomeTax.tax(gross)
takehome -= it
output.append(('Income Tax', '-', it))

ni = NationalInsurance.tax(gross)
takehome -= ni
output.append(('National Ins.', '-', ni))

if args.student:
    slr = StudentFinance.tax(gross)
    output.append(('Student Loan', '-', slr))
else:
    slr = 0.
takehome -= slr

output.append(('Takehome', ' ', takehome))
output.append(('Monthly Pay', ' ', takehome/12.))
output.append(('Weekly Pay', ' ', takehome/52.))

for name, sign, money in output:
    sys.stdout.write('{:>15}:   {}{:>12,.2f} £\n'.format(name, sign, money))
sys.stdout.flush()
