import re
import requests
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9027'
response = requests.get(url, verify=False)
pattern = u'([\u4e00-\u9fa5]+)\|([A-Z]+)'
stations = dict(re.findall(pattern, response.text))
pprint(stations.keys(), indent=4)
pprint(stations.values(), indent=4)
