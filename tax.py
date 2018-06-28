#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colorama
import sys
from argparse import ArgumentParser

from tax_tools import generate_tax_code

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
parser.add_argument('--no-pension', dest='s_pension', action='store_false',
                    help='Exclude auto-enrolled workplace pension')
pension_parser = parser.add_mutually_exclusive_group()
pension_parser.add_argument('-p', metavar='p', type=float, nargs=1, dest='p_pension', default=None,
                    help='Pension rate on gross income')
pension_parser.add_argument('-P', metavar='P', type=float, nargs=2, dest='p_pension', default=None,
                    help='Pension rate above certain gross income')
args = parser.parse_args()

# Initialise variables
gross = args.gross * 1e3

tax_code = generate_tax_code(args.student, args.s_pension, args.p_pension)

# # Print output
# for out_dict in output:
#     sys.stdout.write('{title:>15}:   {color}{sign}{amount:>12,.2f} £{white}\n'.format(
#             white=white, **out_dict))

sys.stdout.write(tax_code.tax_string(gross) + '\n')
sys.stdout.flush()
