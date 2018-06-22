#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser
from colorama import init, Fore

from tax_tools import IncomeTax, NationalInsurance, StudentFinance

# Initialise colorama
init()

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
output = [('Gross Income', Fore.GREEN, ' ', gross)]

# Apply Income Tax
it = IncomeTax.tax(gross)
take_home -= it
output.append(('Income Tax', Fore.RED, '-', it))

# Apply National Insurance
ni = NationalInsurance.tax(gross)
take_home -= ni
output.append(('National Ins.', Fore.RED, '-', ni))

# Apply student loan repayments
if args.student:
    slr = StudentFinance.tax(gross)
    output.append(('Student Loan', Fore.RED, '-', slr))
else:
    slr = 0.
take_home -= slr

# Calculate take-home pay
output.append(('Takehome', Fore.GREEN, ' ', take_home))
output.append(('Monthly Pay', Fore.GREEN, ' ', take_home / 12.))
output.append(('Weekly Pay', Fore.GREEN, ' ', take_home / 52.))

# Print output
for name, sign, color, money in output:
    sys.stdout.write('{:>15}:   {}{}{:>12,.2f} £{}\n'.format(name, sign, color, money, Fore.WHITE))
sys.stdout.flush()
