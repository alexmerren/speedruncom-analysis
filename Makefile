PYTHON := python3
JQ := jq
GIT := git

DATA_DIR := $(CURDIR)/data

## saveoutput: Save the output of our main.py into a prettified json file.
.PHONY: saveoutput
saveoutput:
	@test $(filename) 
	$(PYTHON) main.py | $(JQ) '.' >> $(DATA_DIR)/$(filename)


## srcomapi: Download and extract the srcomapi if needed.
.PHONY: srcomapi
srcomapi:
	@$(GIT) clone git@github.com:blha303/srcomapi.git
