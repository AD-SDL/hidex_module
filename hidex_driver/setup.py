import os
from setuptools import setup, find_packages


package_name = 'hidex_driver'

setup(
    name='hidex_driver',
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[],
    zip_safe=True,
    python_requires=">=3.8",
    maintainer='Rafael Vescovi',
    maintainer_email='ravescovi@anl.gov',
    description='',
    url='', 
    license='MIT License',
    entry_points={ 
        'console_scripts': []
    },
)
