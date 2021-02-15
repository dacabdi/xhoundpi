init:
	PIPENV_VENV_IN_PROJECT=1
    pipenv install --three
test:
    py.test tests
.PHONY: init test