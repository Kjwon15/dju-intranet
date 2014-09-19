""":mod:`djuintra` --- Api for Dju intranet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This modules provides an API for Daejeon university's intranet.

"""
import cookielib
import datetime
import re
import urllib
import urllib2
from collections import namedtuple
from contextlib import closing
from lxml import html

__all__ = ('DjuAgent', 'Schedule', 'TimePlace', 'TimeTable')


Schedule = namedtuple('Schedule', ('title', 'start', 'end', 'depart'))
TimeTable = namedtuple('TimeTable', (
    'grade', 'division', 'code', 'classcode', 'classtype', 'classname', 'score',
    'time', 'minor', 'profname', 'times', 'maxstudents', 'available'))
TimePlace = namedtuple('TimePlace', ('time', 'place'))


class DjuAgent(object):
    """Main class for using Dju intranet.

    You can login with constructor if you gives ID and PW.

    :param userid: User's ID for login
    :type userid: :class:`str`

    :param userpw: User's password for login
    :type userpw: :class:`str`

    """
    URL_LOGIN = 'http://intra.dju.kr/servlet/sys.syd.syd01Svl03'
    URL_SCHEDULE = ('http://intra.dju.kr/servlet/sys.syc.syc01Svl15'
                    '?pgm_id=W_SYS032PQ&pass_gbn=&dpt_ck=')
    # TODO: documentation departcode.
    URL_TIMETABLE = ('http://intra.dju.kr/myhtml/su/sue/schedule/'
                     '{year}-{semester}{isbreak}-001'
                     '-{departcode}-{category}.htm')
    DATE_FORMAT = '%Y-%m-%d %H-%M-%S'

    TIMETABLE_CATEGORIES = {
        'all': 0,
        'liberal': 1,
        'major': 2,
    }

    def __init__(self, userid=None, userpw=None):
        cookiejar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookiejar))

        if userid and userpw:
            self.login(userid, userpw)

    def login(self, userid, userpw):
        """Login to Dju intranet.

        :param userid: User's ID for login
        :type userid: :class:`str`

        :param userpw: User's password for login
        :type userpw: :class:`str`

        :returns: :const:`True` if login successfully

        """
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
                error = tree.xpath('//td')[0].text_content().strip()
                code = int(re.search(r'\d+', error).group())

                if code == 22:
                    raise ValueError('Password not matched')
                elif code == 99:
                    raise ValueError('User id not found')

                msg = tree.xpath('//td')[3].text_content().strip()
                raise ValueError(msg)

    def get_schedules(self):
        """Get schedules from intranet.

        :returns: a set of :class:`Schedule`
        :rtype: :class:`collections.Iterable`

        """

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

    def get_timetables(self, year, semester, isbreak, departcode, category):
        """Get full timetables.

        :param year: a year for timetables
        :type year: :class:`str` or :class:`int`

        :param semester: 1 for spring, 2 for fall
        :type semester: :class:`str` or :class:`int`

        :param isbreak: 0 for normal semester, 1 for break semester
        :type isbreak: :class:`str` or :class:`int`

        :param departcode: 5 digit code for department. for example, '000000'
                           for all
        :type departcode: :class:`str`

        :param category: 0 for all, 1 for liberal, 2 for major
        :type category: :class:`str` or :class:`int`

        :returns: a set of :class:`TimeTable`
        :rtype: :class:`collections.Iterable`

        """
        url = self.URL_TIMETABLE.format(
            year=year, semester=semester, isbreak=isbreak,
            departcode=departcode, category=category)
        with closing(self.opener.open(url)) as fp:
            content = fp.read()
            tree = html.fromstring(content)
            trs = tree.xpath('//table[3]/tr')[1:]

            for tr in trs:
                grade = tr.find('td[1]').text_content().strip()
                division = tr.find('td[2]').text_content().strip()
                code = tr.find('td[3]').text_content().strip()
                classcode = tr.find('td[4]').text_content().strip()
                classtype = tr.find('td[5]').text_content().strip()
                classname = tr.find('td[6]').text_content().strip()
                score = int(tr.find('td[7]').text_content().strip())
                time = int(tr.find('td[8]').text_content().strip())
                minor = tr.find('td[9]').text_content().strip()
                profname = tr.find('td[10]').text_content().strip()
                # FIXME: parse this to array
                _times = tr.xpath('td[11]//font')
                times = []
                for i in xrange(0, len(_times), 2):
                    times.append(TimePlace(_times[i].text_content().strip(),
                                 _times[i+1].text_content().strip()))
                maxstudents = int(tr.find('td[12]').text_content().strip())
                available = tr.find('td[13]').text_content().strip()

                yield TimeTable(grade, division, code, classcode, classtype,
                                classname, score, time, minor, profname, times,
                                maxstudents, available)
