# -*- coding: utf-8 -*-

import colorama
import numpy as np
import sys
from abc import ABCMeta, abstractmethod


class Tax(object):
    """Abstract class to calculate income-dependent payments."""
    
    __metaclass__ = ABCMeta

    PERSONAL_ALLOWANCE = 11850
    PERSONAL_ALLOWANCE_THRESHOLD = 100000
    PERSONAL_ALLOWANCE_DEC_RATE = 0.50
    
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
        pass
    
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

    @classmethod
    def personal_allowance(cls, income):
        """Return the personal allowance for a given gross income."""
        
        if income > cls.PERSONAL_ALLOWANCE_THRESHOLD + cls.PERSONAL_ALLOWANCE / cls.PERSONAL_ALLOWANCE_DEC_RATE:
            return 0
        elif income > cls.PERSONAL_ALLOWANCE_THRESHOLD:
            return cls.PERSONAL_ALLOWANCE - (income - cls.PERSONAL_ALLOWANCE_THRESHOLD) * cls.PERSONAL_ALLOWANCE_DEC_RATE
        else:
            return cls.PERSONAL_ALLOWANCE
    

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
        """Calculate total tax on a given income."""

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
        """Return a string with payment name and amount to be paid for a given income."""
        
        amount = self.tax(income)

        return self.money_string(title=self.name, amount=-amount)


class TaxCode(Tax):
    """Class to calculate the overall payments for a collection of income-dependent payments.
    
    Attributes:
        standard_taxes (Iterable): TaxBracket objects that apply to one's taxable income
        relieving_taxes (Iterable): TaxBracket objects that apply to gross income.
            These reduce one's taxable income.
        gross_taxes (Iterable): TaxBracket objects that apply to gross income.
            These do not reduce one's taxable income.
    """

    def __init__(self):
        self.standard_taxes = []
        self.relieving_taxes = []
        self.gross_taxes = []
    
    def add_standard_tax(self, tax):
        self.standard_taxes.append(tax)

    def add_relieving_tax(self, tax):
        self.relieving_taxes.append(tax)

    def add_gross_tax(self, tax):
        self.gross_taxes.append(tax)

    def relieving_tax(self, income):
        """Calculate the total payments for relieving taxes for a given gross income."""

        total = 0
        for tax in self.relieving_taxes:
            total += tax.tax(income)
        
        return total
    
    def standard_tax(self, income, gross=True):
        """Calculate the total standard tax payments for a given income.
        
        Args:
            income (float): Gross or taxable income, depending on gross optional argument.
            gross (bool, opt.): If true, calculate taxable income first,
        """
        
        if gross:
            taxable_income = income - self.relieving_tax(income) - self.personal_allowance(income)
        else:
            taxable_income = income
        
        total = 0
        for tax in self.standard_taxes:
            total += tax.tax(taxable_income)
        
        return total
    
    def gross_tax(self, income):
        """Calculate the total non-relievable tax payments for a given gross income."""
        
        total = 0
        for tax in self.gross_taxes:
            total += tax.tax(income)
        
        return total
    
    def tax(self, income):
        """Calculate total tax on a given gross income."""

        total = self.relieving_tax(income)
        total += self.standard_tax(income - total - self.personal_allowance(income), gross=False)
        total += self.gross_tax(income)
        
        return total
    
    def get_taxable_income(self, income):
        """Calculate the taxable income for a given gross income."""
        
        taxable_income = income - self.relieving_tax(income) - self.personal_allowance(income)
        
        if taxable_income > 0:
            return taxable_income
        else:
            return 0
        
    def tax_string(self, income):
        """Return string detailing the name and amount of each tax to be paid for an income."""
    
        taxable_income = self.get_taxable_income(income)
        
        output = '{}\n{}\n'.format(
                self.money_string(title='Gross Income', amount=income, color='g'),
                self.money_string(title='Taxable Income', amount=taxable_income, color='g'))
        
        take_home = income - self.tax(income)
        
        for tb in self.standard_taxes:
            output += '{}\n'.format(tb.tax_string(taxable_income))
        for tb in self.gross_taxes:
            output += '{}\n'.format(tb.tax_string(income))
        for tb in self.relieving_taxes:
            output += '{}\n'.format(tb.tax_string(income))
        
        output += '{}\n{}\n{}'.format(
                self.money_string(title='Take-Home Pay', color='g', amount=take_home),
                self.money_string(title='Monthly Pay', color='g', amount=take_home / 12),
                self.money_string(title='Weekly Pay', color='g', amount=take_home / 52))
        
        return output

IncomeTax = TaxBracket('Income Tax',
                       [0,    34500, 150000],
                       [0.20, 0.40,  0.45])

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
    
    tax_code = TaxCode()
    
    tax_code.add_standard_tax(IncomeTax)
    tax_code.add_gross_tax(NationalInsurance)
    
    if student:
        tax_code.add_gross_tax(StudentFinance)
    
    if stat_pension and private_pension is None:
        tax_code.add_relieving_tax(StatutoryPension)
    
    if private_pension is not None:
        rate = [private_pension[0]]
        
        try:
            threshold = [private_pension[1]]
        except IndexError:
            threshold = [0]
        
        tax_code.add_relieving_tax(TaxBracket('Pension', threshold, rate))

    return tax_code
