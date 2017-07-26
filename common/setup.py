from setuptools import setup, find_packages

setup(
    name='common',
    version='0.0.1',
    author='Allef Pablo Araujo',
    description='Python common packages for test applications',
    url='https://github.com/lnls-elp/jigas/common',
    download_url='https://github.com/lnls-elp/jigas/common',
    license='MIT License',
    classifier=[
        'Intended Audience :: Science/Research',
        'Programmming Language :: Python',
        'Topic :: Test Applications'
    ],
    packages=find_packages(),
    package_data={'common':['VERSION']},
    zip_safe=False
)
