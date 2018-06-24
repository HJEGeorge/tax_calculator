#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser
from colorama import init, Fore

from tax_tools import TaxBrackets, IncomeTax, NationalInsurance, StudentFinance, StatutoryPension

# Initialise colorama
init()

# Parse command line arguments
parser = ArgumentParser()
parser.add_argument('gross', type=float,
                    help='Gross income in thousands of £')
parser.add_argument('--no-student', dest='student', action='store_false',
                    help='Has no student loan')
parser.add_argument('--no-pension', dest='pension', action='store_false',
                    help='Exclude auto-enrolled workplace pension')
pension_parser = parser.add_mutually_exclusive_group()
pension_parser.add_argument('-p', type=float, nargs=1,
                    help='Pension rate on gross income')
pension_parser.add_argument('-P', type=float, nargs=2,
                    help='Pension rate above certain gross income')
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
    output.append({ 'title':    'Student Finance',
                    'amount':   slr,
                    'colour':   Fore.RED,
                    'sign':     '-'})
    take_home -= slr

pension = None
if args.p is not None:
    pension = TaxBrackets([0], [args.p])
elif args.P is not None:
    pension = TaxBrackets([args.P[0]*1e3], [args.P[1]])
elif args.pension is not None:
    pension = StatutoryPension

if pension is not None:
    pen = pension.tax(gross)
    output.append({ 'title':    'Pension',
                    'amount':   pen,
                    'colour':   Fore.RED,
                    'sign':     '-'})
    take_home -= pen

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
