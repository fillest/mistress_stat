import setuptools


requires = [
	# see req.txt
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
	entry_points = """\
		[paste.app_factory]
			main = mistress_stat:main
		[console_scripts]
			migrate = sapyens.migrate:run
			create_user = mistress_stat.scripts.create_user:main
	""",
)
