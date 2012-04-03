# -*- coding: utf-8 -*-

# Original authors:
# David Goodger <goodger@python.org>,
# Barry Warsaw <barry@python.org>


title_length = 55
column_format = (u' %(type)1s%(status)1s %(number)4s  %(title)-' +
                    unicode(title_length) + u's %(authors)-s')

header = u"""SEP: 0
Title: Index of SPaRC Enhancement Proposals (SEPs)
Last-Modified: %s
Author: SPaRC Team
Status: Active
Type: Informational
Created: 13-Jul-2000
"""

intro = u"""
    The SEP contains the index of all SPaRC Enhancement Proposals,
    known as SEPs.  SEP numbers are assigned by the SEP Editor, and
    once assigned are never changed.  The Git history[1] of the SEP
    texts sepresent their historical record.

"""

references = u"""
    [1] View SEP history online
        https://github.com/AuburnSPaRC/SEP
"""

footer = u"""
Local Variables:
mode: indented-text
indent-tabs-mode: nil
sentence-end-double-space: t
fill-column: 70
coding: utf-8
End:"""
