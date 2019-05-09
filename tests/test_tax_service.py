import unittest
from tax_service import take_home_pay

class Test(unittest.TestCase):

    def setUp(self) -> None:
        pass


    def test_zero_income_returns_zero(self):
        self.assertEqual(take_home_pay(0), 0)


    def test_2019_tax_rates(self):
        # based on data collected from
        # https://www.tax.service.gov.uk/estimate-paye-take-home-pay/
        # on May 9th 2019
        data = [
            # ([income, student_loan_amount, pension], take_home_pay (yearly))
            ([28000, 0, False], 22577.64),
            ([15500, 0, False], 14077.64),
            ([55200, 0, False], 40555.44),
        ]
        for case in data:
            self.assertEqual(take_home_pay(*case[0]), case[1])