from setuptools import setup
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='lavacord.py',
    version='1.0.0a',
    description='Its a lavalink nodes manger to make a music bots for discord with python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CraazzzyyFoxx/lavacord.py',
    author='CraazzzyyFoxx',
    author_email='hazemmeqdad@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='lavalink, discord, discord-lavalink, lavacord.py',
    packages=["lavacord", "lavacord.types"],
    install_requires=["aiohttp", "hikari", "yarl", "tekore"],
    project_urls={
        'Bug Reports': 'https://github.com/CraazzzyyFoxx/lavacord.py/issues',
        'Source': 'https://github.com/CraazzzyyFoxx/lavacord.py/',
    },
)
