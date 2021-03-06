import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='lavacord.py',
    version='1.0.4a1',
    description='Its a lavalink nodes manger to make a music bots for discord with python.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CraazzzyyFoxx/lavacord.py',
    author='CraazzzyyFoxx',
    author_email='38073783+CraazzzyyFoxx@users.noreply.github.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='lavalink, discord, discord-lavalink, lavacord.py',
    packages=["lavacord", "lavacord.types"],
    install_requires=["aiohttp", "hikari", "yarl", "tekore", "pydantic"],
    project_urls={
        'Bug Reports': 'https://github.com/CraazzzyyFoxx/lavacord.py/issues',
        'Source': 'https://github.com/CraazzzyyFoxx/lavacord.py/',
    },
)
