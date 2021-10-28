PYTHON_CMD ?= python
PIP_CMD ?= pip
AIOBFD_VERSION ?= "0.2"
EL_PACKAGE_ITERATION ?= 1.el
EL_VERSION_ID ?= 7

init_pip:
	@echo "Target init_pip"
	$(PIP_CMD) show -q poetry || $(PIP_CMD) install poetry
	poetry install
	poetry version --no-ansi
	poetry update --dry-run
	touch init_pip

init_pipx:
	@echo "Target init_pipx"
	$(PIP_CMD) show -q pipx || $(PIP_CMD) install pipx
	$(PYTHON_CMD) -m pipx ensurepath
	pipx runpip poetry show -q poetry || pipx install poetry
	poetry install
	poetry version --no-ansi
	poetry update --dry-run
	touch init_pipx

fmt:
	@echo "Target fmt"
	poetry run black aiobfd tests

build:
	@echo "Building aiobfd"
	@poetry build -f wheel

binary: build
	poetry run pyinstaller --runtime-tmpdir /var/lib/aiobfd --distpath dist/usr/bin --clean --onefile --name aiobfd aiobfd/__main__.py
	rm -f dist/*.whl

package-rpm: binary
	mkdir -p dist/var/lib/aiobfd
	cd dist; fpm \
		--input-type dir \
		--output-type rpm \
		--version $(AIOBFD_VERSION) \
		--iteration $(EL_PACKAGE_ITERATION)$(EL_VERSION_ID) \
		--prefix / \
		--name aiobfd \
        --description "Asynchronous BFD Daemon" \
		--rpm-user root \
		.

clean:
	git clean -fdx