# Tax Calculator

This is a simple set of Python scripts to calculate the Income Tax, National Insurance, and Student Finance repayments in the United Kingdom, for a certain gross income.

## Getting Started

A command line tool can be found in `tax.py` and can be used as follows:

```console
$ ./tax.py 35
   Gross Income:       35,000.00 £
     Income Tax:   -    4,630.00 £
  National Ins.:   -    3,189.12 £
Student Finance:   -      900.00 £
        Pension:   -      873.72 £
  Take-Home Pay:       25,407.16 £
    Monthly Pay:        2,117.26 £
     Weekly Pay:          488.60 £
```

Note that the argument must be given in thousands.

A stack plot can be generated with the `tax_graph.py` script. The first argument is the maximum gross income to be plotted. Passing the `-f` option will plot the proportions of your gross income that go to certain receipts.

For both scripts, passing the `--no-student` flag will exclude the calculation of student loan repayments.

For both scripts, passing the `--no-pension` flag will exclude calculation of auto-enrolled workplace pension contributions. The `-p` flag allows you to specify a pension contribution rate on your gross income. The `-P` flag allows you to specify a minimum gross income (first argument) before you start paying a given rate (second argument).

### Prerequisites

`numpy`, `matplotlib`, and `colorama` are required packages.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
