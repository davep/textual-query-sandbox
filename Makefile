###############################################################################
# Common make values.
lib    := textual_query_sandbox
run    := pipenv run
python := $(run) python
lint   := $(run) pylint
mypy   := $(run) mypy
build  := $(python) -m build
twine  := $(run) twine
black  := $(run) black

##############################################################################
# Run the application.
.PHONY: run
run:
	$(python) -m $(lib)

.PHONY: debug
debug:
	TEXTUAL=devtools make

.PHONY: console
console:
	$(run) textual console

##############################################################################
# Setup/update packages the system requires.
.PHONY: setup
setup:				# Install all dependencies
	pipenv sync --dev
	$(run) pre-commit install

.PHONY: resetup
resetup:			# Recreate the virtual environment from scratch
	rm -rf $(shell pipenv --venv)
	pipenv sync --dev

.PHONY: depsoutdated
depsoutdated:			# Show a list of outdated dependencies
	pipenv update --outdated

.PHONY: depsupdate
depsupdate:			# Update all dependencies
	pipenv update --dev

.PHONY: depsshow
depsshow:			# Show the dependency graph
	pipenv graph

##############################################################################
# Checking/testing/linting/etc.
.PHONY: lint
lint:				# Run Pylint over the library
	$(lint) $(lib)

.PHONY: typecheck
typecheck:			# Perform static type checks with mypy
	$(mypy) --scripts-are-modules $(lib)

.PHONY: stricttypecheck
stricttypecheck:	        # Perform a strict static type checks with mypy
	$(mypy) --scripts-are-modules --strict $(lib)

.PHONY: checkall
checkall: lint stricttypecheck # Check all the things

##############################################################################
# Package/publish.
.PHONY: package
package:			# Package the library
	$(build) -w

.PHONY: spackage
spackage:			# Create a source package for the library
	$(build) -s

.PHONY: packagecheck
packagecheck: package spackage	# Check the packaging.
	$(twine) check dist/*

.PHONY: testdist
testdist: packagecheck		# Perform a test distribution
	$(twine) upload --skip-existing --repository testpypi dist/*

.PHONY: dist
dist: packagecheck		# Upload to pypi
	$(twine) upload --skip-existing dist/*

##############################################################################
# Utility.
.PHONY: ugly
ugly:				# Reformat the code with black.
	$(black) $(lib)

.PHONY: repl
repl:				# Start a Python REPL
	$(python)

.PHONY: clean
clean:				# Clean the build directories
	rm -rf build dist $(lib).egg-info

.PHONY: help
help:				# Display this help
	@grep -Eh "^[a-z]+:.+# " $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.+# "}; {printf "%-20s %s\n", $$1, $$2}'

##############################################################################
# Housekeeping tasks.
.PHONY: housekeeping
housekeeping:			# Perform some git housekeeping
	git fsck
	git gc --aggressive
	git remote update --prune

### Makefile ends here
