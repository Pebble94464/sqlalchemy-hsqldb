import os

from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    LONG_DESC :str = fh.read()

setup(
    name="sqlalchemy-hsqldb",
    version="0.1.0",
    description="HSQLDB dialect for SQLAlchemy",
    long_description=LONG_DESC,
    long_description_content_type="text/x-rst",
    author="Jsn",
    author_email="jsn-gh@pebble.plus.com",
    license="MIT",
    url="https://github.com/Pebble94464/sqlalchemy-hsqldb",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        #"Development Status :: 5 - Production/Stable",        
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Database :: Front-Ends",
        "Operating System :: OS Independent",
    ],
    keywords="SQLAlchemy dialect hsqld hypersql",
    project_urls={
        "Documentation": "https://github.com/Pebble94464/sqlalchemy-hsqldb/wiki",
        "Source": "https://github.com/Pebble94464/sqlalchemy-hsqldb",
        "Tracker": "https://github.com/Pebble94464/sqlalchemy-hsqldb/issues",
    },
    packages=find_packages(include=["sqlalchemy_hsqldb"]),
    include_package_data=True,
    install_requires=["SQLAlchemy", "jaydebeapi-hsqldb"],
    zip_safe=False,
    # Specify entry points...
    entry_points={
        "sqlalchemy.dialects": [
            "hsqldb.jaydebeapi = sqlalchemy_hsqldb.jaydebeapi:HyperSqlDialect_jaydebeapi",
            # "<dialect.driver> = <sqlalchemy_dialect.driver>:<dialect driver class>"
        ]
    },
)

# The entry point above allows database urls to be specified, e.g.
#     create_engine("dialect+driver://username:password@host:port/database")

# TODO: remove this line and everything below...
"""
https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
dialect+driver://username:password@host:port/database
Dialect names include the identifying name of the SQLAlchemy dialect,
a name such as sqlite, mysql, postgresql, oracle, or mssql.

The drivername is the name of the DBAPI to be used to connect to the database
using all lowercase letters.
If not specified, a “default” DBAPI will be imported if available
- this default is typically the most widely known driver available for that backend.
"""

