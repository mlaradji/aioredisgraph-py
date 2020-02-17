from setuptools import setup, find_packages
import io

def read_all(f):
    with io.open(f, encoding="utf-8") as I:
        return I.read()


requirements = list(map(str.strip, open("requirements.txt").readlines()))


setup(
    name='aioredisgraph',
    version='0.0.1',
    description='Asynchronous RedisGraph Python Client',
    long_description=read_all("README.md"),
    long_description_content_type='text/markdown',
    url='https://github.com/mlaradji/aioredisgraph-py/',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database'
    ],
    keywords='Asynchronous Redis Graph Extension',
    author='Mohamed Laradji',
    author_email='malaradji@gmail.com'
)
