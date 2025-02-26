from pathlib import Path

from setuptools import find_packages, setup

def get_requirements() -> list[str]:
    try:
        content = Path("requirements.txt").read_text()
    except FileNotFoundError:
        content = Path("../requirements.txt").read_text()
    return [x.strip() for x in content.split("\n") if not x.startswith("#")]


install_requires = get_requirements()

setup(
    name='app',
    version='0.1',
    package_dir={'': 'src'},
    packages=find_packages("src"),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={"console_scripts": ["image = cli:entrypoint"]}
)
