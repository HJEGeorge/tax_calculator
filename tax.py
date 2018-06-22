#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser

from tax_tools import IncomeTax, NationalInsurance, StudentFinance

parser = ArgumentParser()
parser.add_argument('gross', type=float,
                    help='Gross income in thousands of £')
parser.add_argument('--no-student', dest='student', action='store_false',
                    help='Has no student loan')
args = parser.parse_args()

# Initialise variables
gross = args.gross * 1e3
take_home = gross

# Initialise output data
output = [('Gross Income', ' ', gross)]

# Apply Income Tax
it = IncomeTax.tax(gross)
take_home -= it
output.append(('Income Tax', '-', it))

# Apply National Insurance
ni = NationalInsurance.tax(gross)
take_home -= ni
output.append(('National Ins.', '-', ni))

# Apply student loan repayments
if args.student:
    slr = StudentFinance.tax(gross)
    output.append(('Student Loan', '-', slr))
else:
    slr = 0.
take_home -= slr

# Calculate take-home pay
output.append(('Takehome', ' ', take_home))
output.append(('Monthly Pay', ' ', take_home / 12.))
output.append(('Weekly Pay', ' ', take_home / 52.))

# Print output
for name, sign, money in output:
    sys.stdout.write('{:>15}:   {}{:>12,.2f} £\n'.format(name, sign, money))
sys.stdout.flush()
