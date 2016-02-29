from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


version = '0.3.0'

install_requires = [
    'lxml>=3.4.0',
    'requests>=2.4.3',
]


setup(
    name='dju-intranet',
    version=version,
    description='Daejeon university intranet API',
    long_description=README,
    author='Kjwon15',
    author_email='kjwonmail@gmail.com',
    url='https://github.com/Kjwon15/dju-intranet',
    packages=find_packages(),
    py_modules=['djuintra'],
    zip_safe=False,
    install_requires=install_requires,
)
