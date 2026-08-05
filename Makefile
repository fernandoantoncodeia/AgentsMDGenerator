.PHONY: install serve status list

install:
	python3 -m pip install -e .

serve:
	bin/agentsmd-serve

status:
	python3 -m agentsmd.cli status

list:
	python3 -m agentsmd.cli list
