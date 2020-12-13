SHELL := /bin/bash
.DEFAULT_GOAL := run
.PHONY: piprequirements install run


.venv:
	python3 -m venv .venv

piprequirements: .venv
	.venv/bin/python -m pip install -r source/requirements.txt

install: piprequirements
	brew install selenium-server-standalone
	brew cask install chromedriver

run:
	killall selenium-server || true
	{ selenium-server -port 4444 & echo $$! > selenium.PID; }
	sleep 5
	source .venv/bin/activate \
		&& .venv/bin/python source/monitor.py \
		&& kill -SIGTERM `cat selenium.PID` \
		&& rm selenium.PID