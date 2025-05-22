from setuptools import setup, find_packages

setup(
    name="oracle_to_postgres_analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "sqlparse>=0.4.3",
    ],
    author="Oracle to PostgreSQL Migration Team",
    author_email="example@example.com",
    description="A toolkit for analyzing Oracle SQL queries and MyBatis dynamic queries for PostgreSQL migration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/oracle-to-postgres-analyzer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "analyze-sql=oracle_to_postgres_analyzer.src.query_complexity_analyzer:main",
            "analyze-mybatis=oracle_to_postgres_analyzer.src.mybatis_query_analyzer:main",
            "analyze-sql-dir=oracle_to_postgres_analyzer.src.sql_directory_analyzer:main",
        ],
    },
)
