# Rules to only make the required HTML versions, not all of them,
# without the user having to keep track of which.
#
# Not really important, but convenient.

SEP2HTML=sep2html.py

PYTHON=python

.SUFFIXES: .txt .html

.txt.html:
	@$(PYTHON) $(SEP2HTML) $<

SEPS=$(filter-out sep-0000.txt,$(wildcard sep-????.txt))

TARGETS=$(SEPS:.txt=.html) sep-0000.html

all: sep-0000.txt $(TARGETS)

$(TARGETS) sep-0000.html1: sep2html.py

sep-0000.txt: $(SEPS)
	$(PYTHON) gensepindex.py .

install:
	echo "Installing is not necessary anymore. It will be done in post-commit."

clean:
	-rm *.html
	-rm sep-0000.txt
	-rm *.pyc

update:
	svn update

propcheck:
	$(PYTHON) propcheck.py
