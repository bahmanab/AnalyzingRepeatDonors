import sys
import math
import bisect
import time


def is_valid_dollar_amount(string_dollar_amount):
    """
        Checks if string_dollar_amount is a valid dollar amount.
        Acceptable examples 1232.10, 1232.1, and 1232. It should have a maximum precision 14 and maximum scale 2.
        Assumes string_dollar_amount is already stripped from beginning and ending white space characters.
    :param string_dollar_amount: a string that if correct should represent a dollar amount
    :return: True if string_dollar_amount is representing a valid dollar amount with scale 2 and precision 14.
    """
    if string_dollar_amount in ['', '.']:
        return False

    amt_list = string_dollar_amount.split('.')
    # there should be 1 or 2 string of digits on the sides of '.' for a valid dollar amount
    if len(amt_list) not in [1, 2]:
        return False

    # both side of decimal point has only digits or at most one side can be empty
    if all((c.isdigit() or c == '') for c in amt_list):
        if len(amt_list) == 2:
            if len(amt_list[1]) <= 2 and len(amt_list[0]) + len(amt_list[1]) <= 14:
                return True
        else:   # len(amt_list) equals 1
            if len(amt_list[0]) <= 14:
                return True
    return False


def round_dollar_amount(amount):
    """
        Given a dollar amount with two decimal digits drop anything below $.50 and round anything from $.50 and up
        to the next dollar and returns the rounded value.

    :param amount: a float containing dollar amount
    :return: an integer, rounded value of the dollar amount
    """
    return int((amount // 1) + (0 if (amount % 1.0) < 0.50 else 1))


def open_files(file_list):
    """
        Opens all the files in the file list and return their handles.
    :param file_list: a list consisting a tuple for each file to be opened.
                      tuple has the form (file_path, file_opening_mode)
    :return: a tuple of file handles with the same order as the tuples in the file_list
    """
    file_handles = ()
    for file_item in file_list:
        file_path, opening_mode = file_item
        try:
            file_handles += (open(file_path, opening_mode),)
        except OSError:
            print('An error occurred while opening file: ', file_path)
            sys.exit()

    return file_handles


def close_files(file_handle_list):
    """
        Closes all file provided in the file_handle_list.
    :param file_handle_list: a list of file handles.
    """
    for file in file_handle_list:
        try:
            file.close()
        except:
            print('An error occurred while closing files.')
            raise


def create_record_for_output(cmte_id, zip_code, transaction_year, nth_percentile, total_amount_contributions,
                             total_number_of_contributions):
    """
        Given all the information required returns the record as a string with the format of output is:
            cmte_id|zip_code|transaction_year|nth_percentile|total_amount_contributions|total_number_of_contributions

    :param cmte_id: donation recipient id
    :param zip_code: a string containing zip code of donor
    :param transaction_year: an integer containing year of donation
    :param nth_percentile: nth percentile of donation from repeat donors to the recipient cmte_id in transaction_year
                           that has been read till now
    :param total_amount_contributions: total amount of contribution from repeat donor to the recipient cmte_id in
                                          transaction_year
    :param total_number_of_contributions: total number of contributions from repeat donor to the recipient cmte_id in
                                          transaction_year
    :return: a | delimited string including the record for writing to output file
    """

    output_record = [cmte_id, zip_code, str(transaction_year), str(round_dollar_amount(nth_percentile)),
                     str(total_amount_contributions), str(total_number_of_contributions)]

    return '|'.join(output_record) + '\n'


def compute_percentile(ordered_list, p):
    """
        Given a list of numbers sorted in ascending order and a percentile value greater than 0 and less than equal 100,
        returns pth_percentile of the list using the nearest-rank method.
    :param ordered_list: a list of numbers sorted in ascending order
    :param p: a value between 0 and 100 which we want to find the pth percentile of the list given
    :return: pth_percentile of the list
    """
    if p <= 0 or p > 100:
        raise ValueError('Percentage value should be between 0 and 100.')

    # index of pth_percentile value in the list, adjusting for the fact that python uses zero-based indexing
    n = math.ceil(p/100 * len(ordered_list)) - 1

    return round_dollar_amount(ordered_list[n])


def add_to_repeat_donation_dict(cmte_id, zip_code, transaction_year, transaction_amt, repeat_donation_dict):
    """
        Adds the specified donation to the repeat_donation_dict and keeps the list of donations, sorted in an ascending
        order. It also updates the total_amount_of_contributions.
        This function needs bisect module.
    :param cmte_id: donation recipient id
    :param zip_code: a string containing zip code of donor
    :param transaction_year: an integer containing year of donation
    :param transaction_amt: a float containing amount of transaction in dollar
    :param repeat_donation_dict: dictionary of repeat donations with the key (cmte_id, zip_code, year) and the value
                                 which is a list with the first element being a list of all donations from repeat
                                 donors to the recipient cmte_id at the zip_code during the transaction_year that has
                                 been processed till now. The second element of that list is the sum of all donations
                                 which are mentioned in previous list.
                                 example:
                                 An item of dictionary can be:
                                 {('C00384516', '02895', 2017): [[50, 110, 125, 300], 585]}
    :return: the updated repeat_donation_dict
    """
    # add a blank initial value if there is still no donation to this recipient
    # in transaction_year with the specified zip_code
    if (cmte_id, zip_code, transaction_year) not in repeat_donation_dict:
        repeat_donation_dict[(cmte_id, zip_code, transaction_year)] = [[], 0]

    # insert the new transaction amount
    bisect.insort(repeat_donation_dict[(cmte_id, zip_code, transaction_year)][0], transaction_amt)

    # update the total amount of contributions
    repeat_donation_dict[(cmte_id, zip_code, transaction_year)][1] += transaction_amt

    return repeat_donation_dict


def check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id):
    """
        Returns a tuple (validity, fields). If any of the provided fields are malformed or incorrect or other_id is not
        empty, it returns False for validity and an empty list for fields. If all fields are valid it cleans up the
        fields and returns them.
        Cleanups include: striping white spaces from beginning and end of fields, returning only first five digits of
        zip_code, returning transaction_year as an integer instead of transaction_dt and changing the type of
        transaction_amt to float before returning.
    :param cmte_id: donation recipient id
    :param name: a string containing name of donor
    :param zip_code: a string containing zip code of donor
    :param transaction_dt: an string containing date of donation
    :param transaction_amt: a string containing amount of transaction in dollar
    :param other_id: a string which is empty when the donation is from an individual
    :return: a tuple in this form (validity, (cmte_id, name, zip_code, transaction_year, transaction_amt))
    """

    # white space stripping and checks
    other_id = other_id.strip()
    if other_id != '':
        return False, ()

    cmte_id = cmte_id.strip()
    if len(cmte_id) != 9 or (not cmte_id.isalnum()):
        return False, ()

    name = name.strip()
    if len(name) > 200 or name == '':
        return False, ()

    zip_code = zip_code.strip()
    # assumption is that zip_code should be either 5 or 9 digits.
    if not (len(zip_code) == 5 or len(zip_code) == 9) or not zip_code.isdigit():
        return False, ()

    transaction_dt = transaction_dt.strip()
    # transaction_dt should have the form MMDDYYYY
    if (len(transaction_dt) != 8 or (not transaction_dt.isdigit()) or
            (int(transaction_dt[0:2]) < 1 or int(transaction_dt[0:2]) > 12) or
            (int(transaction_dt[2:4]) < 1 or int(transaction_dt[2:4]) > 31)):
        return False, ()

    transaction_amt = transaction_amt.strip()
    if not is_valid_dollar_amount(transaction_amt):
        return False, ()

    validity = True      # no field-check failed
    return validity, (cmte_id, name, zip_code[0:5], int(transaction_dt[-4:]), float(transaction_amt))


def extract_required_fields(record_string):
    """
        Extract the all the fields from a record_string which is raw record with fields separated by |
        and return required fields.

    :param record_string: raw record for a donation according to FEC description
    :return: a tuple including required fields:
             (CMTE_ID, NAME, ZIP_CODE, TRANSACTION_DT, TRANSACTION_AMT, OTHER_ID)

    raw record header file with associated indexes:
           0       1         2      3               4         5              6         7    8    9     10
           CMTE_ID,AMNDT_IND,RPT_TP,TRANSACTION_PGI,IMAGE_NUM,TRANSACTION_TP,ENTITY_TP,NAME,CITY,STATE,ZIP_CODE,
           11       12         13             14              15       16      17       18      19        20
           EMPLOYER,OCCUPATION,TRANSACTION_DT,TRANSACTION_AMT,OTHER_ID,TRAN_ID,FILE_NUM,MEMO_CD,MEMO_TEXT,SUB_ID
    """
    all_fields = record_string.split('|')
    required_fields_indexes = [0, 7, 10, 13, 14, 15]

    return (all_fields[i] for i in required_fields_indexes)


def process_data_stream(input_file, percentile_file, output_file):
    """
        This function process a data_stream of donation records by opening input_file that is formatted based on FEC
        description. It uses the percentile value that is supposed to be in the first line of percentile_file and write
        the output_file which will only contain records from repeat donors.
    :param input_file: a string containing the location of input file.
    :param percentile_file: a string containing the location of percentile file.
    :param output_file: a string containing the location of output_file
    """

    file_handles = open_files([(input_file, 'r'), (percentile_file, 'r'), (output_file, 'w')])
    input_handle, percentile_handle, output_handle = file_handles

    # read the percentile
    first_line = percentile_handle.readline()  # assume the percentile is at the first line
    percentile = int(first_line.strip())
    if percentile < 1 or percentile > 100:
        raise ValueError('The provided percentage should be between 1 and 100.')

    donor_dict = {}
    repeat_donation_dict = {}

    for line in input_handle:
        (cmte_id, name, zip_code, transaction_dt, transaction_amt, other_id) = extract_required_fields(line)

        (validity, fields) = check_field_validity_cleanup(cmte_id, name, zip_code, transaction_dt, transaction_amt,
                                                          other_id)
        if not validity:  # skip this record if any of the required fields are not valid
            continue

        (cmte_id, name, zip_code, transaction_year, transaction_amt) = fields

        donor = (name, zip_code)
        if donor in donor_dict:
            if donor_dict[donor] > transaction_year:
                # keep record of earliest year a donor has donated
                donor_dict[donor] = transaction_year
            elif donor_dict[donor] < transaction_year:   # this is a repeat donor
                repeat_donation_dict = add_to_repeat_donation_dict(cmte_id, zip_code, transaction_year, transaction_amt,
                                                                   repeat_donation_dict)
                nth_percentile = compute_percentile(repeat_donation_dict[(cmte_id, zip_code, transaction_year)][0],
                                                    percentile)
                total_amount_contributions = round_dollar_amount(repeat_donation_dict[(cmte_id, zip_code,
                                                                                       transaction_year)][1])
                total_number_of_contributions = len(repeat_donation_dict[(cmte_id, zip_code, transaction_year)][0])
                output_record = create_record_for_output(cmte_id, zip_code, transaction_year, nth_percentile,
                                                         total_amount_contributions, total_number_of_contributions)

                output_handle.write(output_record)
        else:
            # add this donor to donor list
            donor_dict[donor] = transaction_year

    close_files([input_handle, percentile_handle, output_handle])


if __name__ == "__main__":
    # if optional -time argument is entered, time the code
    if len(sys.argv) >= 5 and sys.argv[4] == '-time':
        start_time = time.time()

    # get the location of input and output file from command line
    try:
        input_path = sys.argv[1]
        percentile_path = sys.argv[2]
        output_path = sys.argv[3]
    except:
        raise Exception(('You need to enter the following paths as command arguments: input_file, percentile_file, ',
                        'and output_file!'))

    process_data_stream(input_path, percentile_path, output_path)

    # if optional -time argument is entered, print the run time
    if len(sys.argv) >= 5 and sys.argv[4] == '-time':
        print("--- running time: %s seconds ---" % (time.time() - start_time))
