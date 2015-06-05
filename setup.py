import setuptools
import base64

setuptools.setup(
    name = 'netlogin',
    version = '0.2',
    py_modules = ['netlogin'],

    author = 'lf',
    # Obfuscated, I don't like spam
    author_email = base64.b64decode(b'cHl0aG9uQGxmY29kZS5jYQ==').decode(),
    description = 'Easily sign into networks using captive portals',
    license = 'MIT',
    keywords = 'captive-portal',
    url = 'https://github.com/lf-/netlogin',

    install_requires = ['python-networkmanager>=0.9'],

    entry_points = {
        'console_scripts': [
            'netlogin = netlogin:main'
        ]
    },

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Networking'
    ]
)
