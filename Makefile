ENV=env
PYTHON=$(ENV)/bin/python
PIP=$(ENV)/bin/pip

GREEN=\033[0;32m
RED=\033[0;31m
COLOR_OFF=\033[0m

all: 
	$(PYTHON) openclass.py

# save external libs in requirements.txt
saveLibs: mkEnv
	@echo -e "$(GREEN)Saving libs to requirements.txt$(COLOR_OFF)"
	@./$(PIP) -q freeze > requirements.txt
	@echo -e "$(GREEN)Done$(COLOR_OFF)"

# load external libs
loadLibs: mkEnv
	@echo -e "$(GREEN)Loading libs from requirements.txt$(COLOR_OFF)"
	@./$(PIP) -q install -r requirements.txt
	@echo -e "$(GREEN)Done$(COLOR_OFF)"

# creates python envirmoent
mkEnv:
	@if [ command -v virtualenv >/dev/null 2>&1 ] ; \
	then \
		echo -e "$(RED)virtualenv needs to be installed$(COLOR_OFF)"; \
	else \
		if [ ! -d $(ENV) ] ; \
		then \
			echo -e "$(GREEN)Creating $(ENV)$(COLOR_OFF)"; \
			virtualenv -q --python=python3.6 $(ENV); \
			echo -e "$(GREEN)Done$(COLOR_OFF)"; \
		else \
			echo -e "$(GREEN)$(ENV) already exists$(COLOR_OFF)"; \
		fi; \
	fi; \


clean:
	@echo -e "$(GREEN)Cleaning......$(COLOR_OFF)"
	@rm -rf $(OUTPUT)
	@echo -e "$(GREEN)Done$(COLOR_OFF)"

cleanEnv:
	@echo -e "$(GREEN)Cleaning $(ENV)......$(COLOR_OFF)"
	@rm -rf $(ENV)
	@echo -e "$(GREEN)Done$(COLOR_OFF)"

cleanAll: clean cleanEnv