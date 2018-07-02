# -*- coding: utf-8 -*-

import colorama
import numpy as np
import sys
from abc import ABCMeta, abstractmethod, abstractproperty


class PayrollCommitment(object):
    """Abstract class to handle an income-dependent payment to be deducted from one's pay."""
    
    __metaclass__ = ABCMeta

    ALLOWANCE = 11850               # Personal allowance (reduces taxable income)
    ALLOWANCE_THRESHOLD = 100000    # Gross income before allowance begins to decrease
    ALLOWANCE_DEC_RATE = 0.50       # Rate at which allowance decreases above threshold
    
    # Supported colorama colors for printing to console
    COLORS = {'g': colorama.Fore.GREEN,
              'r': colorama.Fore.RED,
              'w': colorama.Fore.RESET}
    
    @classmethod
    def personal_allowance_upper(cls):
        """Return the gross income above which the personal allowance is zero."""
        
        return cls.ALLOWANCE_THRESHOLD + cls.ALLOWANCE / cls.ALLOWANCE_DEC_RATE
    
    @abstractproperty
    def name(self):
        """Return name of payment."""
        
        pass
    
    @classmethod
    def money_string(cls, **kwargs):
        """Return a string for console output, detailing a money amount and its title/name.
        
        
        """
        
        if 'amount' not in kwargs:
            kwargs['amount'] = 0
        
        if 'color' not in kwargs:
            if kwargs['amount'] > 0:
                kwargs['color'] = cls.COLORS['g']
            else:
                kwargs['color'] = cls.COLORS['r']
        
        c = kwargs['color']
        if c not in cls.COLORS.values():
            kwargs['color'] = cls.COLORS[c]
        
        if 'sign' not in kwargs:
            if kwargs['amount'] >= 0:
                kwargs['sign'] = ' '
            else:
                kwargs['sign'] = '-'
            
        kwargs['abs_amount'] = abs(kwargs['amount'])
        
        output = '{title:>20}:   {color}{sign}{abs_amount:>12,.2f} £{white}'.format(
                white=cls.COLORS['w'], **kwargs)
        
        return output

    @classmethod
    def personal_allowance(cls, income):
        """Return the personal allowance for a given income."""
        
        # Shift income and thresholds such that if (shifted_income > 0) start reducing allowance
        upper_bound = cls.personal_allowance_upper() - cls.ALLOWANCE_THRESHOLD
        shifted_income = income - cls.ALLOWANCE_THRESHOLD
        
        # Get 1 if below the upper threshold, else 0
        below_threshold = int(shifted_income <= upper_bound)
        
        # Get 1 if above the lower threshold, else 0
        within_threshold = int(shifted_income > 0)
        
        # Get fraction of allowance to reduce allowance by
        # Note this will be larger than the allowance for incomes above the upper threshold
        # but will also then be multiplied by 0
        reduction = shifted_income / upper_bound * cls.ALLOWANCE_DEC_RATE
        
        return cls.ALLOWANCE * below_threshold * (1 - within_threshold * reduction)


class PrivatePension(PayrollCommitment):
    def __init__(self, name, rate):
        self._name = name
        self.rate = rate
    
    @property
    def name(self):
        return self._name
    
    def pension_contribution(self, income):
        return self.rate * income
    
    def pension_cost_and_cont(self, income, marginal_tax_rate):
        cont = self.pension_contribution(income)
        cost = cont * (1. - marginal_tax_rate)
        return cost, cont
    
    def pension_cost(self, income, marginal_tax_rate):
        return self.pension_cost_and_cont(income, marginal_tax_rate)[0]
    
    def pension_string(self, income, marginal_tax_rate):
        cost, cont = self.pension_cost_and_cont(income, marginal_tax_rate)
        output = '{}\n{}'.format(
                self.money_string(title=self.name, amount=-cost),
                self.money_string(title='(Pot) ' + self.name, amount=cont, color=self.COLORS['w']))
        return output


class Tax(PayrollCommitment):
    """Abstract class to represent a payroll tax payment."""
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def tax(self, income):
        """Return tax for a given income."""
        
        pass

    def tax_string(self, income):
        """Return a string detailing the name and amount of each tax for a given gross income."""
        
        return self.money_string(title=self.name, amount=-self.tax(income))


class TaxBracket(Tax):
    """Class to calculate the amount to be paid for some income-dependent payment,
    eg. Income Tax, National Insurance, Student Finance.
    
    :param name: Name of tax.
    :type name: str
    :param brackets: Lower bounds of tax brackets. Must be of same length as rates.
    :type brackets: list(float)
    :param rates: Marginal tax rate on income above respective lower bracket bound.
        Must be of same length as brackets.
    :type rates: list(float)
    """

    def __init__(self, name, brackets, rates):
        
        max_int = sys.maxsize

        if len(brackets) != len(rates):
            raise IndexError('There must be the same bracket dividers as rates')
        
        self._name = name
        self.lower_brackets = np.array(brackets)
        self.upper_brackets = np.array(tuple(brackets[1:]) + (max_int,))
        self.rates = np.array(rates)
    
    @property
    def name(self):
        return self._name

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
        t = np.sum(taxable * r * (taxable > 0).astype(int), axis=1)

        if t.shape == (1,):
            t = t[0]
        
        return t
    
    def get_marginal_rate(self, income):
        """Return the marginal tax rate for a given income."""
        
        thresholds = sorted(self.lower_brackets)
        rate = 0
        i = 0
        while income > thresholds[i] and i < len(thresholds):
            rate = self.rates[i]
            i += 1
        return rate


class TaxCode(Tax):
    """Class to calculate the overall payments for a collection of income-dependent payments.
    
    These payments include:
        Standard taxes that apply to taxable income only eg. Income Tax;
        Gross taxes that apply to gross income eg. National Insurance and student loan repayments;
        Pensions that contribute a proportion of your gross income accounting for tax relief.
    """

    def __init__(self, name=''):
        self._name = name
        self.standard_taxes = []
        self.pensions = []
        self.gross_taxes = []
    
    @property
    def name(self):
        return self._name
    
    def add_standard_tax(self, tax):
        self.standard_taxes.append(tax)
    
    def add_pensions(self, pension):
        self.pensions.append(pension)

    def add_gross_tax(self, tax):
        self.gross_taxes.append(tax)

    def marginal_standard_tax_rate(self, income, gross=True):
        """Return the total marginal tax rate for a given income for all standard taxes.
        
        :param income: Gross income for which to calculate the marginal tax rate.
        :type income: float
        :param gross: If true, then income is defined to be the taxable income
        :type gross: bool
        :return: Marginal tax rate.
        :rtype: float
        """
        
        if gross:
            taxable_income = self.get_taxable_income(income)
        else:
            taxable_income = income
        
        marginal_tax_rate = .0
        for tax in self.standard_taxes:
            marginal_tax_rate += tax.get_marginal_rate(taxable_income)
    
        return marginal_tax_rate
    
    def standard_tax(self, income, gross=True):
        """Calculate the total standard tax payments for a given income.
        
        :param income: Gross income for which to calculate the tax payment.
        :type income: float
        :param gross: If true, then income is defined to be the taxable income
        :type gross: bool
        :return: Tax to be paid.
        :rtype: float
        """
        
        if gross:
            taxable_income = income - self.personal_allowance(income)
        else:
            taxable_income = income
        
        total = 0
        for tax in self.standard_taxes:
            total += tax.tax(taxable_income)
        
        return total
    
    def gross_tax(self, income):
        """Calculate the total payments for a given gross income from non-standard taxes."""
        
        total = 0
        for tax in self.gross_taxes:
            total += tax.tax(income)
        
        return total
    
    def pension_cost(self, income):
        """Calculate private pension payments for a given gross income."""
        
        marginal_tax_rate = self.marginal_standard_tax_rate(income)
        
        pen = 0
        for pension in self.pensions:
            pen += pension.pension_cost(income, marginal_tax_rate)
        
        return pen
    
    def tax(self, income):
        """Calculate total tax on a given gross income."""

        return self.standard_tax(income) + self.gross_tax(income)
    
    def get_taxable_income(self, income):
        """Calculate the taxable income for a given gross income."""
        
        taxable_income = income - self.personal_allowance(income)
        
        return taxable_income * int(taxable_income > 0)
        
    def tax_string(self, income):
        """Return string detailing the name and amount of each tax to be paid for an income."""
        
        taxable_income = self.get_taxable_income(income)
        take_home_pay = income - self.tax(income) - self.pension_cost(income)
        marginal_tax_rate = self.marginal_standard_tax_rate(taxable_income, gross=False)
        
        output = '{}\n{}\n'.format(
                self.money_string(title='Gross Income', amount=income, color='g'),
                self.money_string(title='Taxable Income', amount=taxable_income, color='g'))
        for tb in self.standard_taxes:
            output += '{}\n'.format(tb.tax_string(taxable_income))
        for tb in self.gross_taxes:
            output += '{}\n'.format(tb.tax_string(income))
        for tb in self.pensions:
            output += '{}\n'.format(tb.pension_string(income, marginal_tax_rate))
        
        output += '{}\n{}\n{}'.format(
                self.money_string(title='Take-Home Pay', color='g', amount=take_home_pay),
                self.money_string(title='Monthly Pay', color='g', amount=take_home_pay / 12),
                self.money_string(title='Weekly Pay', color='g', amount=take_home_pay / 52))
        
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


def get_statutory_pension(rate=0.03):
    """Return an instance of TaxBracket to represent statutory workplace pension contributions."""
    
    return TaxBracket('Pension',
                      [5876, 45000],
                      [rate, 0.0])


def generate_tax_code(student=False, pension=True, statutory_pension=0.03, private_pension=None):
    """Create a TaxCode object from specified conditions.
    
    A call with default arguments will include Income Tax, National Insurance, and auto-enrolled
    Statutory Pension contributions.
    
    :param student: If true, include student load repayments.
    :type student: bool
    :param pension: If true, include statutory pension, else exclude it, even if rate is specified.
    :type pension: bool
    :param statutory_pension: Rate of thresholded income to contribute to statutory pension.
        Defaults to 0.03
    :type statutory_pension:
    :param private_pension: Rate on gross income to contribute to a private pension.
        If given, other pension arguments are ignored.
    :type private_pension: float
    :return: A TaxCode object to calculate appropriate payments.
    :rtype: TaxCode
    """
    
    tax_code = TaxCode()
    
    tax_code.add_standard_tax(IncomeTax)
    tax_code.add_gross_tax(NationalInsurance)
    
    if student:
        tax_code.add_gross_tax(StudentFinance)
    
    if private_pension is not None:
        tax_code.add_pensions(PrivatePension('Priv. Pension', private_pension))
        
    elif pension:
        # Statutory pensions cannot get tax relief and apply to a threshold of income
        # so they count as a gross tax
        tax_code.add_gross_tax(get_statutory_pension(statutory_pension))

    return tax_code
