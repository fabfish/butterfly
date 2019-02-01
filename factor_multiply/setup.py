from setuptools import setup
from torch.utils.cpp_extension import CppExtension, BuildExtension

ext_modules = []
extension = CppExtension('factor_multiply', ['factor_multiply.cpp'], extra_compile_args=['-march=native'])
# extension = CppExtension('factor_multiply', ['factor_multiply.cpp'])
ext_modules.append(extension)

setup(
    name='extension',
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExtension})
