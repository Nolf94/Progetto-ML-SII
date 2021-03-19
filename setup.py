from setuptools import setup, find_packages

setup(
    name='lodreranker',
    version='0.1a',

    author='Marco Bellocchi, Lorenzo Guidaldi',
    author_email='lor.guidaldi@stud.uniroma3.it',

    packages=find_packages(),
    include_package_data=True,
    scripts=['bgm_lodreranker/manage.py'],

    install_requires=(
        'django==2.2.18',
    )
)
