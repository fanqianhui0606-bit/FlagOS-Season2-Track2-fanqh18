from setuptools import setup, find_packages

setup(
    name="flag-gems",
    version="5.3.5",
    description="FlagGems: An Open-Source High-Performance Operator Library for Multiple AI Chips",
    packages=find_packages(),
    install_requires=[
        "torch>=2.4.0",
        "triton>=3.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
