#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser
from colorama import init, Fore

from tax_tools import IncomeTax, NationalInsurance, StudentFinance

# Initialise colorama
init()

# Parse command line arguments
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
output = [{ 'title':    'Gross Income',
            'amount':   gross,
            'colour':   Fore.GREEN,
            'sign':     ' '}]

# Apply Income Tax
it = IncomeTax.tax(gross)
take_home -= it
output.append({ 'title':    'Income Tax',
                'amount':   it,
                'colour':   Fore.RED,
                'sign':     '-'})

# Apply National Insurance
ni = NationalInsurance.tax(gross)
take_home -= ni
output.append({ 'title':    'National Ins.',
                'amount':   ni,
                'colour':   Fore.RED,
                'sign':     '-'})

# Apply student loan repayments
if args.student:
    slr = StudentFinance.tax(gross)
    output.append({ 'title':    'Income Tax',
                    'amount':   slr,
                    'colour':   Fore.RED,
                    'sign':     '-'})
else:
    slr = 0.
take_home -= slr

# Calculate take-home pay
output.append({ 'title':    'Take-Home Pay',
                'amount':   take_home,
                'colour':   Fore.GREEN,
                'sign':     ' '})
output.append({ 'title':    'Monthly Pay',
                'amount':   take_home / 12,
                'colour':   Fore.GREEN,
                'sign':     ' '})
output.append({ 'title':    'Weekly Pay',
                'amount':   take_home / 52,
                'colour':   Fore.GREEN,
                'sign':     ' '})

# Print output
for out_dict in output:
    sys.stdout.write('{title:>15}:   {colour}{sign}{amount:>12,.2f} £{white}\n'.format(white=Fore.WHITE, **out_dict))
sys.stdout.flush()
