import distutils.core
import Cython.Build

distutils.core.setup(
    ext_modules = Cython.Build.cythonize("fdmt_homebrew_copy.pyx"))