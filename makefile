build:
	python3 -m nuitka --follow-imports --standalone --show-progress --include-data-files=$(CURDIR)/install_server.sh=install_server.sh  --include-data-files=$(CURDIR)/config.yaml=config.yaml --include-data-dir=$(CURDIR)/app/i18n=app/i18n main.py
	rm -rf main.build
	mv main.dist/main.bin main.dist/main