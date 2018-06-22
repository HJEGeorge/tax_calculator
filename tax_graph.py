#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
from matplotlib.ticker import FuncFormatter

from tax_tools import IncomeTax, NationalInsurance, StudentFinance

parser = ArgumentParser()
parser.add_argument('max', type=int, nargs='?', default=80,
                    help='Maximum gross income in thousands of £')
parser.add_argument('--no-student', dest='student', action='store_false',
                    help='Has no student loan')
parser.add_argument('-p', dest='percent', action='store_true',
                    help='Show percentage taxed')
args = parser.parse_args()

# Set up x-axis scale
dg = 1
x_max = args.max * 1e3
gross = np.arange(1, x_max, dg)

# Calculate taxes and student loan repayments
it = IncomeTax.tax(gross)
ni = NationalInsurance.tax(gross)
if args.student:
    sf = StudentFinance.tax(gross)
else:
    sf = 0.

tax = it + ni + sf
takehome = gross - tax

# Convert to percentages
if args.percent:
    takehome *= 100./gross
    tax *= 100./gross
    it *= 100./gross
    ni *= 100./gross
    sf *= 100./gross

# Initialise stack plot
fig, ax1 = plt.subplots(1)
areas = [takehome, it, ni]

# Set colours and labels
labels = ['Take-Home', 'Income Tax', 'National Ins.']
colors = ['darkgreen', 'darkred', 'sandybrown']
if args.student:
    areas.append(sf)
    labels.append('Student Loan')
    colors.append('gold')

# Format x axes to count as 10k, 20k, 30k, ...
gbp_formatter = FuncFormatter(lambda x, pos: '{:1.0f}k'.format(x*1e-3))
ax1.xaxis.set_major_formatter(gbp_formatter)

if args.percent:
    # Format y axis as 10%, 20%, 30%, ...
    y_formatter = FuncFormatter(lambda x, pos: '{:1.0f}%'.format(x))
    y_max = 100.
    y_label = 'Percentage of Gross'
    legend_loc = 4
else:
    # Format y axis as 10k, 20k, 30k, ...
    y_formatter = gbp_formatter
    y_max = x_max
    y_label = 'Money [GBP]'
    legend_loc = 2

ax1.yaxis.set_major_formatter(y_formatter)
ax1.set_xlim([0, x_max])
ax1.set_ylim([0, y_max])
ax1.set_xlabel('Gross Income [GBP]')
ax1.set_ylabel(y_label)
ax1.grid(linestyle='-', alpha=0.2, color='k')

# Make stack plot
y = np.row_stack(areas)
ax1.stackplot(gross, y, labels=labels, colors=colors)
ax1.legend(loc=legend_loc)

fig.tight_layout()
plt.show()
