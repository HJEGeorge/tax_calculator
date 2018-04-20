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
else:
    sf = 0.

tax = it + ni + sf
takehome = gross - tax

fig, ax1 = plt.subplots(1)

# Plot income and taxes
ax1.plot(gross, gross, color='darkgreen', alpha=0.3, label='Untaxed')
ax1.plot(gross, tax, color='darkred', label='Total Tax')
ax1.plot(gross, it, color='darkorange', label='Income Tax')
ax1.plot(gross, ni, color='sandybrown', label='National Ins.')
if args.student:
    ax1.plot(gross, sf, color='gold', label='Student Loans')
ax1.plot(gross, takehome, color='darkgreen', label='Take-Home')

# Format x- and y-axis to count as 10k, 20k etc.
gbp_formatter = FuncFormatter(lambda x, pos: '{:1.0f}k'.format(x*1e-3))
ax1.xaxis.set_major_formatter(gbp_formatter)
ax1.yaxis.set_major_formatter(gbp_formatter)

ax1.set_xlim([0, args.max])
ax1.set_ylim([0, args.max])
ax1.set_xlabel('Income [GBP]')
ax1.set_ylabel('Money [GBP]')
ax1.tick_params('y')
ax1.legend()

# Show tax percentages
if args.percent:
    # Axes for effective tax rate
    # Ignore first element to avoid divide by 0
    x1 = gross[1:]
    y1 = tax[1:]/x1*100.

    # Axes for marginal tax rate
    # Ignore first element to avoid divide by 0
    x2 = gross[2:]
    y2 = (tax[2:] - tax[1:-1])/dg*100.

    # Plot on same axes
    ax2 = ax1.twinx()
    ax2.plot(x1, y1, color='navy', linestyle=':', label='Eff. Tax Rate')
    ax2.plot(x2, y2, color='royalblue', linestyle='-.', label='Marginal Tax Rate')

    percent_formatter = FuncFormatter(lambda x, pos: '{:1.0f}%'.format(x))
    ax2.yaxis.set_major_formatter(percent_formatter)

    # Colour each y-axis separately
    ax2.set_ylim([0, 100])
    ax2.set_ylabel('Tax Rate', color='navy')
    ax2.tick_params('y', colors='navy')

    ax1.set_ylabel('Money [GBP]', color='darkgreen')
    ax1.tick_params('y', colors='darkgreen')

fig.tight_layout()
plt.show()
