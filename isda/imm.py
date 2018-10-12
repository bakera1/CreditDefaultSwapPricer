
import calendar
import unittest
import datetime

"""

OK
bakera@:~/workspace$ python imm.py 
17/03/2017 [('6M', '20/06/2017'), ('1Y', '20/12/2017'), ('2Y', '20/12/2018'), ('3Y', '20/12/2019'), ('5Y', '20/12/2021'), ('7Y', '20/12/2023')]
20/03/2017 [('6M', '20/12/2017'), ('1Y', '20/06/2018'), ('2Y', '20/06/2019'), ('3Y', '20/06/2020'), ('5Y', '20/06/2022'), ('7Y', '20/06/2024')]
...
18/09/2017 [('6M', '20/12/2017'), ('1Y', '20/06/2018'), ('2Y', '20/06/2019'), ('3Y', '20/06/2020'), ('5Y', '20/06/2022'), ('7Y', '20/06/2024')]
19/09/2017 [('6M', '20/12/2017'), ('1Y', '20/06/2018'), ('2Y', '20/06/2019'), ('3Y', '20/06/2020'), ('5Y', '20/06/2022'), ('7Y', '20/06/2024')]
20/09/2017 [('6M', '20/06/2018'), ('1Y', '20/12/2018'), ('2Y', '20/12/2019'), ('3Y', '20/12/2020'), ('5Y', '20/12/2022'), ('7Y', '20/12/2024')]
21/09/2017 [('6M', '20/06/2018'), ('1Y', '20/12/2018'), ('2Y', '20/12/2019'), ('3Y', '20/12/2020'), ('5Y', '20/12/2022'), ('7Y', '20/12/2024')]
...
15/03/2018 [('6M', '20/06/2018'), ('1Y', '20/12/2018'), ('2Y', '20/12/2019'), ('3Y', '20/12/2020'), ('5Y', '20/12/2022'), ('7Y', '20/12/2024')]
16/03/2018 [('6M', '20/06/2018'), ('1Y', '20/12/2018'), ('2Y', '20/12/2019'), ('3Y', '20/12/2020'), ('5Y', '20/12/2022'), ('7Y', '20/12/2024')]
19/03/2018 [('6M', '20/06/2018'), ('1Y', '20/12/2018'), ('2Y', '20/12/2019'), ('3Y', '20/12/2020'), ('5Y', '20/12/2022'), ('7Y', '20/12/2024')]
20/03/2018 [('6M', '20/12/2018'), ('1Y', '20/06/2019'), ('2Y', '20/06/2020'), ('3Y', '20/06/2021'), ('5Y', '20/06/2023'), ('7Y', '20/06/2025')]
21/03/2018 [('6M', '20/12/2018'), ('1Y', '20/06/2019'), ('2Y', '20/06/2020'), ('3Y', '20/06/2021'), ('5Y', '20/06/2023'), ('7Y', '20/06/2025')]
22/03/2018 [('6M', '20/12/2018'), ('1Y', '20/06/2019'), ('2Y', '20/06/2020'), ('3Y', '20/06/2021'), ('5Y', '20/06/2023'), ('7Y', '20/06/2025')]
...
18/09/2018 [('6M', '20/12/2018'), ('1Y', '20/06/2019'), ('2Y', '20/06/2020'), ('3Y', '20/06/2021'), ('5Y', '20/06/2023'), ('7Y', '20/06/2025')]
19/09/2018 [('6M', '20/12/2018'), ('1Y', '20/06/2019'), ('2Y', '20/06/2020'), ('3Y', '20/06/2021'), ('5Y', '20/06/2023'), ('7Y', '20/06/2025')]
20/09/2018 [('6M', '20/06/2019'), ('1Y', '20/12/2019'), ('2Y', '20/12/2020'), ('3Y', '20/12/2021'), ('5Y', '20/12/2023'), ('7Y', '20/12/2025')]
21/09/2018 [('6M', '20/06/2019'), ('1Y', '20/12/2019'), ('2Y', '20/12/2020'), ('3Y', '20/12/2021'), ('5Y', '20/12/2023'), ('7Y', '20/12/2025')]
24/09/2018 [('6M', '20/06/2019'), ('1Y', '20/12/2019'), ('2Y', '20/12/2020'), ('3Y', '20/12/2021'), ('5Y', '20/12/2023'), ('7Y', '20/12/2025')]
04/03/2019 [('6M', '20/06/2019'), ('1Y', '20/12/2019'), ('2Y', '20/12/2020'), ('3Y', '20/12/2021'), ('5Y', '20/12/2023'), ('7Y', '20/12/2025')]
05/03/2019 [('6M', '20/06/2019'), ('1Y', '20/12/2019'), ('2Y', '20/12/2020'), ('3Y', '20/12/2021'), ('5Y', '20/12/2023'), ('7Y', '20/12/2025')]
06/03/2019 [('6M', '20/06/2019'), ('1Y', '20/12/2019'), ('2Y', '20/12/2020'), ('3Y', '20/12/2021'), ('5Y', '20/12/2023'), ('7Y', '20/12/2025')]
"""

def add_month(date):
    month_days = calendar.monthrange(date.year, date.month)[1]
    candidate = date + datetime.timedelta(days=month_days)
    return candidate.replace(day=1) - datetime.timedelta(days=1) \
        if candidate.day != date.day \
        else candidate

def remove_month(date):
    candidate = date.replace(day=1) - datetime.timedelta(days=1)
    return candidate.replace(day=date.day)

def move_n_months(date, i, n, direction='add'):
    if i == n:
        return date
    else:
        i += 1
        return move_n_months(add_month(date) if direction == 'add' else remove_month(date), i, n, direction)

def next_imm(s_date,
             semi_annual_roll_start=datetime.datetime(2015, 12, 20),
             imm_month_list=[3, 6, 9, 12], imm_semi_annual_roll_months=[3, 9]):

    imm_date_count = 0
    imm_day_of_month = 20
    months_between_imm_dates = 3
    one_day = datetime.timedelta(1)

    # break after reaching first immdate
    while True:
        if imm_date_count >= 1:
            break
        s_date = s_date + one_day
        if s_date.day == imm_day_of_month \
                and s_date.month in imm_month_list:
            imm_date_count += 1

    # semi annual roll date adjustment, implemented after 2015
    if s_date >= semi_annual_roll_start:
        # move back 3 months to previous imm date
        if s_date.month in imm_semi_annual_roll_months:
            s_date = move_n_months(s_date, 0,
                                   months_between_imm_dates,
                                   direction='remove')

    # adjust day for day of week? Modified Following
    return datetime.datetime(s_date.year, s_date.month, imm_day_of_month)

def imm_date_vector(start_date,
                    tenor_list=[0.5, 1, 2, 3, 4, 5, 7, 10, 15, 20, 30],
                    format='%d/%m/%Y'):
    """
    potentially multiple rolldates in each tenor year;
    
    a) which potential roll date in each year is closest.
    b) means generating for each tenor all 4 roll dates, then adjust these for weekend
    c) then filter each based on the closest to the 
    
    d) build the following structure   
    (cob_date, tenor, target_date, (tuple of potential dates))
    
    :param start_date: 
    :param tenor_list: 
    :return: 
    """

    # need a better date add that knows which month?
    return [(x, next_imm(move_n_months(start_date, 0, (6 if x == 0.5 else x * 12)))) for x in tenor_list] if format == '' \
        else [('{0}{1}'.format((6 if x == 0.5 else x), ('Y' if x >= 1 else 'M')),
               next_imm(move_n_months(start_date, 0, (6 if x == 0.5 else x * 12))).strftime(format)) for x in tenor_list]

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.one_day = datetime.timedelta(1)
        self.__format__ = '%d/%m/%Y'
        self.__tenor_list__ = [0.5, 1, 2, 3, 4, 5, 7, 10, 15, 20, 30]
        #self.__tenor_list_short__ = [0.5, 1, 2, 3, 5, 7]
        self.saturday = 5
        self.sunday = 6

    def tearDown(self):
        pass

    def test_add_n_months(self):

        s_date = datetime.datetime(2017, 3, 20)

        real_result = ['20/03/2017', '20/09/2017','20/06/2017']

        local_result = [s_date.strftime(self.__format__),
                 move_n_months(s_date, 0, 6).strftime(self.__format__),
                 next_imm(s_date).strftime(self.__format__)]

        for (r,l) in zip(real_result, local_result):
            self.assertTrue(r[0] == l[0] and r[1] == l[1])


    def test_single_rolldate_day_before_rolldate(self):

        # accepted results
        real_result = [('6M', '20/06/2017'),
                   ('1Y', '20/12/2017'),
                   ('2Y', '20/12/2018'),
                   ('3Y', '20/12/2019'),
                   ('5Y', '20/12/2021'),
                   ('7Y', '20/12/2023')]

        sdate = datetime.datetime(2017, 3, 17)
        tenor_list = [0.5, 1, 2, 3, 5, 7]
        local_result = imm_date_vector(start_date=sdate,
                                 tenor_list=tenor_list,
                                 format='%d/%m/%Y')

        #print sdate, local_result

        for (r,l) in zip(real_result, local_result):
            self.assertTrue(r[0] == l[0] and r[1] == l[1])

    def test_single_rolldate_day_after_rolldate(self):

        # accepted results
        real_result = [('6M', '20/12/2017'),
                   ('1Y', '20/06/2018'),
                   ('2Y', '20/06/2019'),
                   ('3Y', '20/06/2020'),
                   ('5Y', '20/06/2022'),
                   ('7Y', '20/06/2024')]

        sdate = datetime.datetime(2017, 3, 20)
        tenor_list = [0.5, 1, 2, 3, 5, 7]
        local_result = imm_date_vector(start_date=sdate,
                                 tenor_list=tenor_list,
                                 format='%d/%m/%Y')

        #print sdate, local_result

        for (r,l) in zip(real_result, local_result):
            self.assertTrue(r[0] == l[0] and r[1] == l[1])

    def o_test_rolldate(self):
        """
            use this test to generate large slabs of data
        :return: 
        """
        start_date = datetime.datetime(2017, 3, 17)
        max_days = 100
        day_count = 0

        while True:

            # limit number of days
            if day_count >= max_days:
                break

            # omit weekends
            if start_date.weekday() in [self.saturday, self.sunday]:
                start_date = start_date + self.one_day
                day_count += 1
                continue

            # compute the imm date vector result
            result = imm_date_vector(start_date,
                            tenor_list=self.__tenor_list__,
                            format=self.__format__)

            day_count += 1
            print(start_date.strftime(self.__format__), result)

            # roll one more cob date forward
            start_date = start_date + self.one_day

            # check the results from calculation
            self.assertTrue(True)

if __name__ == '__main__':
	unittest.main()
