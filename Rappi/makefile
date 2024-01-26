format-everything:
	isort .
	black .

run-tests:
	coverage run -m pytest
	coverage report -m --include="code/*" --omit="*__init__.py"

pre-commit: format-everything run-tests