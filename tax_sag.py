#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from argparse import ArgumentParser
from matplotlib.ticker import FuncFormatter

from tax_methods import IncomeTax, NationalInsurance, StudentFinance

parser = ArgumentParser()
parser.add_argument('max', type=int, nargs='?', default=80000,
                    help='Maximum gross income')
parser.add_argument('--no-student', dest='student', action='store_false',
                    help='Has no student loan')
parser.add_argument('-p', dest='percent', action='store_true',
                    help='Show percentage taxed')
args = parser.parse_args()

# x-axis
dg = 1
gross = np.arange(0, args.max, dg)

# Calculate taxes
it = IncomeTax.tax(gross)
ni = NationalInsurance.tax(gross)
if args.student:
    sf = StudentFinance.tax(gross)
    areas = [sf, ni, it]
else:
    sf = 0.
    areas = [ni, it]

tax = it + ni + sf
takehome = gross - tax
areas = [takehome, it, ni]
labels = ['Take-Home', 'Income Tax', 'National Ins.']
colors = ['darkgreen', 'darkred', 'sandybrown']
if args.student:
    areas.append(sf)
    labels.append('Student Loan')
    colors.append('gold')

fig, ax1 = plt.subplots(1)

y = np.row_stack(areas)
ax1.stackplot(gross, y, labels=labels, colors=colors)

# Format x- and y-axis to count as 10k, 20k etc.
gbp_formatter = FuncFormatter(lambda x, pos: '{:1.0f}k'.format(x*1e-3))
ax1.xaxis.set_major_formatter(gbp_formatter)
ax1.yaxis.set_major_formatter(gbp_formatter)

ax1.set_xlim([0, args.max])
ax1.set_ylim([0, args.max])
ax1.set_xlabel('Income [GBP]')
ax1.set_ylabel('Money [GBP]')
ax1.tick_params('y')
ax1.legend(loc=2)

fig.tight_layout()
plt.show()
