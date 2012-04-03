"""Code to handle the output of SEP 0."""
import datetime
import sys
import unicodedata

from operator import attrgetter

from . import constants
from .sep import SEP, SEPError


indent = u' '

def write_column_headers(output):
    """Output the column headers for the SEP indices."""
    column_headers = {'status': u'', 'type': u'', 'number': u'num',
                        'title': u'title', 'authors': u'owner'}
    print>>output, constants.column_format % column_headers
    underline_headers = {}
    for key, value in column_headers.items():
        underline_headers[key] = unicode(len(value) * '-')
    print>>output, constants.column_format % underline_headers


def sort_seps(seps):
    """Sort SEPs into meta, informational, accepted, open, finished,
    and essentially dead."""
    meta = []
    info = []
    accepted = []
    open_ = []
    finished = []
    dead = []
    for sep in seps:
        # Order of 'if' statement important.  Key Status values take precedence
        # over Type value, and vice-versa.
        if sep.type_ == 'Process':
            meta.append(sep)
        elif sep.status == 'Draft':
            open_.append(sep)
        elif sep.status in ('Rejected', 'Withdrawn', 'Deferred',
                'Incomplete', 'Replaced'):
            dead.append(sep)
        elif sep.type_ == 'Informational':
            info.append(sep)
        elif sep.status in ('Accepted', 'Active'):
            accepted.append(sep)
        elif sep.status == 'Final':
            finished.append(sep)
        else:
            raise SEPError("unsorted (%s/%s)" %
                           (sep.type_, sep.status),
                           sep.filename, sep.number)
    return meta, info, accepted, open_, finished, dead


def verify_email_addresses(seps):
    authors_dict = {}
    for sep in seps:
        for author in sep.authors:
            # If this is the first time we have come across an author, add him.
            if author not in authors_dict:
                authors_dict[author] = [author.email]
            else:
                found_emails = authors_dict[author]
                # If no email exists for the author, use the new value.
                if not found_emails[0]:
                    authors_dict[author] = [author.email]
                # If the new email is an empty string, move on.
                elif not author.email:
                    continue
                # If the email has not been seen, add it to the list.
                elif author.email not in found_emails:
                    authors_dict[author].append(author.email)

    valid_authors_dict = {}
    too_many_emails = []
    for author, emails in authors_dict.items():
        if len(emails) > 1:
            too_many_emails.append((author.first_last, emails))
        else:
            valid_authors_dict[author] = emails[0]
    if too_many_emails:
        err_output = []
        for author, emails in too_many_emails:
            err_output.append("    %s: %r" % (author, emails))
        raise ValueError("some authors have more than one email address "
                         "listed:\n" + '\n'.join(err_output))

    return valid_authors_dict


def sort_authors(authors_dict):
    authors_list = authors_dict.keys()
    authors_list.sort(key=attrgetter('sort_by'))
    return authors_list

def normalized_last_first(name):
    return len(unicodedata.normalize('NFC', name.last_first))


def write_sep0(seps, output=sys.stdout):
    today = datetime.date.today().strftime("%Y-%m-%d")
    print>>output, constants.header % today
    print>>output
    print>>output, u"Introduction"
    print>>output, constants.intro
    print>>output
    print>>output, u"Index by Category"
    print>>output
    write_column_headers(output)
    meta, info, accepted, open_, finished, dead = sort_seps(seps)
    print>>output
    print>>output, u" Meta-SEPs (SEPs about SEPs or Processes)"
    print>>output
    for sep in meta:
        print>>output, unicode(sep)
    print>>output
    print>>output, u" Other Informational SEPs"
    print>>output
    for sep in info:
        print>>output, unicode(sep)
    print>>output
    print>>output, u" Accepted SEPs (accepted; may not be implemented yet)"
    print>>output
    for sep in accepted:
        print>>output, unicode(sep)
    print>>output
    print>>output, u" Open SEPs (under consideration)"
    print>>output
    for sep in open_:
        print>>output, unicode(sep)
    print>>output
    print>>output, u" Finished SEPs (done, implemented in code sepository)"
    print>>output
    for sep in finished:
        print>>output, unicode(sep)
    print>>output
    print>>output, u" Deferred, Abandoned, Withdrawn, and Rejected SEPs"
    print>>output
    for sep in dead:
        print>>output, unicode(sep)
    print>>output
    print>>output
    print>>output, u" Numerical Index"
    print>>output
    write_column_headers(output)
    prev_sep = 0
    for sep in seps:
        if sep.number - prev_sep > 1:
            print>>output
        print>>output, unicode(sep)
        prev_sep = sep.number
    print>>output
    print>>output
    print>>output, u"Key"
    print>>output
    for type_ in SEP.type_values:
        print>>output, u"    %s - %s SEP" % (type_[0], type_)
    print>>output
    for status in SEP.status_values:
        print>>output, u"    %s - %s proposal" % (status[0], status)

    print>>output
    print>>output
    print>>output, u"Owners"
    print>>output
    authors_dict = verify_email_addresses(seps)
    max_name = max(authors_dict.keys(), key=normalized_last_first)
    max_name_len = len(max_name.last_first)
    print>>output, u"    %s  %s" % ('name'.ljust(max_name_len), 'email address')
    print>>output, u"    %s  %s" % ((len('name')*'-').ljust(max_name_len),
                                    len('email address')*'-')
    sorted_authors = sort_authors(authors_dict)
    for author in sorted_authors:
        # Use the email from authors_dict instead of the one from 'author' as
        # the author instance may have an empty email.
        print>>output, (u"    %s  %s" %
                (author.last_first.ljust(max_name_len), authors_dict[author]))
    print>>output
    print>>output
    print>>output, u"References"
    print>>output
    print>>output, constants.references
    print>>output, constants.footer
