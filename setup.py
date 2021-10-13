from setuptools import setup

setup(
    name="afidsvalidator",
    packages=["afidsvalidator"],
    include_package_data=True,
    install_requires=[
        "blinker~=1.4",
        "Flask~=1.1",
        "Flask-Migrate~=2.5",
        "Flask-Script~=2.0",
        "flask-login~=0.4",
        "Flask-Dance[sqla]~=5.0",
        "gunicorn~=20.0",
        "numpy~=1.17",
        "plotly~=4.12",
        "psycopg2-binary~=2.8",
        "python-dotenv~=0.17",
        "WTForms~=2.2",
    ],
)
