#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colorama
import sys
from argparse import ArgumentParser

from tax_tools import TaxBrackets, IncomeTax, NationalInsurance, StudentFinance, StatutoryPension

colorama.init()
white = colorama.Style.RESET_ALL
red = colorama.Fore.RED
green = colorama.Fore.GREEN

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
            'colour':   green,
            'sign':     ' '}]

# Apply Income Tax
it = IncomeTax.tax(gross)
take_home -= it
output.append({ 'title':    'Income Tax',
                'amount':   it,
                'colour':   red,
                'sign':     '-'})

# Apply National Insurance
ni = NationalInsurance.tax(gross)
take_home -= ni
output.append({ 'title':    'National Ins.',
                'amount':   ni,
                'colour':   red,
                'sign':     '-'})

# Apply student loan repayments
if args.student:
    slr = StudentFinance.tax(gross)
    output.append({ 'title':    'Student Finance',
                    'amount':   slr,
                    'colour':   red,
                    'sign':     '-'})
    take_home -= slr

pension = None
if args.p is not None:
    pension = TaxBrackets([0], [args.p])
elif args.P is not None:
    pension = TaxBrackets([args.P[0]*1e3], [args.P[1]])
elif args.pension:
    pension = StatutoryPension

if pension is not None:
    pen = pension.tax(gross)
    output.append({ 'title':    'Pension',
                    'amount':   pen,
                    'colour':   red,
                    'sign':     '-'})
    take_home -= pen

# Calculate take-home pay
output.append({ 'title':    'Take-Home Pay',
                'amount':   take_home,
                'colour':   green,
                'sign':     ' '})
output.append({ 'title':    'Monthly Pay',
                'amount':   take_home / 12,
                'colour':   green,
                'sign':     ' '})
output.append({ 'title':    'Weekly Pay',
                'amount':   take_home / 52,
                'colour':   green,
                'sign':     ' '})

# Print output
for out_dict in output:
    sys.stdout.write('{title:>15}:   {colour}{sign}{amount:>12,.2f} £{white}\n'.format(
            white=white, **out_dict))
sys.stdout.flush()
