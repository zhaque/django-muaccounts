from setuptools import setup, find_packages

setup(name="django-muaccaunts",
           version="0.1.2",
           description="Domain-based multi-user accounts",
           author="CrowdSense",
           author_email="admin@crowdsense.com",
           packages=find_packages(),
           include_package_data=True,
)

