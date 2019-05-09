#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Original code written by Johan G. McQuillan (2018)
# Modified by Henry George for Step Exchange Limited (2018)
#
# A command line utility to calculate UK PAYE tax contributions, student loan and pension deductions.


import logging
import colorama
import sys
from argparse import ArgumentParser

from tax_tools import generate_tax_code

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

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
                        help='Exclude pension')
    pension_parser = parser.add_mutually_exclusive_group()
    pension_parser.add_argument('-p', metavar='p', type=float, dest='private_pension', default=None,
                                help='Private pension rate')
    pension_parser.add_argument('-P', metavar='P', type=float, dest='statutory_pension', default=None,
                                help='Statutory pension rate')
    args = parser.parse_args()

    # Initialise variables
    gross = args.gross * 1e3

    tax_code = generate_tax_code(args.student, args.pension, args.statutory_pension, args.private_pension)

    sys.stdout.write(tax_code.tax_string(gross) + '\n')
    sys.stdout.flush()