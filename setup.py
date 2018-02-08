from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_module_coapthon',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Carlo Vallati',
    author_email='carlo.vallati@unipi.it',
    description='WiSHFUL Module Coapthon',
    long_description='WiSHFUL Module oapthon',
    keywords='traffic generation',
    install_requires=[]
)
