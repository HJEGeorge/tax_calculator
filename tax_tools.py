
import numpy as np
import sys
from abc import ABCMeta, abstractmethod


class Tax(object):
    """Abstract class to calculate income-dependent payments."""
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def tax(self, income):
        """Return tax or payment for a given taxable income."""
        pass


class TaxBracket(Tax):
    """Class to calculate the amount to be paid for some income-dependent payment,
    eg. Income Tax, National Insurance, Student Finance.
    
    Args:
        brackets (iterable): Lower bounds of tax brackets.
            must be of same length as rates.
        rates (iterable): Marginal tax rate on income above respective lower bracket bound.
            Must be of same length as brackets.
    """

    def __init__(self, brackets, rates):
        
        max_int = sys.maxsize

        if len(brackets) != len(rates):
            raise IndexError('There must be the same bracket dividers as rates')
        self.lower_brackets = np.array(brackets)
        self.upper_brackets = np.array(tuple(brackets[1:]) + (max_int,))
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
        taxable = np.where(x[:, None] < ub, x[:, None] - lb, ub - lb)
        tax = np.sum(taxable * r * (taxable > 0).astype(int), axis=1)

        if tax.shape == (1,):
            tax = tax[0]
        
        return tax


class TaxCode(Tax):
    """Class to calculate the overall payments for a collection of income-dependent payments.
    
    Args:
        *tax_brackets: TaxBracket objects to form the overall tax code.
    """

    def __init__(self, *tax_brackets):
        self.tax_brackets = list(tax_brackets)
    
    def tax(self, income):
        """Calculate total on a given gross income."""
        
        total = 0
        for tb in self.tax_brackets:
            total += tb.tax(income)
    

IncomeTax = TaxBracket([11850, 46350, 150000],
                       [0.20,  0.40,   0.45])

NationalInsurance = TaxBracket([162 * 52, 892 * 52],
                               [0.12,      0.02])

StudentFinance = TaxBracket([25000],
                            [0.09])

StatutoryPension = TaxBracket([5876, 45000],
                              [0.03,   0.0])


def generate_tax_code(student=False, stat_pension=True, private_pension=None):
    """Create a TaxCode object from specified conditions.
    
    A call with default arguments will include Income Tax, National Insurance, and auto-enrolled
    Statutory Pension contributions.
    
    Args:
        student (bool, opt.): If true, include student loan repayments.
        stat_pension (bool, opt.): If true, include Statutory Pension contributions.
        private_pension (list, opt.): Specify private pension contributions.
            First argument is the marginal rate.
            Second argument is the threshold above which this is paid (defaults to 0).
            If private_pension is specified, Statutory Pension will be ignored.
    """
    
    tax_code = [IncomeTax, NationalInsurance]
    
    if student:
        tax_code.append(StudentFinance)
    
    if stat_pension and private_pension is None:
        tax_code.append(StatutoryPension)
    
    if private_pension is not None:
        rate = [private_pension[0]]
        
        try:
            threshold = [private_pension[1]]
        except IndexError:
            threshold = [0]
        
        tax_code.append(TaxBracket(rate, threshold))

    return tax_code
