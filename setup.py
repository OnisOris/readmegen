from setuptools import setup, find_packages, Extension

def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='readmegen',
    version='0.0.1',
    author='OnisOris',
    author_email='onisoris@yandex.ru',
    description='Module for autogenerating readme files from restructured comments',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/OnisOris/readmegen',
    packages=find_packages(),
    install_requires=['code2flow'],
    classifiers=[
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent'
    ],
    keywords='restructuredtext rest markdown md doc',
    project_urls={
        'GitHub': 'https://github.com/OnisOris/readmegen'
    },
    python_requires='>=3.9'
)
