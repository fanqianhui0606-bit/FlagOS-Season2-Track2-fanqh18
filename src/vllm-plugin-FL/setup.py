from setuptools import setup, find_packages

setup(
    name="vllm-plugin-fl",
    version="0.2.0",
    description="FlagOS Unified Multi-Chip Backend Plugin for vLLM (Season 2)",
    packages=find_packages(),
    install_requires=[
        "vllm>=0.6.0",
        "torch>=2.4.0",
    ],
    entry_points={
        "vllm.plugins": [
            "fl = vllm_fl:register"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
