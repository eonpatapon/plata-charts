from setuptools import setup, find_packages

install_requires = [
    'django-datetime-widget'
]

setup(
    name='plata_charts',
    version='0.1',
    description="Order charts for the Plata shop",
    author="Jean-Philippe Braun",
    author_email="eon@patapon.info",
    maintainer="Jean-Philippe Braun",
    maintainer_email="eon@patapon.info",
    url="http://www.github.com/eonpatapon/plata-charts/",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    scripts=[],
    license="MIT",
)
