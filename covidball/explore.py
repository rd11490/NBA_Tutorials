import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Set display options for pandas for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)


reddit = pd.read_csv('./data/reddit_data.csv')


def convert_date(date_in):
    if date_in is None or pd.isna(date_in):
        return None

    date = datetime.datetime.strptime(date_in.strip(), '%m %d %Y')
    return date

reddit['DateIn'] = reddit['Date'].apply(convert_date)
reddit['DateOut'] = reddit['Date Out'].apply(convert_date)


reddit_dates = reddit[['DateIn', 'DateOut']]

hashtag = pd.read_csv('./data/hashtag_data_2021.csv')

def convert_hashtag_date(date_in):
    if date_in is None or pd.isna(date_in):
        return None

    date = datetime.datetime.strptime(date_in.strip(), '%d %B %Y')
    return date

hashtag['DateIn'] = hashtag['INJURED ON'].apply(convert_hashtag_date)
hashtag['DateOut'] = hashtag['RETURNED'].apply(convert_hashtag_date)

hashtag_dates = hashtag[['DateIn', 'DateOut']]

all_dates = pd.concat([hashtag_dates, reddit_dates]).to_dict('records')

day_count = 79
start_date = datetime.datetime.strptime('1 October 2021', '%d %B %Y')

dates = []
protocol = []

for single_date in (start_date + datetime.timedelta(n) for n in range(day_count)):
    in_protocol = 0
    for p in all_dates:
        if single_date >= p['DateIn']:
            if pd.isnull(p['DateOut']) or single_date <= p['DateOut']:
                in_protocol += 1
    # print(single_date)
    # print(in_protocol)
    dates.append(single_date)
    protocol.append(in_protocol)

plt.figure(figsize=(12,8))
plt.plot(dates, protocol, color='red')
plt.xlabel('Date')
plt.ylabel('Players in Protocol')
plt.title('NBA Players in Health and Safety Protocol By Date')
plt.show()