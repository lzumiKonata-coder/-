import requests
import re
import execjs
import time
import json
from config import *
from bs4 import BeautifulSoup
from hashlib import md5

def get_enc(clazzid,userid,jobid,objectid,playingtime,duration,clipTime):
    # 定义模板字符串
    template = '[{0}][{1}][{2}][{3}][{4}][{5}][{6}][{7}]'

    # 按占位符顺序传入参数
    result = template.format(
        clazzid,          # {0}
        userid,                 # {1}
        jobid or '',            # {2}
        objectid,               # {3}
        playingtime*1000,       # {4}
        'd_yHJ!$pdA~5',         # {5}
        duration * 1000,        # {6}  duration*1000
        clipTime                # {7}
    )

    enc = md5(result.encode('utf-8')).hexdigest()
    return enc

def get_cookies(uname,pwd):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://i.chaoxing.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    params = {
        'fid': '',
        'newversion': 'true',
        'refer': 'https://i.chaoxing.com',
    }

    response = requests.get('https://passport2.chaoxing.com/login', params=params, headers=headers)
    all_headers = response.headers
    cookies = all_headers.get('Set-Cookie')
    JSESSIONID = re.search(r'JSESSIONID=(.*?);', cookies).group(1)
    route = re.search(r'route=(.*?);', cookies).group(1)
    cookies = {}
    cookies['JSESSIONID'] = JSESSIONID
    cookies['route'] = route


    with open('encrypt.js', 'r') as f:
        ctx = execjs.compile(f.read())

    data = ctx.call('get_uname_password', uname, pwd)

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://passport2.chaoxing.com',
        'Pragma': 'no-cache',
        'Referer': 'https://passport2.chaoxing.com/login?fid=12&refer=http%3A%2F%2Fi.chaoxing.com%2Fbase%3Ft%3D1768033122232&space=2',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'fid': '-1',
        'uname': '{}'.format(data['uname']),
        'password': '{}'.format(data['password']),
        'refer': 'http%3A%2F%2Fi.chaoxing.com%2Fbase%3Ft%3D'+str(int(1000*time.time())),
        't': 'true',
        'forbidotherlogin': '0',
        'validate': '',
        'doubleFactorLogin': '0',
        'independentId': '0',
        'independentNameId': '0',
    }

    response = requests.post('https://passport2.chaoxing.com/fanyalogin', cookies=cookies, headers=headers, data=data)
    all_headers = response.headers
    set_cookies = all_headers.get('Set-Cookie')
    fid = re.search(r'fid=(.*?);', set_cookies).group(1)
    _uid = re.search(r'_uid=(.*?);', set_cookies).group(1)
    _d = re.search(r'_d=(.*?);', set_cookies).group(1)
    UID = re.search(r'UID=(.*?);', set_cookies).group(1)
    vc3 = re.search(r'vc3=(.*?);', set_cookies).group(1)
    uf = re.search(r'uf=(.*?);', set_cookies).group(1)
    cx_p_token = re.search(r'cx_p_token=(.*?);', set_cookies).group(1)
    p_auth_token = re.search(r'p_auth_token=(.*?);', set_cookies).group(1)
    xxtenc = re.search(r'xxtenc=(.*?);', set_cookies).group(1)
    DSSTASH_LOG = re.search(r'DSSTASH_LOG=(.*?);', set_cookies).group(1)
    cookies = {}
    cookies['fid'] = fid
    cookies['_uid'] = _uid
    cookies['_d'] = _d
    cookies['UID'] = UID
    cookies['vc3'] = vc3
    cookies['uf'] = uf
    cookies['cx_p_token'] = cx_p_token
    cookies['p_auth_token'] = p_auth_token
    cookies['xxtenc'] = xxtenc
    cookies['DSSTASH_LOG'] = DSSTASH_LOG
    return cookies

def get_course_list(cookies):
    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://mooc1-1.chaoxing.com',
        'Pragma': 'no-cache',
        'Referer': 'https://mooc1-1.chaoxing.com/visit/interaction?s=1a02f4c43f48fb2856b975e81df0c67a',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'courseType': '1',
        'courseFolderId': '0',
        'baseEducation': '0',
        'superstarClass': '',
        'courseFolderSize': '0',
    }

    response = requests.post('https://mooc1-1.chaoxing.com/mooc-ans/visit/courselistdata', cookies=cookies, headers=headers, data=data)
    html_content = response.text

    # 1. 解析HTML
    soup = BeautifulSoup(html_content, 'lxml')

    # 2. 提取所有课程li标签（class为"course clearfix"）
    course_items = soup.find_all('li', class_='course clearfix')

    # 3. 遍历每个课程，提取目标信息
    course_data = []
    for item in course_items:
        try:
            # 提取li标签上的自定义属性：courseId、clazzId、personId
            course_id = item.attrs.get('courseid', '')  # 若属性不存在，返回空字符串
            clazz_id = item.attrs.get('clazzid', '')
            person_id = item.attrs.get('personid', '')
            id = item.attrs.get('id', '')

            # 提取课程标题（span标签的title属性，class为"course-name overHidden2"）
            title_span = item.find('span', class_='course-name overHidden2')
            course_title = title_span.attrs.get('title', '') if title_span else ''

            # 整理成字典，方便后续使用
            course_info = {
                'clazzid': clazz_id,
                'courseid': course_id,
                'id': id,
                'personid': person_id,
                'title': course_title,
            }
            course_data.append(course_info)

        except Exception as e:
            # 防止单个课程解析失败导致整体中断
            print(f"解析某门课程时出错：{e}")
            continue
    return course_data

#knowledgeid ,cookies
def find_chapterid(courseid,clazzid,personid):

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        # 'Cookie': 'fid=604; _uid=340877631; _d=1768050124375; UID=340877631; vc3=dmXBEuXhoKNrcul%2FjHK440b61oTfE2Ph4DCmg3%2BAxPmj0SokV90%2BCGTg5P1QPCoE7sCbho12Wft1jAapUUI5A2hnzbAcbHgFRI9Lf1SYMFO8v5aVdvy%2F7zxI%2BE6EuSynb27kgQdfSrTa7mLeS268vk1aUYAQdLNvOBAMeCElf6o%3D02ada3b7517d3850d0b3b30521a8d74d; uf=fbe48ba271b0dbbda0f23d4d7560668d20c0c7f6174700c7924fba3709ea73d0599df2b2b27c1159c854e77cd3b513525d984d23a7662dfb9b0594e13f4b452fa995cca83579031aa94b593de5d847e4d649b59fbc966abce5851b744f8aa02c9fb3947ed09a594c2acbfa05dc5aa122da2c896ba76a37dca9f93ef6dfabec8dcdf9752c7b23a3419f747da084bc699570b5a05e402d2a6370184964ffe8c27c5732f38550869b59d62f3251e9fde267b1f899d50c1c3fa3aa2ebad65cd196bb; cx_p_token=f08c3e03d567b2cb11535c9998c98b30; p_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIzNDA4Nzc2MzEiLCJsb2dpblRpbWUiOjE3NjgwNTAxMjQzNzcsImV4cCI6MTc2ODY1NDkyNH0.cAa4fg62lIF_KyxhJK1AdPmzN_-zv9VwtusuTtkLIs4; xxtenc=ae21f750236073e55c3ad2ed66e1b299; DSSTASH_LOG=C_38-UN_2388-US_340877631-T_1768050124377',
    }

    params = {
        't': f'{int(time.time() * 1000)}',
    }

    response = requests.get('http://i.chaoxing.com/base', params=params, cookies=cookies, headers=headers)
    content = response.text
    s = re.search(r'\?s=(.*?)\'', content).group(1)
    # print(content)
    # print(s)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://i.chaoxing.com/',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        # 'Cookie': 'fid=604; _uid=340877631; _d=1768050124375; UID=340877631; vc3=dmXBEuXhoKNrcul%2FjHK440b61oTfE2Ph4DCmg3%2BAxPmj0SokV90%2BCGTg5P1QPCoE7sCbho12Wft1jAapUUI5A2hnzbAcbHgFRI9Lf1SYMFO8v5aVdvy%2F7zxI%2BE6EuSynb27kgQdfSrTa7mLeS268vk1aUYAQdLNvOBAMeCElf6o%3D02ada3b7517d3850d0b3b30521a8d74d; uf=fbe48ba271b0dbbda0f23d4d7560668d20c0c7f6174700c7924fba3709ea73d0599df2b2b27c1159c854e77cd3b513525d984d23a7662dfb9b0594e13f4b452fa995cca83579031aa94b593de5d847e4d649b59fbc966abce5851b744f8aa02c9fb3947ed09a594c2acbfa05dc5aa122da2c896ba76a37dca9f93ef6dfabec8dcdf9752c7b23a3419f747da084bc699570b5a05e402d2a6370184964ffe8c27c5732f38550869b59d62f3251e9fde267b1f899d50c1c3fa3aa2ebad65cd196bb; cx_p_token=f08c3e03d567b2cb11535c9998c98b30; p_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIzNDA4Nzc2MzEiLCJsb2dpblRpbWUiOjE3NjgwNTAxMjQzNzcsImV4cCI6MTc2ODY1NDkyNH0.cAa4fg62lIF_KyxhJK1AdPmzN_-zv9VwtusuTtkLIs4; xxtenc=ae21f750236073e55c3ad2ed66e1b299; DSSTASH_LOG=C_38-UN_2388-US_340877631-T_1768050124377; spaceFid=604; spaceRoleId=""',
    }

    params = {
        's': f'{s}',
    }

    response = requests.get('https://mooc1-1.chaoxing.com/visit/interaction', params=params, cookies=cookies,
                            headers=headers)
    all_headers = response.headers
    set_cookies = all_headers['Set-Cookie']
    k8s = re.search(r'k8s=(.*?);', set_cookies).group(1)
    jrose = re.search(r'jrose=(.*?);', set_cookies).group(1)
    route = re.search(r'route=(.*?);', set_cookies).group(1)
    cookies['k8s'] = k8s
    cookies['jrose'] = jrose
    cookies['route'] = route
    # print(cookies)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        # 'referer': 'https://mooc1-1.chaoxing.com/visit/interaction?s=1a02f4c43f48fb2856b975e81df0c67a',
    }

    params = {
        'courseid': f'{courseid}',
        'clazzid': f'{clazzid}',
        'vc': '1',
        'cpi': f'{personid}',
        'ismooc2': '1',
        'v': '2',
    }
    response = requests.get(
        'https://mooc1-1.chaoxing.com/mooc-ans/visit/stucoursemiddle',
        params=params,
        cookies=cookies,
        headers=headers,
    )

    content = response.text
    # print(content)
    enc = re.search(r'<input type="hidden" id="enc" name="enc" value="(.*?)"/>', content).group(1)
    # print(enc)
    all_headers = response.headers
    set_cookies = all_headers['Set-Cookie']
    jrose = re.search(r'jrose=(.*?);', set_cookies).group(1)
    # route = re.search(r'route=(.*?);', set_cookies).group(1)
    cookies['jrose'] = jrose
    # cookies['route'] = route
    # print(all_headers)

    headers = {
        'host': 'mooc2-ans.chaoxing.com',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'iframe',

        # 'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=0, i',
        # 'cookie': 'k8s=1768048371.498.5102.324410; route=bca6486eee9aca907e6257b7921729c3; fid=604; source=""; _uid=340877631; _d=1768102825152; UID=340877631; vc3=QCerNmM7VYPQFnLMJE1ykzLKibbQKv3ofX%2B9Bbn%2BAwXxXVx%2FMojtFql7BCgWDNplFyUMgDdphTQZuadz3lPTt9LX3hlE5ouCf3pJmRRE8ADvCJCnjCrm6J5ybj9O1A8MyBZE2Tp7WSlHACtXhv5LvPduOh5r9a6%2BMDkidk15b3A%3D503c7460e7813c24336144d9a7b86db0; uf=fbe48ba271b0dbbda0f23d4d7560668d20c0c7f6174700c7924fba3709ea73d09f424c3caac2622f78abafae41430b335d984d23a7662dfb9b0594e13f4b452fa995cca83579031aa94b593de5d847e4d649b59fbc966abce5851b744f8aa02c9fb3947ed09a594cb656531ee955ab093783faf299eb07b207aa1c10b563632f4dfd8fe371d6b8268e0cb4577cddd1f270b5a05e402d2a6370184964ffe8c27cf42ab3d23ff0667eae07e83b67ff7d52b1f899d50c1c3fa3aa2ebad65cd196bb; cx_p_token=15a111fe7605580357259da7cbe29d31; p_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIzNDA4Nzc2MzEiLCJsb2dpblRpbWUiOjE3NjgxMDI4MjUxNTQsImV4cCI6MTc2ODcwNzYyNX0.CtSr4gsYtO5Zn9WYXr7TGpPFGHyTFFvvG6oJst1B6xo; xxtenc=ae21f750236073e55c3ad2ed66e1b299; DSSTASH_LOG=C_38-UN_2388-US_340877631-T_1768102825154; spaceFid=604; spaceRoleId=""; jrose=A13D09983EDE82B5A485A21A9117582D.mooc2-1883325526-62t2r; jrosehead=1D474D58E26B9A2F5D83AE559EE8D392.mooc-portal-3058043660-r5w9c',
    }

    params = {
        'courseid': f'{courseid}',
        'clazzid': f'{clazzid}',
        'cpi': f'{personid}',
        'ut': 's',
        't': f'{int(time.time() * 1000)}',
        'stuenc': f'{enc}',
    }

    response = requests.get(
        'https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    content = response.text
    pattern_finish = r'已完成任务点: <span style="color:#00B368">(.*?)<'
    pattern_total = r'</span>/(\d+)'
    finish = re.search(pattern_finish, content).group(1)
    total = re.search(pattern_total, content).group(1)
    soup = BeautifulSoup(content, 'html.parser')
    # 提取所有chapter_item节点
    chapter_items = soup.find_all('div', class_='chapter_item')
    chapterids = []

    for item in chapter_items:
        # 排除已完成
        if not item.find('div', class_='icon_yiwanc'):
            # 检查是否有待完成任务点
            if item.find('input', class_='knowledgeJobCount') or item.find('div', class_='catalog_jindu'):
                # 提取chapterid
                item_id = item.get('id', '')
                if item_id.startswith('cur'):
                    chapterids.append(item_id.replace('cur', ''))
                else:
                    checkbox = item.find('input', {'name': 'checkbox'})
                    if checkbox and checkbox.get('value'):
                        chapterids.append(checkbox.get('value'))

    return finish,total,chapterids

def get_cards_v(cookies, courseid, clazzid, chapterid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }

    params = {
        'courseId': f'{courseid}',
        'clazzid': f'{clazzid}',
        'chapterId': f'{chapterid}',
        'cpi': '0',
        'verificationcode': '',
        'mooc2': '1',
        'microTopicId': '0',
        'editorPreview': '0',
    }

    response = requests.get(
        'https://mooc1.chaoxing.com/mooc-ans/mycourse/studentstudyAjax',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    content = response.text
    pattern = r'v=(.*?)&'
    try:
        v = re.search(pattern, content).group(1)
        return v
    except:
        print('get_v_error')

def get_v(v,cookies):
    headers = {
        # 'Accept': '*/*',
        # 'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cache-Control': 'no-cache',
        # 'Connection': 'keep-alive',
        # 'Pragma': 'no-cache',
        #'Referer': 'https://mooc1.chaoxing.com/mooc-ans/knowledge/cards?clazzid=126922707&courseid=254985633&knowledgeid=1031257808&num=0&ut=s&cpi=404635848&v=2025-0424-1038-3&mooc2=1&isMicroCourse=false&editorPreview=0',
        # 'Sec-Fetch-Dest': 'script',
        # 'Sec-Fetch-Mode': 'no-cors',
        # 'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        # 'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
        # 'Cookie': 'k8s-ed=1768038637.49.13085.718153; jrose=E917A32C4D861C3467DF267C4AFAD7DB.html-editor-a-379741770-gl3kd; k8s=1768038636.687.7553.421071; route=ce3aca120f3fcc9eb76807ea1ee5aae1; writenote=yes; fid=604; source=""; _uid=340877631; _d=1768102825152; UID=340877631; vc3=QCerNmM7VYPQFnLMJE1ykzLKibbQKv3ofX%2B9Bbn%2BAwXxXVx%2FMojtFql7BCgWDNplFyUMgDdphTQZuadz3lPTt9LX3hlE5ouCf3pJmRRE8ADvCJCnjCrm6J5ybj9O1A8MyBZE2Tp7WSlHACtXhv5LvPduOh5r9a6%2BMDkidk15b3A%3D503c7460e7813c24336144d9a7b86db0; uf=fbe48ba271b0dbbda0f23d4d7560668d20c0c7f6174700c7924fba3709ea73d09f424c3caac2622f78abafae41430b335d984d23a7662dfb9b0594e13f4b452fa995cca83579031aa94b593de5d847e4d649b59fbc966abce5851b744f8aa02c9fb3947ed09a594cb656531ee955ab093783faf299eb07b207aa1c10b563632f4dfd8fe371d6b8268e0cb4577cddd1f270b5a05e402d2a6370184964ffe8c27cf42ab3d23ff0667eae07e83b67ff7d52b1f899d50c1c3fa3aa2ebad65cd196bb; cx_p_token=15a111fe7605580357259da7cbe29d31; p_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIzNDA4Nzc2MzEiLCJsb2dpblRpbWUiOjE3NjgxMDI4MjUxNTQsImV4cCI6MTc2ODcwNzYyNX0.CtSr4gsYtO5Zn9WYXr7TGpPFGHyTFFvvG6oJst1B6xo; xxtenc=ae21f750236073e55c3ad2ed66e1b299; DSSTASH_LOG=C_38-UN_2388-US_340877631-T_1768102825154; spaceFid=604; spaceRoleId=""; videojs_id=1715483; jrose=71B1CFD5ED3644F469AAD5913D7B7186.mooc-3710904213-fbbwr',
    }

    params = {
        'v': f'{v}',
    }

    response = requests.get(
        'https://mooc1.chaoxing.com/ananas/ueditor/ueditor.parse.js',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    content = response.text
    v = re.search(r'modules/video/index-review.html\?v=(.*?)"', content).group(1)
    return v

def get_dtoken(cookies, v,objectid):
    headers = {
        'Referer': f'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v={v}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }

    params = {
        'k': f'{cookies['fid']}',
        'flag': 'normal',
        'ro': '0',
        '_dc': f'{int(time.time() * 1000)}',
    }

    response = requests.get(
        f'https://mooc1.chaoxing.com/ananas/status/{objectid}',
        params=params,
        cookies=cookies,
        headers=headers,
    )

    json_data = json.loads(response.text)
    try:
        dtoken = json_data['dtoken']
        return dtoken
    except:
        print('get_dtoken_error')

#提交视频进度
def main(clazzid, courseid, chapterid, personid, cookies,interval):
    global finish
    cards_v = get_cards_v(cookies, courseid, clazzid, chapterid)

    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cache-Control': 'no-cache',
        # 'Connection': 'keep-alive',
        # 'Pragma': 'no-cache',
        # 'Referer': 'https://mooc1.chaoxing.com/mycourse/studentstudy?chapterId=1031257807&courseId=254985633&clazzid=126922707&cpi=404635848&enc=13282807a10886521f68c6cee47a7818&mooc2=1&hidetype=0&openc=583e870843feb6b6a503720a0e0cc107',
        # 'Sec-Fetch-Dest': 'iframe',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-Site': 'same-origin',
        # 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        # 'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
        # 'Cookie': 'k8s=1768038636.687.7553.421071; route=ce3aca120f3fcc9eb76807ea1ee5aae1; writenote=yes; fid=604; source=""; _uid=340877631; _d=1768102825152; UID=340877631; vc3=QCerNmM7VYPQFnLMJE1ykzLKibbQKv3ofX%2B9Bbn%2BAwXxXVx%2FMojtFql7BCgWDNplFyUMgDdphTQZuadz3lPTt9LX3hlE5ouCf3pJmRRE8ADvCJCnjCrm6J5ybj9O1A8MyBZE2Tp7WSlHACtXhv5LvPduOh5r9a6%2BMDkidk15b3A%3D503c7460e7813c24336144d9a7b86db0; uf=fbe48ba271b0dbbda0f23d4d7560668d20c0c7f6174700c7924fba3709ea73d09f424c3caac2622f78abafae41430b335d984d23a7662dfb9b0594e13f4b452fa995cca83579031aa94b593de5d847e4d649b59fbc966abce5851b744f8aa02c9fb3947ed09a594cb656531ee955ab093783faf299eb07b207aa1c10b563632f4dfd8fe371d6b8268e0cb4577cddd1f270b5a05e402d2a6370184964ffe8c27cf42ab3d23ff0667eae07e83b67ff7d52b1f899d50c1c3fa3aa2ebad65cd196bb; cx_p_token=15a111fe7605580357259da7cbe29d31; p_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIzNDA4Nzc2MzEiLCJsb2dpblRpbWUiOjE3NjgxMDI4MjUxNTQsImV4cCI6MTc2ODcwNzYyNX0.CtSr4gsYtO5Zn9WYXr7TGpPFGHyTFFvvG6oJst1B6xo; xxtenc=ae21f750236073e55c3ad2ed66e1b299; DSSTASH_LOG=C_38-UN_2388-US_340877631-T_1768102825154; spaceFid=604; spaceRoleId=""; jrose=CCE9479D56C021114614FE5C1CED87AE.mooc-3710904213-fbbwr; videojs_id=6178284',
    }

    params = {
        'clazzid': f'{clazzid}',
        'courseid': f'{courseid}',
        'knowledgeid': f'{chapterid}',
        'num': '0',
        'ut': 's',
        'cpi': f'{personid}',
        'v': f'{cards_v}',
        'mooc2': '1',
        'isMicroCourse': 'false',
        'editorPreview': '0',
    }

    response = requests.get('https://mooc1.chaoxing.com/mooc-ans/knowledge/cards', params=params, cookies=cookies,
                            headers=headers)

    # 获取userid
    userid = re.search(r'"userid":"(.*?)",', response.text).group(1)
    # 获取v
    v = re.search(r'<link type="text/css" href="/ananas/ueditor/themes/iframe.css\?v=(.*?)" rel="stylesheet" />',
                  response.text).group(1)
    v = get_v(v, cookies)

    mArg = re.findall(r'mArg = (.*?);', response.text)
    datas = json.loads(mArg[1])
    datas = datas['attachments']
    # print(datas)
    for data in datas:
        if data['type'] =='video':
            # print(data)
            duration = data['attDuration']
            objectid = data['property']['objectid']
            otherInfo = data['otherInfo']
            otherInfo = re.search(r'(.*?)&', otherInfo).group(1)
            jobid = data['property']['jobid']
            attDurationEnc = data['attDurationEnc']
            videoFaceCaptureEnc = data['videoFaceCaptureEnc']
            clipTime = '0_' + '{}'.format(duration)
            dtoken = get_dtoken(cookies, v, objectid)
            n = duration//interval
            playingtime = 0
            for i in range(n+2):
                print(f'已提交时长: {playingtime}')
                print(f'剩余时长: {duration-playingtime}')
                enc = get_enc(clazzid, userid, jobid, objectid, playingtime, duration, clipTime)
                params = {
                    'clazzId': f'{clazzid}',
                    'playingTime': f'{playingtime}',
                    'duration': f'{duration}',
                    'clipTime': '0_' + str(duration),
                    'objectId': f'{objectid}',
                    'otherInfo': f'{otherInfo}',
                    'courseId': f'{courseid}',
                    'jobid': f'{jobid}',
                    'userid': f'{userid}',
                    'isdrag': '0',
                    'view': 'pc',
                    'enc': f'{enc}',
                    'rt': '0.9',
                    'videoFaceCaptureEnc': f'{videoFaceCaptureEnc}',
                    'dtype': 'Video',
                    '_t': f'{int(time.time() * 1000)}',
                    'attDuration': f'{duration}',
                    'attDurationEnc': f'{attDurationEnc}',
                }
                # print(params)
                response = requests.get(
                    f'https://mooc1.chaoxing.com/mooc-ans/multimedia/log/a/{personid}/{dtoken}',
                    params=params,
                    cookies=cookies,
                    headers=headers,
                )
                print(response.text)
                time.sleep(interval-3)
                if playingtime + interval <= duration:
                    playingtime += interval
                else:
                    playingtime = duration

        finish += 1
        print(f'已完成任务点数:{finish}')


# uname =input('请输入账号:')
# pwd = input('请输入密码:')


cookies = get_cookies(uname, pwd)

course_data = get_course_list(cookies)
for course in course_data:
    print(course)

personid = course_data[0]['personid']

clazzid =input('请输入clazzid:')
courseid = input('请输入courseid:')


finish,total,chapterids = find_chapterid(courseid, clazzid,personid)
finish = int(finish)

print(f'已完成任务点数:{finish},总任务点数:{total}')
# print(chapterids)

interval = 30    #视频提交间隔（建议30到60）

for chapterid in chapterids:
    main(clazzid, courseid, chapterid, personid, cookies,interval)






