import cookielib
import datetime
import urllib
import urllib2
from collections import namedtuple
from contextlib import closing
from lxml import html


Schedule = namedtuple('Schedule', ('title', 'start', 'end', 'depart'))


class DjuAgent(object):
    URL_LOGIN = 'http://intra.dju.kr/servlet/sys.syd.syd01Svl03'
    URL_SCHEDULE = ('http://intra.dju.kr/servlet/sys.syc.syc01Svl15'
                    '?pgm_id=W_SYS032PQ&pass_gbn=&dpt_ck=')
    DATE_FORMAT = '%Y-%m-%d %H-%M-%S'

    def __init__(self, userid=None, userpw=None):
        cookiejar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookiejar))

        if userid and userpw:
            self.login(userid, userpw)

    def login(self, userid, userpw):
        login_data = urllib.urlencode({
            'proc_gubun': '1',
            'pgm_id': 'SYS200PE',
            'id': userid,
            'pwd': userpw,
        })

        with closing(self.opener.open(self.URL_LOGIN, login_data)) as fp:
            content = fp.read()
            if 'self.location' not in content:
                tree = html.fromstring(content)
                msg = tree.xpath('//td')[3].text_content().strip()
                raise ValueError(msg.encode('utf-8'))

    def get_schedules(self):
        with closing(self.opener.open(self.URL_SCHEDULE)) as fp:
            content = fp.read()
            tree = html.fromstring(content)
            trs = tree.xpath('//tr')[6:]

            for tr in trs:
                title = tr.find('td[1]').text_content().strip()
                start = datetime.datetime.strptime(
                    tr.find('td[2]').text_content().strip(),
                    self.DATE_FORMAT)
                try:
                    end = datetime.datetime.strptime(
                        tr.find('td[3]').text_content().strip(),
                        self.DATE_FORMAT)
                except ValueError:
                    end = None

                depart = tr.find('td[4]').text_content().strip()

                yield Schedule(title, start, end, depart)
