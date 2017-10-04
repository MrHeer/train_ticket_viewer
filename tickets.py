"""
---------------------------------------
命令行火车票查看器

Usage:
    tickets [-dgcktz] <from> <to> <date>

Options:
    -h, --help      帮助
    -d              动车
    -g              高铁
    -c              城际
    -k              快速
    -t              特快
    -z              直达
    -v, --version   版本

Examples:
    tickets 上海 北京 2017-10-01
    tickets -dg 成都 南京 2017-10-05
"""

import requests
from docopt import docopt
from datetime import datetime
from prettytable import PrettyTable
from colorama import init, Fore
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import stations

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

init()


class TrainCollection:
    headers = '车次 车站 时间 历时 一等座 二等座 软卧 硬卧 软座 硬座 无座'.split()

    def __init__(self, raw_trains, options):
        self.raw_trains = raw_trains
        self.options = options

    @staticmethod
    def colored(color, string):
        return ''.join([getattr(Fore, color.upper()), string, Fore.RESET])

    def get_from_to_station_name(self, data_list):
        from_station_telecode = data_list[6]
        to_station_telecode = data_list[7]
        return '\n'.join([
            self.colored('green', stations.get_name(from_station_telecode)),
            self.colored('red', stations.get_name(to_station_telecode))
        ])

    def get_start_arrive_time(self, data_list):
        return '\n'.join([
            self.colored('green', data_list[8]),
            self.colored('red', data_list[9])
        ])

    def get_time_duration(self, data_list):
        hours = int(data_list[10].split(':')[0])
        minutes = int(data_list[10].split(':')[1])
        days = int(hours / 24)
        hours = hours - (24 * days)
        if days > 0:
            return ''.join([
                str(days),
                '天',
                str(hours),
                '时',
                str(minutes),
                '分'
            ])
        elif hours > 0:
            return ''.join([
                str(hours),
                '时',
                str(minutes),
                '钟'
            ])
        else:
            return ''.join([
                str(minutes),
                '钟'
            ])

    def parse_train_data(self, data_list):
        return (
            data_list[3],  # 车次
            self.get_from_to_station_name(data_list),
            self.get_start_arrive_time(data_list),
            self.get_time_duration(data_list),  # 历时
            # data_list[10],                              # 历史
            data_list[31] or '--',  # 一等座
            data_list[30] or '--',  # 二等座
            data_list[23] or '--',  # 软卧
            data_list[28] or '--',  # 硬卧
            data_list[24] or '--',  # 软座
            data_list[29] or '--',  # 硬座
            data_list[33] or '--'  # 无座
        )

    def need_print(self, data_list):
        station_train_code = data_list[3]
        initial = station_train_code[0].lower()
        return not self.options or initial in self.options

    @property
    def trains(self):
        for train in self.raw_trains:
            data_list = train.split('|')
            if self.need_print(data_list):
                yield self.parse_train_data(data_list)

    def pretty_print(self):
        pt = PrettyTable()
        pt._set_field_names(self.headers)
        for train in self.trains:
            pt.add_row(train)
        print(pt)


class Cli(object):
    url_template = (
        'https://kyfw.12306.cn/otn/leftTicket/queryX?'
        'leftTicketDTO.train_date={}&'
        'leftTicketDTO.from_station={}&'
        'leftTicketDTO.to_station={}&'
        'purpose_codes=ADULT'
    )

    def __init__(self):
        self.arguments = docopt(__doc__, version='Tickets 1.0')
        self.from_station = stations.get_telecode(self.arguments['<from>'])
        self.to_station = stations.get_telecode(self.arguments['<to>'])
        self.date = self.arguments['<date>']
        self.check_arguments_validity()
        self.options = ''.join([key for key, value in self.arguments.items() if value is True])

    @property
    def request_url(self):
        return self.url_template.format(self.date, self.from_station, self.to_station)

    def check_arguments_validity(self):
        if self.from_station is None or self.to_station is None:
            print(u'请输入有效的车站名称')
            exit()
        try:
            if datetime.strptime(self.date, '%Y-%m-%d') < datetime.now():
                raise ValueError
        except:
            print(u'请输入有效日期')
            exit()

    def run(self):
        r = requests.get(self.request_url, verify=False)
        trains = r.json()['data']['result']
        TrainCollection(trains, self.options).pretty_print()


if __name__ == '__main__':
    Cli().run()
