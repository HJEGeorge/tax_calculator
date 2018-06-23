# Tax Calculator

This is a simple set of Python scripts to calculate the Income Tax, National Insurance, and Student Finance repayments in the United Kingdom, for a certain gross income.

## Getting Started

A command line tool can be found in `tax.py` and can be used as follows:

```console
$ ./tax.py 35
   Gross Income:       35,000.00 £
     Income Tax:   -    4,630.00 £
  National Ins.:   -    3,189.12 £
   Student Loan:   -      900.00 £
       Takehome:       26,280.88 £
    Monthly Pay:        2,190.07 £
     Weekly Pay:          505.40 £
```

Note that the argument must be given in thousands.

A stack plot can be generated with the `tax_graph.py` script. The first argument is the maximum gross income to be plotted.

Passing the `--no-student` flag will exclude the calculation of student loan repayments.

### Prerequisites

`numpy`, `matplotlib`, and `colorama` are required packages.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
