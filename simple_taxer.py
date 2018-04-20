#!/usr/bin/env python

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('gross', type=float, help='Gross income')
parser.add_argument('--no-student', dest='student', action='store_false', help='Has no student loan')
args = parser.parse_args()

rate_student = 0.09
thres_student = 25000

income_tax = [[ 11850,  46350,  150000],
              [  0.20,   0.40,    0.45]]

nation_ins = [[702*52, 52*3863],
              [  0.12,    0.02]]

i = 0
gross = args.gross
total = gross

taxed = 0
to_tax = gross
for i in reversed(range(len(income_tax))):
    if gross > income_tax[0][i]:
        taxed += (to_tax - income_tax[0][i]) * income_tax[1][i]
        to_tax = income_tax[0][i]
total -= taxed

insured = 0
to_insure = gross
for i in reversed(range(len(nation_ins))):
    if gross > nation_ins[0][i]:
        insured += (to_insure - nation_ins[0][i]) * nation_ins[1][i]
        to_insure = nation_ins[0][i]
total -= insured

if gross > thres_student:
    student_fee = (gross - thres_student) * rate_student
    total -= student_fee
else:
    student_fee = 0


print '{:>15}:   {:>12,.2f}'.format('Gross Income', gross)
print '{:>15}:   {:>12,.2f}'.format('Income Tax', -taxed)
print '{:>15}:   {:>12,.2f}'.format('National Ins.', -insured)
if args.student:
    print '{:>15}:   {:>12,.2f}'.format('Student Loan', -student_fee)
print '{:>15}:   {:>12,.2f}'.format('Total', total)
print '{:>15}:   {:>12,.2f}'.format('Monthly Pay', total/12)

