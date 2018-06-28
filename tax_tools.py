# -*- coding: utf-8 -*-

import colorama
import numpy as np
import sys
from abc import ABCMeta, abstractmethod


class Tax(object):
    """Abstract class to calculate income-dependent payments."""
    
    __metaclass__ = ABCMeta
    
    COLORS = {'g': colorama.Fore.GREEN,
              'r': colorama.Fore.RED,
              'w': colorama.Fore.RESET}
    
    @abstractmethod
    def tax(self, income):
        """Return tax or payment for a given taxable income."""
        pass
    
    @abstractmethod
    def tax_string(self, income):
        """Return a string detailing the name and amount of each tax for a given gross income"""
    
    @classmethod
    def money_string(cls, **kwargs):
        """Return a string for console output, detailing a money amount and its title/name.
        
        Args:
            **kwargs:
        """
        
        if 'amount' not in kwargs:
            kwargs['amount'] = 0
        
        if 'color' not in kwargs:
            if kwargs['amount'] > 0:
                kwargs['color'] = cls.COLORS['g']
            else:
                kwargs['color'] = cls.COLORS['r']
        
        if kwargs['color'] not in cls.COLORS.values():
            kwargs['color'] = cls.COLORS[kwargs['color']]
        
        if 'sign' not in kwargs:
            if kwargs['amount'] >= 0:
                kwargs['sign'] = ' '
            else:
                kwargs['sign'] = '-'
            
        kwargs['abs_amount'] = abs(kwargs['amount'])
        
        output = '{title:>15}:   {color}{sign}{abs_amount:>12,.2f} £{white}'.format(
                white=cls.COLORS['w'], **kwargs)
        
        return output
    

class TaxBracket(Tax):
    """Class to calculate the amount to be paid for some income-dependent payment,
    eg. Income Tax, National Insurance, Student Finance.
    
    Args:
        name (str): Name of tax.
        brackets (iterable): Lower bounds of tax brackets.
            Must be of same length as rates.
        rates (iterable): Marginal tax rate on income above respective lower bracket bound.
            Must be of same length as brackets.
    """

    def __init__(self, name, brackets, rates):
        
        max_int = sys.maxsize

        if len(brackets) != len(rates):
            raise IndexError('There must be the same bracket dividers as rates')
        
        self.name = name
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
    
    def tax_string(self, income):
        """Return a string with tax name and amount to be paid for a given gross income."""
        
        amount = self.tax(income)

        return self.money_string(title=self.name, amount=-amount)


class TaxCode(Tax):
    """Class to calculate the overall payments for a collection of income-dependent payments.
    
    Args:
        *tax_brackets: TaxBracket objects to form the overall tax code.
    """

    def __init__(self, *tax_brackets):
        self.tax_brackets = tax_brackets
    
    def tax(self, income):
        """Calculate total on a given gross income."""
        
        total = 0
        for tb in self.tax_brackets:
            total += tb.tax(income)
        return total
    
    def tax_string(self, income):
        """Return string detailing the name and amount of each tax to be paid for an income."""
    
        output = self.money_string(title='Gross Income', amount=income, color='g')
        
        take_home = income - self.tax(income)
        
        for tb in self.tax_brackets:
            output += '\n{}'.format(tb.tax_string(income))
        
        output += '\n{}'.format(self.money_string(
                title='Take-Home Pay', color='g', amount=take_home))
        output += '\n{}'.format(self.money_string(
                title='Monthly Pay', color='g', amount=take_home / 12))
        output += '\n{}'.format(self.money_string(
                title='Weekly Pay', color='g', amount=take_home / 52))
        
        return output


allowance = 11850
base_rate = 0.20
reduce_rate = 0.50
reduce_start = 100000
reduce_end = reduce_start + allowance / reduce_rate

IncomeTax = TaxBracket('Income Tax',
                       [allowance, 46350, reduce_start,                    reduce_end, 150000],
                       [base_rate, 0.40,  0.40 + reduce_rate * base_rate,  0.40,       0.45])

NationalInsurance = TaxBracket('National Ins.',
                               [162 * 52, 892 * 52],
                               [0.12,     0.02])

StudentFinance = TaxBracket('Student Finance',
                            [25000],
                            [0.09])

StatutoryPension = TaxBracket('Pension',
                              [5876, 45000],
                              [0.03, 0.0])


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
        
        tax_code.append(TaxBracket('Pension', rate, threshold))

    return TaxCode(*tax_code)
