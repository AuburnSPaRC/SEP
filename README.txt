reStructuredText for SEPs
=========================

This is a direct search-and-replace port of the Python SEP
scripts at:

http://svn.python.org/projects/seps/trunk/

Original (modified) README.txt follows:

Original SEP source may be written using two standard formats, a
mildly idiomatic plaintext format and the reStructuredText format
(also, technically plaintext).  These two formats are described in SEP
9 and SEP 12 respectively.  The sep2html.py processing and
installation script knows how to produce the HTML for either SEP
format.  A local copy of the Docutils package is included for
processing reStructuredText SEPs.


Instructions for SEP Writers
============================

Check out the repository and change into the directory: ::

    git clone git@github.com:AuburnSPaRC/SEP.git
    cd SEP/

Create your new SEP, but don't assign a number (sep-xxxx.txt) ::

   touch sep-xxxx.txt
   git add sep-xxxx.txt

Write your SEP in your editor of choice.  To preview ::

   make clean
   make

When committing, only check in the txt file source of your SEP, and not the HTML,
The editors will take care of that.

    git add sep-xxxx.txt
    git commit
    git push origin master


Instructions for Generating For Release
=======================================

Check out the repository and change into the directory: ::

    git clone git@github.com:AuburnSPaRC/SEP.git
    cd SEP/

Check out the repository and change into the directory: ::

    git clone git@github.com:AuburnSPaRC/SEP.git
    cd SEP/

If this is your first time using the repository, you need to add
the git filters to your configuration (replaces the Date and Version headers)::

    cat .gitconfig >> .git/config

Check out the gh-pages branch (the release branch), and merge changes from the
master branch::

    git checkout gh-pages
    git merge origin/master

Remove the txt files, and then check them out.  This will regenerate the headers::

    rm *.txt
    git co *.txt

Generate the SEP files::

    make clean
    make
    git add *.txt
    git add *.html

And finally push to Github::

    git commit
    git push origin gh-pages
