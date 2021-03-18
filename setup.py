""" Setup xHoundPi module """

from setuptools import setup

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

#TODO read short description field from README.md to ensure consistency

setup(
    name='xHoundPi',
    packages=['xHoundPi'],
    version='0.5.0b',
    license='Propietary, see LICENSE file for EULA',
    description='High precision GPS firmware for point surveyor xHound hardware modules based on ARM64 Raspberry Pi platforms.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='xHound',
    author_email='dacabdi@gmail.com',
    url='https://github.com/dacabdi/xhoundpi',
    keywords=[
        'xhound',
        'gps',
        'surveyor',
        'rover',
        'rtk',
    ],
    install_requires=[
    ],
    classifiers=[
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Manufacturing',
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: GIS',
        "Environment :: Handhelds/PDA's",
    ],
)
