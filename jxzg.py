import requests
import json
import re

from GDGM_SSO import main as GDGMUtils

def url_param_to_dict(param):
    param = param.split('?')[1]
    param_dict = {}
    for i in param.split('&'):
        param_dict[i.split('=')[0]] = i.split('=')[1]
    return param_dict


def get_host_url(url):
    return re.search(r'(https?://.*?)/', url).group(1)


class jxzg:
    server_url = 'https://jxzg.gdgm.cn:9103'
    cas_login_url = server_url + '/centralized/login/casLogin'
    ticket_url = server_url + '/centralized/login/casLogin?ticket={}'
    user_info_url = server_url + '/centralized/login/singleLogin'

    # NBBZTX 内部质量保证检测系统
    get_level_url = '/assurance/support/queryDictionaryList'
    get_plan_url = '/assurance/TmTaskPersonal/plan'
    task_add_url = '/assurance/TmTaskPersonal/add'
    find_task_url = '/assurance/TmTaskPersonal/query'

    session = requests.Session()

    user_info = {}

    def __init__(self, sso_obj):
        self.sso = sso_obj
        self.user_info = self.get_base_info(self.get_ticket())

    def get_ticket(self):
        ticket = self.sso.get_service_ticket(self.cas_login_url, True)
        return ticket

    def get_base_info(self, ticket):
        response = self.session.get(self.ticket_url.format(ticket), allow_redirects=False)
        response = self.session.get(response.headers['Location'], allow_redirects=False) # https://jxzg.gdgm.cn:9103/#/login?loginType=casLogin&relationNo=*******
        response = self.session.post(self.user_info_url, data={'relationNo': url_param_to_dict(response.headers['Location'])['relationNo']}).json()['data']
        return response

    def get_system_url(self, system_name):
        for i in self.user_info['systemList']:
            if i['systemName'] == system_name or i['systemNo'] == system_name:
                return get_host_url(i['systemUrl'])

    def get_level(self):
        response = self.session.post(self.get_system_url('NBBZTX') + self.get_level_url, data={'dictKey': 'RWYXJ', 'token': self.user_info['token']})
        print(response.text)
        response = response.json()
        response = response['data']['list']
        result = {}
        for i in response:
            result[i['fieldValue']] = i['fieldKey']
        return result

    def get_plan(self, personalNo=None):
        if personalNo is None:
            personalNo = self.user_info['relationNo']
        response = self.session.post(self.get_system_url('NBBZTX') + self.get_plan_url, data={'personalNo': personalNo, 'token': self.user_info['token']}).json()
        result = []
        for i in response['data']:
            result.append({
                'no': i['planNo'],
                'name': i['planName'],
            })
        return result

    def add_task(self, name, level, planNo, startDate, endDate, warnDate, desc, createrNo=None, createrName=None, createType='STUDENT'):
        if createrNo is None:
            createrNo = self.user_info['relationNo']
        if createrName is None:
            createrName = self.user_info['userName']
        response = self.session.post(self.get_system_url('NBBZTX') + self.task_add_url, data={
            'taskName': name,
            'taskLevel': level,
            'planNo': planNo,
            'startDate': startDate,
            'endDate': endDate,
            'warnDate': warnDate,
            'taskDesc': desc,
            'createrNo': createrNo,
            'createrName': createrName,
            'createType': createType,
            'token': self.user_info['token']
        }).json()
        return response

    def find_task(self, createrNo=None, departmentNo=None, taskStatus=None, taskName=None, createType=None, pageNum=1, pageSize=100):
        if createrNo is None:
            createrNo = self.user_info['relationNo']
        response = self.session.post(self.get_system_url('NBBZTX') + self.find_task_url, data={
            'createType': createType,
            'departmentNo': departmentNo,
            'taskStatus': taskStatus,
            'taskName': taskName,
            'createrNo': createrNo,
            'pageNum': pageNum,
            'pageSize': pageSize,
            'token': self.user_info['token']
        }).json()
        return response['data']['rows']

def make_task_info(year, name, level, planNoDict):
    with open('jxzg_data.txt', 'r', encoding='utf-8') as f:
        data = f.read()
    data = data.split('\n')
    data = [i for i in data if i]
    data = [i.split('----') for i in data]
    result = []
    for i in data:
        result.append({
            'name': f'{year}年{name}-{i[0]}-{i[1]}',
            'desc': i[2],
            'level': level,
            'planNo': planNoDict[str(year)],
            'startDate': f'{year}-09-01',
            'endDate': f'{year + 1}-09-1',
            'warnDate': f'{year + 1}-07-27'
        })
    return result

def plan_to_dict(plan):
    result = {}
    for i in plan:
        year = re.search(r'\d{4}', i['name']).group()
        result[year] = i['no']
    return result

def main(level='中', start_year=2023, end_year=2025):
    config = GDGMUtils.load_config()
    gdgm_info = config['gdgm']

    print('sso开始登录')
    sso_obj = GDGMUtils.sso(gdgm_info['user'], gdgm_info['password'])
    print('sso登录成功')

    jxzg_obj = jxzg(sso_obj)
    print(json.dumps(jxzg_obj.user_info, indent=4, ensure_ascii=False))
    level = jxzg_obj.get_level()[level]

    plan = plan_to_dict(jxzg_obj.get_plan())
    print(json.dumps(plan, indent=4, ensure_ascii=False))

    find = jxzg_obj.find_task(createType='STUDENT')
    print(json.dumps(find, indent=4, ensure_ascii=False))

    for i in range(start_year, end_year + 1):
        task_info = make_task_info(i, jxzg_obj.user_info['userName'], level, plan)
        for j in task_info:
            if not any(j['name'] == k['taskName'] for k in find):
                print(f'添加 {j["name"]}')
                print(jxzg_obj.add_task(j['name'], j['level'], j['planNo'], j['startDate'], j['endDate'], j['warnDate'], j['desc'], jxzg_obj.user_info['relationNo'], jxzg_obj.user_info['userName']))
            else:
                print(f'{j["name"]} 已存在')

if __name__ == '__main__':
    main()
