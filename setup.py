import ast
from pathlib import Path

from setuptools import setup


HERE = Path(__file__).resolve().parent


def get_version():
    """Read __version__ without importing the package."""
    module = ast.parse((HERE / "toolshed" / "__init__.py").read_text(encoding="utf-8"))
    for node in ast.walk(module):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                return ast.literal_eval(node.value)
    raise ValueError("version could not be located")


setup(
    name="toolshed",
    version=get_version(),
    description="Tools for data",
    long_description=(HERE / "README.rst").read_text(encoding="utf-8"),
    long_description_content_type="text/x-rst",
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: BSD License",
    ],
    keywords="bioinformatics",
    author="Brent Pedersen",
    author_email="bpederse@gmail.com",
    url="https://github.com/brentp/toolshed/",
    license="BSD-2-Clause",
    python_requires=">=3.8",
    packages=["toolshed"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points={"console_scripts": ["toolshed=toolshed:main"]},
)
