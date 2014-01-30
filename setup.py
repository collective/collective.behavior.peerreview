from setuptools import setup
from setuptools import find_packages

version = '0.0.1'

setup(
    name='collective.behavior.peerreview',
    version=version,
    description="Provide peer review process for any Plone content type.",
    long_description=(
        open("README.rst").read() + "\n" +
        open("CHANGES.rst").read(),
    ),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='plone collective behavior dexterity peer review',
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/collective/collective.behavior.peerreview',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.behavior'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'plone.app.dexterity',
        'plone.app.widgets[dexterity]',
        'plone.behavior',
        'plone.directives.form',
        'setuptools',
    ],
    extras_require = {
        'test': ['plone.app.testing']
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
