long_description =  """\
The package *cypari* is a Python wrapper for the `PARI library
<http://pari.math.u-bordeaux.fr/>`_, a computer algebra system for
number theory computations.  It is derived from the `corresponding
component
<http://doc.sagemath.org/html/en/reference/libs/sage/libs/pari/index.html>`_
of `Sage <http://www.sagemath.org>`_, but is independent of the rest of
Sage and can be used with any recent version of Python.
"""

from setuptools import setup, Command
from distutils.extension import Extension
from distutils.command.build_ext import build_ext
from Cython.Build import cythonize
import os, sys


def manually_compile_files(sources, extra_include_dirs):
    import distutils.sysconfig
    import distutils.ccompiler
    config_vars = distutils.sysconfig.get_config_vars()
    python_include_dir = config_vars['INCLUDEPY']
    compiler = distutils.ccompiler.new_compiler()
    distutils.sysconfig.customize_compiler(compiler)
    compiler.add_include_dir(python_include_dir)
    for directory in extra_include_dirs:
        compiler.add_include_dir(directory)
    compiler.compile(sources=sources)


pari_include_dir = 'build/pari/include'
pari_library_dir = 'build/pari/lib'
pari_static_library = os.path.join(pari_library_dir, 'libpari.a')
cysignals_include_dir = 'cypari/cysignals'
    
class Clean(Command):
    user_options = []
    def initialize_options(self):
        pass 
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -rf build/lib* build/temp* build/bdist* dist')
        os.system('rm -rf cypari*.egg-info')
        os.system('rm -if cypari/*.c')
        os.system('rm -if cypari/*.pyc')
        os.system('rm -if cypari/*.so*')
        os.system('rm -if cypari/cysignals/alarm.c')
        os.system('rm -if cypari/cysignals/signals.c')
        os.system('rm -if cypari/cysignals/signals.h')
        os.system('rm -if cypari/cysignals/signals_api.h')
        os.system('rm -if cypari/cysignals/implementation.o')
        
class CyPariBuildExt(build_ext):
    def __init__(self, dist):
        build_ext.__init__(self, dist)
        
    def run(self):
        build_ext.run(self)

if not os.path.exists('build/pari') and 'clean' not in sys.argv:
#    if sys.platform == 'win32':
#        sys.exit('Please run the bash script build_pari.sh first.')
    if os.system('bash build_pari.sh') != 0:
        sys.exit("***Failed to build PARI library***")

if (not os.path.exists('cypari/auto_gen.pxi')
    or not os.path.exists('cypari/auto_instance.pxi')):
    import autogen
    autogen.autogen_all()

include_dirs = []
if 'clean' not in sys.argv:
    include_dirs=[pari_include_dir, cysignals_include_dir]
    cython_sources = ['cypari/gen.pyx',
                      'cypari/cysignals/signals.pyx']
    if sys.platform != 'win32':
                      cython_sources.append('cypari/cysignals/alarm.pyx')
    cythonize(cython_sources)
    manually_compile_files(['cypari/cysignals/implementation.c'],
                           [pari_include_dir])

pari_gen = Extension('cypari.gen',
                     sources=['cypari/gen.c'],
                     include_dirs=include_dirs,
                     extra_link_args=[pari_static_library],
                     extra_compile_args=['-g']
)

cysignals_sources = ['cypari/cysignals/signals.c']
#                     'cypari/cysignals/implementation.c']
    
cysignals = Extension('cypari.cysignals.signals',
                      sources=cysignals_sources,
                      include_dirs=include_dirs,
                      extra_link_args=[pari_static_library],
)

alarm = Extension('cypari.cysignals.alarm',
                     sources=['cypari/cysignals/alarm.c'],
                     include_dirs=include_dirs,
)

# Load version number
exec(open('cypari/version.py').read())

cypari_extensions = [pari_gen, cysignals]
if sys.platform != 'win32':
    cypari_extensions.append(alarm)
setup(
    name = 'cypari',
    version = version,
    description = "Sage's PARI extension, modified to stand alone.",
    packages = ['cypari', 'cypari.cysignals'],
    package_dir = {'cypari':'cypari', 'cypari.cysignals':'cypari/cysignals'},
    cmdclass = {'clean':Clean, 'build_ext':CyPariBuildExt},
    ext_modules = cypari_extensions,
    zip_safe = False,
    long_description = long_description,
    url = 'https://bitbucket.org/t3m/cypari',
    author = 'Marc Culler and Nathan M. Dunfield',
    author_email = 'culler@uic.edu, nathan@dunfield.info',
    license='GPLv2+',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
    keywords = 'Pari, Sage, SnapPy',
)

