#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colorama
import sys
from argparse import ArgumentParser

from tax_tools import TaxBracket, IncomeTax, NationalInsurance, StudentFinance, StatutoryPension

colorama.init()
white = colorama.Style.RESET_ALL
red = colorama.Fore.RED
green = colorama.Fore.GREEN


def output_dict(title, amount):
    """Return a dictionary for printing a accounting details about to the console."""
    if amount > 0:
        sign = ' '
        color = green
    else:
        sign = '-'
        color = red
    
    d = {'title':   title,
         'amount':  abs(amount),
         'sign':    sign,
         'color':   color}
    return d

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
output = [output_dict('Gross Income', gross)]

# Apply Income Tax
it = IncomeTax.tax(gross)
take_home -= it
output.append(output_dict('Income Tax', -it))

# Apply National Insurance
ni = NationalInsurance.tax(gross)
take_home -= ni
output.append(output_dict('National Ins.', -ni))

# Apply student loan repayments
if args.student:
    sfe = StudentFinance.tax(gross)
    take_home -= sfe
    output.append(output_dict('Student Finance', -sfe))

pension = None
if args.p is not None:
    pension = TaxBracket([0], [args.p])
elif args.P is not None:
    pension = TaxBracket([args.P[0] * 1e3], [args.P[1]])
elif args.pension:
    pension = StatutoryPension

if pension is not None:
    pen = pension.tax(gross)
    take_home -= pen
    output.append(output_dict('Pension', -pen))

# Calculate take-home pay
output.append(output_dict('Take-Home Pay', take_home))
output.append(output_dict('Monthly Pay', take_home / 12))
output.append(output_dict('Weekly Pay', take_home / 52))

# Print output
for out_dict in output:
    sys.stdout.write('{title:>15}:   {color}{sign}{amount:>12,.2f} £{white}\n'.format(
            white=white, **out_dict))
sys.stdout.flush()
