from setuptools import setup, find_packages

setup(name="tap-contentful",
      version="0.0.2",
      description="Singer.io tap for extracting data from contentful API",
      author="Stitch",
      url="http://singer.io",
      classifiers=["Programming Language :: Python :: 3 :: Only"],
      py_modules=["tap_contentful"],
      install_requires=[
        "singer-python==6.8.0",
        "requests==2.34.2",
        "backoff==2.2.1",
        "parameterized"
      ],
      entry_points="""
          [console_scripts]
          tap-contentful=tap_contentful:main
      """,
      packages=find_packages(),
      package_data = {
          "tap_contentful": ["schemas/*.json"],
      },
      include_package_data=True,
)
