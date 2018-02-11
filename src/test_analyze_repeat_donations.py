import unittest
import analyze_repeat_donations as analyzer


class TestAnalyzeRepeatDonations(unittest.TestCase):

    def test_round_dollar_amount(self):
        self.assertEqual(analyzer.round_dollar_amount(0.40), 0)
        self.assertEqual(analyzer.round_dollar_amount(0.0), 0)
        self.assertEqual(analyzer.round_dollar_amount(1.50), 2)
        self.assertEqual(analyzer.round_dollar_amount(100.78), 101)

    def test_compute_percentile(self):
        self.assertEqual(analyzer.compute_percentile([15, 20, 35, 40, 50], 5), 15)
        self.assertEqual(analyzer.compute_percentile([15, 20, 35, 40, 50], 30), 20)
        self.assertEqual(analyzer.compute_percentile([15, 20, 35, 40, 50], 40), 20)
        self.assertEqual(analyzer.compute_percentile([15, 20, 35, 40, 50], 100), 50)
        with self.assertRaises(ValueError):
            analyzer.compute_percentile([15, 20, 35, 40, 50], 0)
            analyzer.compute_percentile([15, 20, 35, 40, 50], -1)
            analyzer.compute_percentile([15, 20, 35, 40, 50], 200)

    def test_is_valid_dollar_amount(self):
        self.assertEqual(analyzer.is_valid_dollar_amount('1425.48'), True)
        self.assertEqual(analyzer.is_valid_dollar_amount('1425.4'), True)
        self.assertEqual(analyzer.is_valid_dollar_amount('1425.'), True)
        self.assertEqual(analyzer.is_valid_dollar_amount('1425'), True)
        self.assertEqual(analyzer.is_valid_dollar_amount('0.48'), True)
        self.assertEqual(analyzer.is_valid_dollar_amount('.48'), True)
        self.assertEqual(analyzer.is_valid_dollar_amount('0.0'), True)
        self.assertEqual(analyzer.is_valid_dollar_amount('-1425.48'), False)
        self.assertEqual(analyzer.is_valid_dollar_amount('14.25.48'), False)
        self.assertEqual(analyzer.is_valid_dollar_amount('1425.483'), False)
        self.assertEqual(analyzer.is_valid_dollar_amount('1,425.48'), False)
        self.assertEqual(analyzer.is_valid_dollar_amount('123456789012.48'), True)
        self.assertEqual(analyzer.is_valid_dollar_amount('1234567890123.48'), False)
        self.assertEqual(analyzer.is_valid_dollar_amount('.'), False)

    def test_check_field_validity_cleanup(self):
        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00629618', 'PEREZ, JOHN A', '90017', '01032017', '40', 'H6CA34245')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertFalse(chk[0])

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00177436', 'DEEHAN, WILLIAM N', '30004', '01312017', '384.', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertTrue(chk[0])
        self.assertTupleEqual(chk[1], ('C00177436', 'DEEHAN, WILLIAM N', '30004', 2017, 384))

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00177436 ', ' DEEHAN, WILLIAM N', '300045436', '01312017', '384.50', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertTrue(chk[0])
        self.assertTupleEqual(chk[1], ('C00177436', 'DEEHAN, WILLIAM N', '30004', 2017, 384.5))

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00384818', 'ABBOTT, JOSEPH', '028956146', '13132017', '250', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertFalse(chk[0])

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00384516', 'SABOURIN, JAMES', '028956146', '01312017', '230.000', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertFalse(chk[0])

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00384516', 'SABOURIN, JAMES', '028956146', '01002018', '384', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertFalse(chk[0])

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00384516', 'SABOURIN, JAMES', '0289561469', '01182018', '384', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertFalse(chk[0])

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00384516', '', '028956146', '01002018', '384', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertFalse(chk[0])

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C003845', 'SABOURIN, JAMES', '028956146', '01132018', '384', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertFalse(chk[0])

        cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id = (
            'C00384516', 'SABOURIN, JAMES', '02895O146', '01202018', '384', '')
        chk = analyzer.check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id)
        self.assertFalse(chk[0])

    def test_create_record_for_output(self):
        cmte_id, zip_code, year, total_amount, nth_percentile, num_contrib = ('C00177436', '30004', 2017, 384, 200, 2)
        self.assertEqual(analyzer.create_record_for_output(cmte_id, zip_code, year, nth_percentile, total_amount,
                                                           num_contrib), 'C00177436|30004|2017|200|384|2\n')

        cmte_id, zip_code, year, total_amount, nth_percentile, num_contrib = ('C00177436', '30004', 2019, 580, 70.50, 5)
        self.assertEqual(analyzer.create_record_for_output(cmte_id, zip_code, year, nth_percentile, total_amount,
                                                           num_contrib), 'C00177436|30004|2019|71|580|5\n')

    def test_extract_required_fields(self):
        record_string = 'C00544767|A|12S|P|201705179053996351|10|IND|MUELLER, BARBARA|MUNCIE|IN|473045926|RETIRED|' \
                        'RETIRED|04042017|5||SA17.885404|1162908||NON CONTRIBUTION ACCOUNT|4051820171405315561'
        (cmte_id, name, zip_code, date, amount, other) = analyzer.extract_required_fields(record_string)
        self.assertTupleEqual((cmte_id, name, zip_code, date, amount, other),
                              ('C00544767', 'MUELLER, BARBARA', '473045926', '04042017', '5', ''))

        record_string = 'C00450189|N|MY|P|201707069066530158|15|IND|WOLFBERG, ROBERT|CHICAGO|IL|60606|' \
                        'PLS FINANCIAL SERVICES|TREASURER|03202017|50||SA11AI.5157|1168288|||4070620171415552675'
        (cmte_id, name, zip_code, date, amount, other) = analyzer.extract_required_fields(record_string)
        self.assertTupleEqual((cmte_id, name, zip_code, date, amount, other),
                              ('C00450189', 'WOLFBERG, ROBERT', '60606', '03202017', '50', ''))

    def test_add_to_repeat_donation_dict(self):
        repeat_donation_dict = {}
        cmte_id, zip_code, transaction_year, transaction_amt = 'C00384516', '02895', 2017, 150.45
        repeat_donation_dict = analyzer.add_to_repeat_donation_dict(cmte_id, zip_code, transaction_year,
                                                                    transaction_amt, repeat_donation_dict)
        self.assertDictEqual(repeat_donation_dict, {('C00384516', '02895', 2017): [[150.45], 150.45]})

        cmte_id, zip_code, transaction_year, transaction_amt = 'C00384516', '02895', 2017, 34.0
        repeat_donation_dict = analyzer.add_to_repeat_donation_dict(cmte_id, zip_code, transaction_year,
                                                                    transaction_amt, repeat_donation_dict)
        self.assertDictEqual(repeat_donation_dict, {('C00384516', '02895', 2017): [[34.0, 150.45], 184.45]})

        cmte_id, zip_code, transaction_year, transaction_amt = 'C00384516', '02895', 2017, 100.24
        repeat_donation_dict = analyzer.add_to_repeat_donation_dict(cmte_id, zip_code, transaction_year,
                                                                    transaction_amt, repeat_donation_dict)
        self.assertDictEqual(repeat_donation_dict, {('C00384516', '02895', 2017): [[34.0, 100.24, 150.45], 284.69]})

        cmte_id, zip_code, transaction_year, transaction_amt = 'C02244516', '02615', 2015, 12
        repeat_donation_dict = analyzer.add_to_repeat_donation_dict(cmte_id, zip_code, transaction_year,
                                                                    transaction_amt, repeat_donation_dict)
        self.assertDictEqual(repeat_donation_dict, {('C00384516', '02895', 2017): [[34.0, 100.24, 150.45], 284.69],
                                                    ('C02244516', '02615', 2015): [[12], 12]})

if __name__ == "__main__":
    unittest.main(verbosity=2)
