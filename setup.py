"""
Setup configuration for MongoDB Atlas Extension
"""

from setuptools import setup, find_packages

setup(
    name='mongodb-atlas-extension',
    version='0.0.18',
    description='Dynatrace Extension for MongoDB Atlas Connection Monitoring',
    author='Yamana',
    author_email='marco.yamana.terceiros@claro.com.br',
    license='ClaroS.A',
    
    packages=find_packages(),
    
    install_requires=[
        'dt-extensions-sdk>=1.0.0',
        'requests>=2.31.0',
        # Dependências transitivas explícitas (necessário para ActiveGate)
        'charset-normalizer>=2.0.0,<4.0.0',
        'certifi>=2023.0.0',
        'idna>=3.0',
        'urllib3>=1.26.0,<3.0.0',
    ],
    
    python_requires='>=3.10',
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    
    entry_points={
        'console_scripts': [
            'mongodb-atlas-extension=mongodb_atlas_extension:main',
        ],
    },
    
    package_data={
        'mongodb_atlas_extension': ['activationSchema.json'],
    },
    
    include_package_data=True,
)