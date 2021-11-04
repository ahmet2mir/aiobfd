PYTHON_CMD ?= python
PIP_CMD ?= pip

init_pip:
	@echo "Target init_pip"
	$(PIP_CMD) show -q poetry || $(PIP_CMD) install poetry
	$(PIP_CMD) show -q poetry-dynamic-versioning || $(PIP_CMD) install poetry-dynamic-versioning
	poetry install
	poetry version --no-ansi
	poetry update --dry-run
	touch init_pip

init_pipx:
	@echo "Target init_pipx"
	$(PIP_CMD) show -q pipx || $(PIP_CMD) install pipx
	$(PYTHON_CMD) -m pipx ensurepath
	pipx runpip poetry show -q poetry || pipx install poetry
	pipx runpip poetry show -q poetry-dynamic-versioning || pipx inject poetry poetry-dynamic-versioning
	poetry install
	poetry version --no-ansi
	poetry update --dry-run
	touch init_pipx

fmt:
	@echo "Target fmt"
	poetry run black aiobfd tests

build:
	@echo "Building aiobfd"
	poetry build -f wheel

binary: build
	@echo "Building binary"
	mkdir -p artifacts/binaries
	cp README.md LICENSE artifacts/binaries
	poetry run pyinstaller --distpath artifacts/binaries --clean --onefile --name aiobfd aiobfd/__main__.py

archive-linux: binary
	@echo "Target archive-linux"
	mkdir -p artifacts/archives
	tar cfz artifacts/archives/aiobfd-$(shell poetry version --no-ansi --short)-linux-x86_64.tar.gz -C artifacts/binaries aiobfd README.md LICENSE
	sha256sum artifacts/archives/aiobfd-$(shell poetry version --no-ansi --short)-linux-x86_64.tar.gz >> artifacts/checksums.txt

clean:
	git clean -fdx
