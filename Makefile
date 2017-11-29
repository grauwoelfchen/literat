ifeq (, $(ENV))
	env := development
else ifeq (test, $(ENV))
	env := testing
else
	env := $(ENV)
endif

package = literat

setup:
	pip install -e '.[${env}]' -c constraints.txt
.PHONY: setup

clean:
	find . ! -readable -prune -o -print \
	  ! -path "./.git/*" ! -path "./venv*" \
	  ! -path "./doc/*" | \
	  grep -E "(__pycache__|\.egg-info|\.pyc|\.pyo)" | \
	  xargs rm -rf
.PHONY: clean

check:
	flake8
.PHONY: check

lint:
	pylint ${package}
.PHONY: lint

vet: | check lint
.PHONY: vet


.DEFAULT_GOAL = check
default: check
