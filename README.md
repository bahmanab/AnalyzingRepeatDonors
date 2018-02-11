# Table of Content
1. [Running the Code](README.md#running-the-Code)
2. [Assumptions](README.md#assumptions)
3. [Output File Format](README.md#output-file-format)
4. [A Short Description of the Code](README.md#a-short-description-of-the-code)
5. [Code Requirements and Testing](README.md#code-requirements-and-testing)


# Analyzing Repeat Donors
## Running the Code
The command format for running the code is:

```python ./src/analyze_repeat_donations.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt```

Obviously the name or path of the files can be different from above. However, the order should be the same, meaning that the first file is the input data in the format described by [FEC](http://classic.fec.gov/finance/disclosure/metadata/DataDictionaryContributionsbyIndividuals.shtml). The second file is the file which specifies the percentile value. The third file is the output file. 

There is an optional parameter `-time` that if needed should be entered as the fourth input argument: 

```python ./src/analyze_repeat_donations.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt -time```

If provided, the code prints the run time at the end of each run.

## Assumptions
- Percentile input value will be read from first line of percentile file. 
- Input data in the format described by [FEC](http://classic.fec.gov/finance/disclosure/metadata/DataDictionaryContributionsbyIndividuals.shtml).
- Repeat donors are defined as any donor which has donated to any recipient in any previous years. 
- Only the first 5 digits of zip code is considered in analyzing data.
- Unique individual is define as any two contributor which has identical name and zip code at the same time.
- Each run of the program uses only one percentile which is provided in the percentile file. 
- Each line of input file is a record.
- Only the following field are considered important (although this can be modified easily): `CMTE_ID`, `NAME`, `ZIP_CODE`, `TRANSACTION_AMT`, `TRANSACTION_DT`, `OTHER_ID`.
- Only the records with empty `OTHER_ID` is considered.
- Percentile value in the percentile file is assumed to be an integer between 1 and 100.
- Code skips a record if:
	- `TRANSACTION_DT` is an invalid date (empty or malformed). The form should be an 8 digits sequence of numbers in the form `MMDDYYYY`. Integer equivalent of `MM` should be between 1 to 12 and `DD` should be between 1 and 31.  
	- `ZIP_CODE` is empty or less than five digits.
	- `NAME` is empty or longer than character limit long which is 200 characters.
	- `CMTE_ID` is not exactly 9 characters long (excluding any leading or trailing spaces). 
	- `TRANSACTION_AMT` should only have digits and at maximum one `.`. It should have a maximum precision of 14 and maximum scale of 2. 

## Output File Format
Output file format is:

```CMTE_ID|ZIP_CODE|YEAR|NTH_PERCENTILE|TOTAL_NUMBER_OF_CONTRIBUTION_FROM_REPEAT_DONORS|TOTAL_AMOUNT_OF_CONTRIBUTION_FROM_REPEAT_DONORS```

Both `TOTAL_NUMBER_OF_CONTRIBUTION_FROM_REPEAT_DONORS` and `TOTAL_NUMBER_OF_CONTRIBUTION_FROM_REPEAT_DONORS` gets rounded to nearest total dollar amount ($.50 gets rounded up to $1). Each line represent one record. For each repeat donor encountered in the input file, a corresponding output line will be written.

- `NTH_PERCENTILE`: donation amount in a given percentile
- `TOTAL_NUMBER_OF_CONTRIBUTION_FROM_REPEAT_DONORS`: total number of contributions received for a specific recipient, zip code, and calendar year. 
- `TOTAL_AMOUNT_OF_CONTRIBUTION_FROM_REPEAT_DONORS`: total amount of contributions received for a specific recipient, zip code, and calendar year.

## A Short Description of the Code
This code parse the input file line by line and write the output in the output file. This way it avoids the requirement to load all the input data, specially since the input file can be very large in size. Consequently, the behavior of the code is affected by this design. It means that if the order of information in the input file changes, the resulting output can be different. 
 
To find the repeat donor, I use a dictionary with a tuple `(NAME, ZIP_CODE)` as the key and the earliest year that a individual has donated, as we have seen till now, as the value. This way every time we want to check a new record, in order to check if it is a repeat donor, it will be O(1) operations. Every time an earlier year of donation from an individual is observed, his/her record will be updated with the earlier year.

I use a different dictionary for recipients in which I use a tuple `(CMTE_ID, ZIP_CODE, TRANSACTION_YEAR)` as the key and a list of the following form as the value:

`[[50, 110, 125, 300], 585]`

The first element of this list keeps an ordered list of donation from repeat donors to the recipient `CMTE_ID`. The second element store the sum of the donations. This way every time I add an element to the first list, I update this total contribution by adding the last element with current sum. This adds to space complexity but considerably can reduce the time complexity for large inputs. To keep the first list in an ascending order, I add any new element using the `bisect` module which uses a bisection method to find the location of the new element. For large lists, this will save time since it avoids sorting the list every time we need to find percentile. 


## Code Requirements and Testing
I have tested the code with python 3.5.4 and it needs the following modules: `sys`, `math`, `bisect`, and `time`.

I have also written some unittests for most of the functions in the `./src/analyse_repeat_donations.py`. You can find the tests in `./src/test_analyze_repeat_donations.py`. To run those tests you can simply execute:

```python ./src/test_analyse_repeat_donations.py```

The tests are written using the `unittest` module.

There are also a few integration tests in the folder `./insight_testsuite/tests/`. You can run those tests by running the `python ./insight_testsuite/run_tests.sh`.






