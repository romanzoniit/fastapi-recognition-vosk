from setuptools import find_packages
from setuptools import setup

setup(
    name='fastapi-recognition',
    version='0.0.1',
    author='Ramil B',
    description='FastApi vosk app',
    data_files=[('RECOGNITION_FILES', []),
                ('ARCHIVED_FILES', []),
                ('UPLOADED_FILES', [])
                ],
    install_requires=[
        'anyio==3.6.1',
        'certifi==2022.6.15',
        'cffi==1.15.1',
        'charset-normalizer==2.1.0',
        'click==8.1.3',
        'colorama==0.4.5',
        'fastapi==0.79.0',
        'h11==0.13.0',
        'idna==3.3',
        'pycparser==2.21',
        'pydantic==1.9.1',
        'pydub==0.25.1',
        'python-dotenv==0.20.0',
        'python-multipart==0.0.5',
        'requests==2.28.1',
        'six==1.16.0',
        'sniffio==1.2.0',
        'srt==3.5.2',
        'starlette==0.19.1',
        'tqdm==4.64.0',
        'typing_extensions==4.3.0',
        'urllib3==1.26.11',
        'uvicorn==0.18.2',
        'vosk==0.3.42',
        'rarfile==4.0',
        'unrar==0.4',
        'fastapi-recognition==0.0.1'
    ],
    packages=find_packages(),
    scripts=['recognition']
)
