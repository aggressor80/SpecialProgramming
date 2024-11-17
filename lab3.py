from spyre import server
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from urllib import request
from os import listdir, makedirs, walk, path
from shutil import rmtree
from datetime import datetime
from re import search


def check_folder():
    if listdir('data'):
        rmtree('data')
        makedirs('data')


def get_data(province_id):
    url = f'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={province_id}&year1=1981&year2=2024&type=Mean'

    vhi = request.urlopen(url).read().decode('utf-8')
    now = datetime.now()
    formatted_time = now.strftime('%d%m%Y%H%M%S')
    with open(f'data/vhi_id_{province_id}_{formatted_time}.csv', 'w') as f:
        f.write(vhi)


def make_df(file_path, norm_province_id):
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    temp_df = pd.read_csv(file_path, header=1, names=headers)
    temp_df = temp_df.drop(temp_df.loc[temp_df['VHI'] == -1].index)
    temp_df.loc[0, 'Year'] = temp_df.loc[0, 'Year'][9:]
    temp_df = temp_df.drop(columns='empty').drop(temp_df.index[-1])
    temp_df['area'] = norm_province_id
    temp_df['Year'] = temp_df['Year'].astype(int)
    temp_df['Week'] = temp_df['Week'].astype(int)
    temp_df = temp_df.drop(['SMN', 'SMT'], axis=1)

    return temp_df


def find_paths(dir_path):
    file_paths = []
    for root, dirs, files in walk(dir_path):
        for i in files:
            file_paths.append(path.join(root, i))

    return file_paths


def find_province_id(file_path):
    with open(file_path, 'r') as f:
        return int(search(r'Province\s*=\s*(\d+)', f.readline()).group(1))


replacements_dict = {1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20,
                     10: 21, 11: 9, 12: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14,
                     18: 15, 19: 16, 20: 25, 21: 17, 22: 18, 23: 6, 24: 1, 25: 2, 26: 7, 27: 5}


class DataApp(server.App):
    title = 'NOAA Data Visualisation'

    inputs = [{'type': 'dropdown',
               'label': 'indicator',
               'options': [{'label': 'VCI', 'value': 'VCI'},
                           {'label': 'TCI', 'value': 'TCI'},
                           {'label': 'VHI', 'value': 'VHI'}],
               'key': 'indicator',
               'action_id': 'simple_html_output'},

              {'type': 'dropdown',
               'label': 'Area',
               'options': [{'label': 'Vinnytsia r.', 'value': '1'},
                           {'label': 'Volyn r.', 'value': '2'},
                           {'label': 'Dnipro r.', 'value': '3'},
                           {'label': 'Donetsk r.', 'value': '4'},
                           {'label': 'Zhytomyr r.', 'value': '5'},
                           {'label': 'Zakarpattia r.', 'value': '6'},
                           {'label': 'Zaporizhzhia r.', 'value': '7'},
                           {'label': 'Ivano-Frankivsk r.', 'value': '8'},
                           {'label': 'Kyiv r.', 'value': '9'},
                           {'label': 'Kirovohrad r.', 'value': '10'},
                           {'label': 'Luhansk r.', 'value': '11'},
                           {'label': 'Lviv r.', 'value': '12'},
                           {'label': 'Mykolaiv r.', 'value': '13'},
                           {'label': 'Odesa r.', 'value': '14'},
                           {'label': 'Poltava r.', 'value': '15'},
                           {'label': 'Rivne r.', 'value': '16'},
                           {'label': 'Sumy r.', 'value': '17'},
                           {'label': 'Ternopil r.', 'value': '18'},
                           {'label': 'Kharkiv r.', 'value': '19'},
                           {'label': 'Kherson r.', 'value': '20'},
                           {'label': 'Khmelnytshyi r.', 'value': '21'},
                           {'label': 'Cherkasy r.', 'value': '22'},
                           {'label': 'Chernivtsi r.', 'value': '23'},
                           {'label': 'Chernihiv r.', 'value': '24'},
                           {'label': 'AR Crimea', 'value': '25'},
                           {'label': 'Kyiv c.', 'value': '26'},
                           {'label': 'Sevastopol c.', 'value': '27'}],
               'key': 'area_index',
               'action_id': 'simple_html_output'},

              {
                  'type': 'text',
                  'key': 'range_years',
                  'label': 'Years',
                  'value': '1982-2024',
                  'action_id': 'simple_html_output'
              },
              {
                  'type': 'text',
                  'key': 'range_weeks',
                  'label': 'Weeks',
                  'value': '1-52',
                  'action_id': 'simple_html_output'
              }
              ]

    outputs = [
        {
            'type': 'plot',
            'id': 'get_plot',
            'control_id': 'update_data',
            'tab': 'Plot',
            'on_page_load': True},
        {
            'type': 'table',
            'id': 'get_data',
            'control_id': 'update_data',
            'tab': 'Table',
            'on_page_load': True
        }
    ]

    tabs = ['Table', 'Plot']

    controls = [
        {
            'type': 'button',
            'id': 'update_data',
            'label': 'Show data'
        }]

    def __init__(self):
        check_folder()
        for i in range(1, 28):
            get_data(i)
        self.df = pd.concat([make_df(i, replacements_dict[find_province_id(i)]) for i in find_paths('data')])

    def get_data(self, params):
        start_year, end_year = self.parse_range(params['range_years'])
        start_week, end_week = self.parse_range(params['range_weeks'])

        filtered_df = self.df[
            (self.df['area'] == int(params['area_index'])) &
            (self.df['Year'].between(start_year, end_year)) &
            (self.df['Week'].between(start_week, end_week))
            ]

        return filtered_df[['Year', 'Week', params['indicator']]]

    def get_plot(self, params):
        start_year, end_year = self.parse_range(params['range_years'])

        filtered_df = self.df[
            (self.df['area'] == int(params['area_index'])) &
            (self.df['Year'].between(start_year, end_year))
            ]

        ax = sns.lineplot(x='Year', y=params['indicator'], data=filtered_df, ci=None)
        return ax.get_figure()

    def parse_range(self, r):
        start, end = map(int, r.split('-'))
        return start, end


app = DataApp()
app.launch()
