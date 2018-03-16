from setuptools import setup

version = {}

with open('pdiff/__version__.py', 'r') as f:
  exec(f.read(), version)

with open('README.md', 'r') as f:
  readme = f.read()

setup(
    name='pdiff',
    version=version['__version__'],
    description='Pretty side-by-side diff',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/nkouevda/pdiff',
    author='Nikita Kouevda',
    author_email='nkouevda@gmail.com',
    license='MIT',
    packages=['pdiff'],
    install_requires=[
        'argparse-extensions',
        'colorama',
        'six',
    ],
    entry_points={
        'console_scripts': [
            'pdiff=pdiff.pdiff:main',
        ],
    },
)
