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

__all__ = ('DjuAgent', 'Score', 'Scores', 'Semester', 'Schedule', 'TimePlace',
           'TimeTable')


Schedule = namedtuple('Schedule', ('title', 'start', 'end', 'depart'))
TimePlace = namedtuple('TimePlace', ('time', 'place'))


class TimeTable(namedtuple('TimeTable', (
                           'grade', 'division', 'code', 'classcode',
                           'classtype', 'classname', 'score', 'time', 'minor',
                           'profname', 'times', 'maxstudents', 'available'))):
    """Named tuple for time table.

    :param grade: Required grade for the course
    :type grade: :class:`int`

    :param division: Liberal or major and somthing else
    :type division: :class:`str`

    :param code: Course code for registration
    :type code: :class:`str`

    :param classcode: Class number for registration
    :type classcode: :class:`str`

    :param classname: Name of the course
    :type classname: :class:`str`

    :param score: Credits
    :type score: :class:`int`

    :param time: how many time costs for this class for one week
    :type time: :class:`int`

    :param minor: Is it need to minor?
    :type minor: :class:`str`

    :param profname: The name of the professor
    :type profname: :class:`str`

    :param times: When is the class
    :type times: A set of :class:`TimePlace`

    :param maxstudents: How many students can listen this class
    :type maxstudents: :class:`int`

    :param available: Is this class available?
    :type available: :class:`str`

    """
    pass


class Scores(namedtuple('Scores', ('averagescore', 'semesters'))):
    """All personal scores.

    :param averagescore: Average score for you
    :type averagescore: :class:`float`

    :param semesters: A set of :class:`Semester`
    :type semesters: :class:`collections.Iterable`

    """
    pass


class Semester(namedtuple('Semester', ('title', 'scores'))):
    """Scores for the semester

    :param title: Title of the semester
    :type title: :class:`str`

    :param scores: A set of :class:`Score`
    :type scores: :class:`collections.Iterable`

    """
    pass


class Score(namedtuple('Score', ('code', 'title', 'point', 'score'))):
    """Personal scores data.

    :param code: Cource code
    :type code: :class:`str`

    :param title: Cource title
    :type title: :class:`str`

    :param point: Credits for course
    :type point: :class:`float`

    :param score: Your score
    :type score: :class:`str`

    """
    pass


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
    URL_PERSONAL_SCORES = ('http://intra.dju.kr/servlet/su.suh.suh04Svl01?'
                           'pgm_id=W_SUH080PQ&pass_gbn=001&dpt_ck=')
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

        :returns: :const:`None` if login successfully

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
                errorcode, msg = self._get_error_code(content)

                if errorcode == 22:
                    raise ValueError('Password not matched')
                elif errorcode == 99:
                    raise ValueError('User id not found')
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
                grade = int(grade) if grade else None
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

    def get_personal_scores(self):
        """Get personal total scores

        :returns: A personal scores group by semesters and Average score
        :rtype: :class:`Scores`
        """
        with closing(self.opener.open(self.URL_PERSONAL_SCORES)) as fp:
            content = fp.read()
            tree = html.fromstring(content)
            table_semesters = tree.xpath('//table')[3:-2]
            total_score = tree.xpath('//table')[-2]

            semesters = []
            for table in table_semesters:
                title = table.find('tr[1]').text_content().strip()
                rows = table.xpath('.//tr')[2:-1]
                scores = (Score(
                    code=row.find('td[3]').text_content().strip(),
                    title=row.find('td[4]').text_content().strip(),
                    point=float(row.find('td[5]').text_content().strip()),
                    score=row.find('td[6]').text_content().strip(),
                ) for row in rows)
                semesters.append(Semester(
                    title=title,
                    scores=scores,
                ))

            average_score = float(total_score.xpath('.//td')[-1].text_content())

            return Scores(
                semesters=semesters,
                averagescore=average_score,
            )

    @classmethod
    def _get_error_code(cls, content):
        tree = html.fromstring(content)
        error = tree.xpath('//td')[0].text_content().strip()
        code = int(re.search(r'\d+', error).group())
        msg = tree.xpath('//td')[3].text_content().strip()

        return (code, msg)
