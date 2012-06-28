import setuptools


requires = [
]


setuptools.setup(
	name='mistress_stat',
	version='0.1',
	description='mistress_stat',
	author='f',
	author_email='fsfeel@gmail.com',
	url='',
	package_dir = {'': 'src'},
	packages=setuptools.find_packages("src"),
	include_package_data=True,
	zip_safe=False,
	install_requires = requires,
)
