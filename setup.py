from setuptools import setup, find_packages

setup(
    name="bootstrap",
    version="1.0.0",
    packages=find_packages(),
    author="Tommy Carpenter",
    author_email="tommyjcarpenter@gmail.com",
    description=("Dev env bootstrapping"),
    license="MIT",
    url="https://github.com/tommyjcarpenter/dev-bootstrap",
    install_requires=["click"],
    scripts=["bin/runboot.py"],
)
