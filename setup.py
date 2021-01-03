from setuptools import setup, find_packages

setup(
    python_requires='>=3.9',
    name='Dno',
    url='https://github.com/dmitriy-shikhalev/dno.git',
    author='Dmitriy Shikhalev',
    author_email='dmitriy.shikhalev@gmail.com',
    packages=find_packages(),
    # packages=['dno'],
    install_requires=[
        'aiohttp==3.7.3',
        'pydantic==1.7.3',
    ],
    version='0.1',
    license='GNU GPL v3',
    description='Package for web-based operations with domain objects',
    long_description=open('README.txt').read(),
)
