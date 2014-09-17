Dju calendar
============

This project gives you schedule of Daejeon university.
Daejeon university's web sites are sucks. So I made it.


Examples
--------

Login
~~~~~

.. code-block:: python

   >>> import djuintra
   >>> agent = djuintra.DjuAgent()
   >>> agent.login('<User ID>', '<User PW>')
   >>> # returns True if logged in successfully.


Get Time tables
~~~~~~~~~~~~~~~

.. code-block:: python

   >>> for timetable in da.get_timetables(2014, 2, 0, '00000', 0):
   ...     print(u'{0.classname} by {0.profname} {0.score}/{0.time}'.format(timetable))
   대학영어(1) by 제임스썸머필드 2/2
   대학영어(1) by 페리 2/2
   대학영어(1) by 네드콕스 2/2
   대학영어(1) by 티머시롤랜드 2/2
   대학영어(1) by 브라이언맥컬리 2/2
   대학영어(1) by 제임스썸머필드 2/2
   대학영어(1) by 페리 2/2
   대학영어(1) by 네드콕스 2/2
   대학영어(1) by 티머시롤랜드 2/2
   대학영어(1) by 브라이언맥컬리 2/2
   대학영어(1) by 아담드레슬러 2/2
   대학영어(1) by 마이너 2/2
   대학영어(1) by 로드리고버뮤즈 2/2


Get Schedules
~~~~~~~~~~~~~

.. code-block:: python

   >>> for schedule in da.get_schedules():
   ...     print(u'{0.title}({0.depart}): {0.start}~{0.end}'.format(schedule))
   ...
   수업일수1/3선(학사서비스팀): 2014-10-05 09:00:00~2014-10-05 23:59:59
   전역복학마감일자(개강후3주내)(학사서비스팀): 2014-09-19 17:30:00~None
   휴학신청기간(학사서비스팀): 2014-08-04 09:00:00~2014-08-14 17:30:00
   복학신청기간(학사서비스팀): 2014-07-14 09:00:00~2014-07-25 17:30:00
   부/복수전공신청기간(학사서비스팀): 2014-07-07 09:00:00~2014-07-11 17:30:00
   모의토익원서접수신청기간(외국어교육센터): 2014-09-15 12:00:00~2014-09-19 17:00:00

