import requests
import re
import execjs
import time
import json
from config import *
import logging
from bs4 import BeautifulSoup
from hashlib import md5
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ====================== 全局配置 ======================
# 初始化Session，自动管理Cookie，添加重试/超时配置
session = requests.Session()
# 配置重试策略
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('https://', adapter)
session.mount('http://', adapter)
# 全局请求头
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
})

# 预编译正则（减少重复编译开销）
RE_JSESSIONID = re.compile(r'JSESSIONID=(.*?);')
RE_ROUTE = re.compile(r'route=(.*?);')
RE_S = re.compile(r'\?s=(.*?)\'')
RE_K8S = re.compile(r'k8s=(.*?);')
RE_JROSE = re.compile(r'jrose=(.*?);')
RE_ENC = re.compile(r'<input type="hidden" id="enc" name="enc" value="(.*?)"/>')
RE_FINISH = re.compile(r'已完成任务点: <span style="color:#00B368">(.*?)<')
RE_TOTAL = re.compile(r'</span>/(\d+)')
RE_V1 = re.compile(r'v=(.*?)&')
RE_V2 = re.compile(r'modules/video/index-review.html\?v=(.*?)"')
RE_USERID = re.compile(r'"userid":"(.*?)",')
RE_MARG = re.compile(r'mArg = (.*?);')
RE_OTHERINFO = re.compile(r'(.*?)&')
RE_NUMBER = re.compile(r'(\d+)')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ====================== 核心函数 ======================
def get_enc(clazzid, userid, jobid, objectid, playingtime, duration, clipTime):
    """生成加密串"""
    template = '[{0}][{1}][{2}][{3}][{4}][{5}][{6}][{7}]'
    result = template.format(
        clazzid, userid, jobid or '', objectid,
        playingtime*1000, 'd_yHJ!$pdA~5', duration * 1000, clipTime
    )
    return md5(result.encode('utf-8')).hexdigest()

def get_cookies(uname, pwd):
    """登录并获取Cookie（Session自动维护，无需返回cookies字典）"""
    # 第一步：获取初始Cookie
    params = {
        'fid': '',
        'newversion': 'true',
        'refer': 'https://i.chaoxing.com',
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://i.chaoxing.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }
    # 使用session发起请求，自动保存Cookie
    session.get('https://passport2.chaoxing.com/login', params=params, headers=headers, timeout=10)

    # 第二步：加载加密JS并获取加密后的账号密码
    with open('encrypt.js', 'r', encoding='utf-8') as f:
        ctx = execjs.compile(f.read())
    data = ctx.call('get_uname_password', uname, pwd)

    # 第三步：提交登录
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://passport2.chaoxing.com',
        'Pragma': 'no-cache',
        'Referer': 'https://passport2.chaoxing.com/login?fid=12&refer=http%3A%2F%2Fi.chaoxing.com%2Fbase%3Ft%3D1768033122232&space=2',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest',
    }
    post_data = {
        'fid': '-1',
        'uname': data['uname'],
        'password': data['password'],
        'refer': 'http%3A%2F%2Fi.chaoxing.com%2Fbase%3Ft%3D' + str(int(1000 * time.time())),
        't': 'true',
        'forbidotherlogin': '0',
        'validate': '',
        'doubleFactorLogin': '0',
        'independentId': '0',
        'independentNameId': '0',
    }
    # Session自动携带Cookie，无需手动传cookies参数
    response = session.post(
        'https://passport2.chaoxing.com/fanyalogin',
        headers=headers,
        data=post_data,
        timeout=10
    )
    if response.status_code != 200:
        raise Exception(f'登录失败，状态码：{response.status_code}')
    # 登录成功后，Session已自动保存所有Cookie，无需手动解析
    logger.info('登录成功，Session已维护Cookie')
    return True  # 只需返回登录成功标识

def get_course_list():
    """获取课程列表（Session自动带Cookie）"""
    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://mooc1-1.chaoxing.com',
        'Pragma': 'no-cache',
        'Referer': 'https://mooc1-1.chaoxing.com/visit/interaction?s=1a02f4c43f48fb2856b975e81df0c67a',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = {
        'courseType': '1',
        'courseFolderId': '0',
        'baseEducation': '0',
        'superstarClass': '',
        'courseFolderSize': '0',
    }
    response = session.post(
        'https://mooc1-1.chaoxing.com/mooc-ans/visit/courselistdata',
        headers=headers,
        data=data,
        timeout=10
    )
    html_content = response.text
    soup = BeautifulSoup(html_content, 'lxml')
    course_items = soup.find_all('li', class_='course clearfix')
    course_data = []
    for item in course_items:
        try:
            course_info = {
                'clazzid': item.attrs.get('clazzid', ''),
                'courseid': item.attrs.get('courseid', ''),
                'id': item.attrs.get('id', ''),
                'personid': item.attrs.get('personid', ''),
                'title': item.find('span', class_='course-name overHidden2').attrs.get('title', '') if item.find('span', class_='course-name overHidden2') else '',
            }
            course_data.append(course_info)
        except Exception as e:
            logger.error(f'解析课程失败：{e}')
            continue
    return course_data

def find_chapterid(courseid, clazzid, personid):
    """查找未完成的章节ID"""
    # 第一步：获取s参数
    params = {'t': f'{int(time.time() * 1000)}'}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Upgrade-Insecure-Requests': '1',
    }
    response = session.get('http://i.chaoxing.com/base', params=params, headers=headers, timeout=10)
    content = response.text
    s_match = RE_S.search(content)
    if not s_match:
        raise Exception('未提取到s参数')
    s = s_match.group(1)

    # 第二步：访问interaction页面（Session自动处理Cookie）
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://i.chaoxing.com/',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Upgrade-Insecure-Requests': '1',
    }
    session.get('https://mooc1-1.chaoxing.com/visit/interaction', params={'s': s}, headers=headers, timeout=10)

    # 第三步：获取enc参数
    params = {
        'courseid': courseid,
        'clazzid': clazzid,
        'vc': '1',
        'cpi': personid,
        'ismooc2': '1',
        'v': '2',
    }
    headers = {'referer': 'https://mooc1-1.chaoxing.com/visit/interaction?s=1a02f4c43f48fb2856b975e81df0c67a'}
    response = session.get(
        'https://mooc1-1.chaoxing.com/mooc-ans/visit/stucoursemiddle',
        params=params,
        headers=headers,
        timeout=10
    )
    enc_match = RE_ENC.search(response.text)
    if not enc_match:
        raise Exception('未提取到enc参数')
    enc = enc_match.group(1)

    # 第四步：获取章节进度
    params = {
        'courseid': courseid,
        'clazzid': clazzid,
        'cpi': personid,
        'ut': 's',
        't': f'{int(time.time() * 1000)}',
        'stuenc': enc,
    }
    headers = {
        'host': 'mooc2-ans.chaoxing.com',
        'upgrade-insecure-requests': '1',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'iframe',
        'priority': 'u=0, i',
    }
    response = session.get(
        'https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse',
        params=params,
        headers=headers,
        timeout=10
    )
    content = response.text

    # 提取完成/总任务点
    finish_match = RE_FINISH.search(content)
    total_match = RE_TOTAL.search(content)
    finish = finish_match.group(1) if finish_match else '0'
    total = total_match.group(1) if total_match else '0'

    # 1. 解析HTML
    soup = BeautifulSoup(content, 'html.parser')

    # 2. 提取符合条件的id（用Python原生strip()处理空白，避免转义问题）
    unfinished_ids = []
    for item in soup.find_all('div', class_='chapter_item'):
        # 用Python的strip()去除文本首尾空白，替代错误的JS正则写法
        item_text = item.get_text().strip()  # 等价于去除首尾空白，无转义警告
        if '待完成任务点' in item_text:
            item_id = item.get('id')
            number = RE_NUMBER.findall(item_id)[0]
            unfinished_ids.append(number)

    return finish, total, unfinished_ids

def get_cards_v(courseid, clazzid, chapterid):
    """获取cards_v参数"""
    params = {
        'courseId': courseid,
        'clazzid': clazzid,
        'chapterId': chapterid,
        'cpi': '0',
        'verificationcode': '',
        'mooc2': '1',
        'microTopicId': '0',
        'editorPreview': '0',
    }
    response = session.get(
        'https://mooc1.chaoxing.com/mooc-ans/mycourse/studentstudyAjax',
        params=params,
        timeout=10
    )
    v_match = RE_V1.search(response.text)
    if not v_match:
        logger.error('未提取到cards_v参数')
        return None
    return v_match.group(1)

def get_v(v):
    """获取最终v参数"""
    params = {'v': v}
    response = session.get(
        'https://mooc1.chaoxing.com/ananas/ueditor/ueditor.parse.js',
        params=params,
        timeout=10
    )
    v_match = RE_V2.search(response.text)
    if not v_match:
        logger.error('未提取到最终v参数')
        return None
    return v_match.group(1)

def get_dtoken(v, objectid):
    """获取dtoken参数"""
    headers = {'Referer': f'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v={v}'}
    params = {
        'k': session.cookies.get('fid', ''),  # 从Session的Cookie中获取fid
        'flag': 'normal',
        'ro': '0',
        '_dc': f'{int(time.time() * 1000)}',
    }
    response = session.get(
        f'https://mooc1.chaoxing.com/ananas/status/{objectid}',
        params=params,
        headers=headers,
        timeout=10
    )
    try:
        json_data = response.json()
        return json_data.get('dtoken')
    except Exception as e:
        logger.error(f'获取dtoken失败：{e}')
        return None

def main(clazzid, courseid, chapterid, personid, interval):
    """提交视频进度"""
    cards_v = get_cards_v(courseid, clazzid, chapterid)
    if not cards_v:
        logger.warning(f'章节{chapterid}未获取到cards_v，跳过')
        return

    # 获取userid和v参数
    params = {
        'clazzid': clazzid,
        'courseid': courseid,
        'knowledgeid': chapterid,
        'num': '0',
        'ut': 's',
        'cpi': personid,
        'v': cards_v,
        'mooc2': '1',
        'isMicroCourse': 'false',
        'editorPreview': '0',
    }
    response = session.get('https://mooc1.chaoxing.com/mooc-ans/knowledge/cards', params=params, timeout=10)
    userid_match = RE_USERID.search(response.text)
    if not userid_match:
        logger.warning(f'章节{chapterid}未提取到userid，跳过')
        return
    userid = userid_match.group(1)

    # 提取v参数
    v_match = re.search(r'<link type="text/css" href="/ananas/ueditor/themes/iframe.css\?v=(.*?)" rel="stylesheet" />', response.text)
    if not v_match:
        logger.warning(f'章节{chapterid}未提取到v参数，跳过')
        return
    v = get_v(v_match.group(1))
    if not v:
        return

    # 解析视频数据
    mArg = RE_MARG.findall(response.text)
    if len(mArg) < 2:
        logger.warning(f'章节{chapterid}未提取到mArg，跳过')
        return
    try:
        datas = json.loads(mArg[1])['attachments']
    except Exception as e:
        logger.error(f'解析mArg失败：{e}')
        return

    logger.info(f'开始处理章节{chapterid}')
    for data in datas:
        try:
            if data.get('type') != 'video':
                continue
            duration = data.get('attDuration', 0)
            objectid = data.get('property', {}).get('objectid')
            if not objectid:
                continue
            otherInfo = data.get('otherInfo', '')
            otherInfo = RE_OTHERINFO.search(otherInfo).group(1) if RE_OTHERINFO.search(otherInfo) else ''
            jobid = data.get('property', {}).get('jobid') or data.get('property', {}).get('_jobid')
            attDurationEnc = data.get('attDurationEnc', '')
            videoFaceCaptureEnc = data.get('videoFaceCaptureEnc', '')
            clipTime = f'0_{duration}'
            dtoken = get_dtoken(v, objectid)
            if not dtoken:
                continue

            # 循环提交进度
            playingtime = 0
            n = duration // interval
            for i in range(n + 2):
                logger.info(f'章节{chapterid} - 已提交时长:{playingtime} / 总时长:{duration}')
                enc = get_enc(clazzid, userid, jobid, objectid, playingtime, duration, clipTime)
                params = {
                    'clazzId': clazzid,
                    'playingTime': playingtime,
                    'duration': duration,
                    'clipTime': clipTime,
                    'objectId': objectid,
                    'otherInfo': otherInfo,
                    'courseId': courseid,
                    'jobid': jobid,
                    'userid': userid,
                    'isdrag': '0',
                    'view': 'pc',
                    'enc': enc,
                    'rt': '0.9',
                    'videoFaceCaptureEnc': videoFaceCaptureEnc,
                    'dtype': 'Video',
                    '_t': int(time.time() * 1000),
                    'attDuration': duration,
                    'attDurationEnc': attDurationEnc,
                }
                # 提交进度
                resp = session.get(
                    f'https://mooc1.chaoxing.com/mooc-ans/multimedia/log/a/{personid}/{dtoken}',
                    params=params,
                    timeout=10
                )
                resp_json = resp.json()
                if resp_json.get('isPassed'):
                    logger.info(f'章节{chapterid}进度提交完成，已通过')
                    break
                # 休眠（避免过快请求）
                time.sleep(max(1, interval - 3))
                time.sleep(random.randint(1,3)) #随机休眠1-3秒
                # 更新播放时长
                if playingtime + interval <= duration:
                    playingtime += interval
                else:
                    playingtime = duration
        except Exception as e:
            logger.error(f'处理章节{chapterid}视频失败：{e}')
            continue

# ====================== 主程序 ======================
if __name__ == "__main__":
    # 请手动输入账号密码，或从config.py导入
    # uname = input('请输入学习通账号：')
    # pwd = input('请输入学习通密码：')

    try:
        # 登录（Session自动维护Cookie）
        get_cookies(uname, pwd)
        # 获取课程列表
        course_data = get_course_list()
        logger.info('已获取课程列表：')
        for idx, course in enumerate(course_data):
            logger.info(f'{idx+1}. {course["title"]} - clazzid:{course["clazzid"]} - courseid:{course["courseid"]}')

        if not course_data:
            logger.error('未获取到任何课程')
            exit(1)

        personid = course_data[0]['personid']

        clazzid = input('\n请输入要学习的课程clazzid：')
        courseid = input('请输入要学习的课程courseid：')

        # 查找未完成章节
        finish, total, chapterids = find_chapterid(courseid, clazzid, personid)
        finish = int(finish)
        logger.info(f'已完成任务点数:{finish}, 总任务点数:{total}')
        logger.info(f'待完成章节{chapterids}')
        logger.info(f'待完成章节数量：{len(chapterids)}')

        # 配置提交间隔（建议30-60秒）
        interval = 30
        # 逐个处理章节
        for chapterid in chapterids:
            main(clazzid, courseid, chapterid, personid, interval)

        logger.info('所有章节处理完成')
    except Exception as e:
        logger.error(f'程序执行失败：{e}')


