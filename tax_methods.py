
import numpy as np
import sys

class RateBrackets(object):
    """Class to calculate the tax to be paid for some given tax scheme,
    eg. Income Tax, National Insurance, Student Finance."""

    def __init__(self, brackets, rates):
        """Construct a tax calculator.

        Args:
            brackets (Iterable): Lower bounds of tax brackets.
                must be of same length as rates.
            rates (Iterable): Marginal tax rate on income above respective lower bracket bound.
                Must be of same length as brackets.
        """

        if len(brackets) != len(rates):
            raise IndexError('There must be the same bracket dividers as rates')
        self.lower_brackets = np.array(brackets)
        self.upper_brackets = np.array(tuple(brackets[1:]) + (sys.maxint,))
        self.rates = np.array(rates)

    def tax(self, income):
        """Calculate total tax on a given gross income."""

        # Ensure we are dealing with 1D np.ndarray
        x = np.array(income).flatten()

        # Broadcast brackets and rates to have extra dimension of same size as x
        ub = np.broadcast_to(self.upper_brackets, (x.shape[0], self.upper_brackets.shape[0]))
        lb = np.broadcast_to(self.lower_brackets, (x.shape[0], self.lower_brackets.shape[0]))
        r = np.broadcast_to(self.rates, (x.shape[0], self.rates.shape[0]))

        # Get amount of income between each bracket (negative if not to be taxed)
        taxable = np.where(income[:, None] < ub, income[:, None] - lb, ub - lb)
        tax = np.sum(taxable * r * (taxable > 0).astype(int), axis=1)
        return tax

IncomeTax = RateBrackets(           [11850, 46350,  150000],
                                    [0.20,  0.40,   0.45])

NationalInsurance = RateBrackets(   [162*52,892*52],
                                    [0.12,  0.02])

StudentFinance = RateBrackets(      [25000],
                                    [0.09])

# Income tax brackets and rates
income_tax = [[ 11850,  46350,  150000],
              [  0.20,   0.40,    0.45]]

# National insurance brackets and rates

rate_student = 0.09     # Rate of student loan repayments
thres_student = 25000.  # Threshold before student loan repayments

def get_income_tax(salary):
    untaxed = salary
    tax = 0.
    for i in reversed(range(len(income_tax))):
        if salary > income_tax[0][i]:
            # Apply tax rate to amount within bracket
            tax += (untaxed - income_tax[0][i]) * income_tax[1][i]
            margin = income_tax[0][i]
    return tax

def get_ni(salary):
    uninsured = salary
    insurance = 0.
    for i in reversed(range(len(nation_ins))):
        if salary > nation_ins[0][i]:
            # Apply nation insurance rate to amount within bracket
            insurance += (uninsured - nation_ins[0][i]) * nation_ins[1][i]
            uninsured = nation_ins[0][i]
    return insurance

def get_slr(salary):
    above_threshold = np.array(salary > thres_student).astype(int)
    return (salary - thres_student) * rate_student * above_threshold
