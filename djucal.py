import cookielib
import urllib
import urllib2
from contextlib import closing



class DjuAgent(object):
    URL_LOGIN = 'http://intra.dju.kr/servlet/sys.syd.syd01Svl03'
    URL_SCHEDULE = ('http://intra.dju.kr/servlet/sys.syc.syc01Svl15'
                    '?pgm_id=W_SYS032PQ&pass_gbn=&dpt_ck=')

    def __init__(self):
        cookiejar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookiejar))


    def login(self, userid, userpw):
        login_data = urllib.urlencode({
            'proc_gubun': '1',
            'pgm_id': 'SYS200PE',
            'id': userid,
            'pwd': userpw,
        })

        with closing(self.opener.open(self.URL_LOGIN, login_data)) as fp:
            content = fp.read()
            if 'self.location' in content:
                return True

    def get_schedule(self):
        with closing(self.opener.open(self.URL_SCHEDULE)) as fp:
            content = fp.read()
            return content
