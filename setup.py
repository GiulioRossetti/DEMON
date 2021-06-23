from setuptools import setup, find_packages
from codecs import open
from os import path

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


here = path.abspath(path.dirname(__file__))

def get_requirements(remove_links=True):
    """
    lists the requirements to install.
    """

    # try:
    with open(path.join(here, 'requirements.txt')) as f:
        requirements = f.read().splitlines()
    # except Exception as ex:
    #    with open('DecoraterBotUtils.egg-info\requires.txt') as f:
    #        requirements = f.read().splitlines()
    if remove_links:
        for requirement in requirements:
            # git repository url.
            if requirement.startswith("git+"):
                requirements.remove(requirement)
            # subversion repository url.
            if requirement.startswith("svn+"):
                requirements.remove(requirement)
            # mercurial repository url.
            if requirement.startswith("hg+"):
                requirements.remove(requirement)
    return requirements


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='demon',
      version='2.0.6',
      license='BSD-2-Clause',
      description='Community Discovery algorithm',
      url='https://github.com/GiulioRossetti/DEMON',
      author='Giulio Rossetti',
      author_email='giulio.rossetti@gmail.com',
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 5 - Production/Stable',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: BSD License',

          "Operating System :: OS Independent",

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3'
      ],
      keywords=['complex-networks', 'community discovery'],
      install_requires=get_requirements(),
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test", "demon.test", "demon.test.*"]),
      )
