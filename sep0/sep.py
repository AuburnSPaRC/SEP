# -*- coding: utf-8 -*-
"""Code for handling object sepresentation of a SEP."""
import re
import textwrap
import unicodedata

from email.parser import HeaderParser

from . import constants


class SEPError(Exception):

    def __init__(self, error, sep_file, sep_number=None):
        super(SEPError, self).__init__(error)
        self.filename = sep_file
        self.number = sep_number

    def __str__(self):
        error_msg = super(SEPError, self).__str__()
        if self.number is not None:
            return "SEP %d: %r" % (self.number, error_msg)
        else:
            return "(%s): %r" % (self.filename, error_msg)


class SEPParseError(SEPError):

    pass


class Author(object):

    """Represent SEP authors.

    Attributes:

        + first_last : str
            The author's full name.

        + last_first : str
            Output the author's name in Last, First, Suffix order.

        + first : str
            The author's first name.  A middle initial may be included.

        + last : str
            The author's last name.

        + suffix : str
            A person's suffix (can be the empty string).

        + sort_by : str
            Modification of the author's last name that should be used for
            sorting.

        + email : str
            The author's email address.
    """

    def __init__(self, author_and_email_tuple):
        """Parse the name and email address of an author."""
        name, email = author_and_email_tuple
        self.first_last = name.strip()
        self.email = email.lower()
        last_name_fragment, suffix = self._last_name(name)
        name_sep = name.index(last_name_fragment)
        self.first = name[:name_sep].rstrip()
        self.last = last_name_fragment
        self.suffix = suffix
        if not self.first:
            self.last_first = self.last
        else:
            self.last_first = u', '.join([self.last, self.first])
            if self.suffix:
                self.last_first += u', ' + self.suffix
        self.nick = self.last

    def __hash__(self):
        return hash(self.first_last)

    def __eq__(self, other):
        return self.first_last == other.first_last

    @property
    def sort_by(self):
        name_parts = self.last.split()
        for index, part in enumerate(name_parts):
            if part[0].isupper():
                break
        else:
            raise ValueError("last name missing a capital letter: %r"
	                                                       % name_parts)
        base = u' '.join(name_parts[index:]).lower()
        return unicodedata.normalize('NFKD', base).encode('ASCII', 'ignore')

    def _last_name(self, full_name):
        """Find the last name (or nickname) of a full name.

        If no last name (e.g, 'Aahz') then return the full name.  If there is
        a leading, lowercase portion to the last name (e.g., 'van' or 'von')
        then include it.  If there is a suffix (e.g., 'Jr.') that is appended
        through a comma, then drop the suffix.

        """
        name_partition = full_name.partition(u',')
        no_suffix = name_partition[0].strip()
        suffix = name_partition[2].strip()
        name_parts = no_suffix.split()
        part_count = len(name_parts)
        if part_count == 1 or part_count == 2:
            return name_parts[-1], suffix
        else:
            assert part_count > 2
            if name_parts[-2].islower():
                return u' '.join(name_parts[-2:]), suffix
            else:
                return name_parts[-1], suffix


class SEP(object):

    """Representation of SEPs.

    Attributes:

        + number : int
            SEP number.

        + title : str
            SEP title.

        + type_ : str
            The type of SEP.  Can only be one of the values from
            SEP.type_values.

        + status : str
            The SEP's status.  Value must be found in SEP.status_values.

        + authors : Sequence(Author)
            A list of the authors.
    """

    # The various RFC 822 headers that are supported.
    # The second item in the nested tuples sepresents if the header is
    # required or not.
    headers = (('SEP', True), ('Title', True), ('Version', True),
               ('Last-Modified', True), ('Author', True),
               ('Discussions-To', False), ('Status', True), ('Type', True),
               ('Content-Type', False), ('Requires', False),
               ('Created', True), ('ROS-Version', False),
               ('Post-History', False), ('Replaces', False),
               ('Replaced-By', False), ('Resolution', False),
               )
    # Valid values for the Type header.
    type_values = (u"Rules", u"Informational", u"Process")
    # Valid values for the Status header.
    # Active SEPs can only be for Informational or Process SEPs.
    status_values = (u"Accepted", u"Rejected", u"Withdrawn", u"Deferred",
                     u"Final", u"Active", u"Draft", u"Replaced")

    def __init__(self, sep_file):
        """Init object from an open SEP file object."""
        # Parse the headers.
        self.filename = sep_file
        sep_parser = HeaderParser()
        metadata = sep_parser.parse(sep_file)
        header_order = iter(self.headers)
        try:
            for header_name in metadata.keys():
                current_header, required = header_order.next()
                while header_name != current_header and not required:
                    current_header, required = header_order.next()
                if header_name != current_header:
                    raise SEPError("did not deal with "
                                   "%r before having to handle %r" %
                                   (header_name, current_header),
                                   sep_file.name)
        except StopIteration:
            raise SEPError("headers missing or out of order",
                                sep_file.name)
        required = False
        try:
            while not required:
                current_header, required = header_order.next()
            else:
                raise SEPError("SEP is missing its %r" % (current_header,),
                               sep_file.name)
        except StopIteration:
            pass
        # 'SEP'.
        try:
            self.number = int(metadata['SEP'])
        except ValueError:
            raise SEPParseError("SEP number isn't an integer", sep_file.name)
        # 'Title'.
        self.title = metadata['Title']
        # 'Type'.
        type_ = metadata['Type']
        if type_ not in self.type_values:
            raise SEPError('%r is not a valid Type value' % (type_,),
                           sep_file.name, self.number)
        self.type_ = type_
        # 'Status'.
        status = metadata['Status']
        if status not in self.status_values:
            raise SEPError("%r is not a valid Status value" %
                           (status,), sep_file.name, self.number)
        # Special case for Active SEPs.
        if (status == u"Active" and
                self.type_ not in ("Process", "Informational")):
            raise SEPError("Only Process and Informational SEPs may "
                           "have an Active status", sep_file.name,
                           self.number)
        self.status = status
        # 'Author'.
        authors_and_emails = self._parse_author(metadata['Author'])
        if len(authors_and_emails) < 1:
            raise SEPError("no authors found", sep_file.name,
                           self.number)
        self.authors = map(Author, authors_and_emails)

    def _parse_author(self, data):
        """Return a list of author names and emails."""
        # XXX Consider using email.utils.parseaddr (doesn't work with names
        # lacking an email address.
        angled = ur'(?P<author>.+?) <(?P<email>.+?)>'
        paren = ur'(?P<email>.+?) \((?P<author>.+?)\)'
        simple = ur'(?P<author>[^,]+)'
        author_list = []
        for regex in (angled, paren, simple):
            # Watch out for commas separating multiple names.
            regex += u'(,\s*)?'
            for match in re.finditer(regex, data):
                # Watch out for suffixes like 'Jr.' when they are comma-separated
                # from the name and thus cause issues when *all* names are only
                # separated by commas.
                match_dict = match.groupdict()
                author = match_dict['author']
                if not author.partition(' ')[1] and author.endswith('.'):
                    prev_author = author_list.pop()
                    author = ', '.join([prev_author, author])
                if u'email' not in match_dict:
                    email = ''
                else:
                    email = match_dict['email']
                author_list.append((author, email))
            else:
                # If authors were found then stop searching as only expect one
                # style of author citation.
                if author_list:
                    break
        return author_list

    @property
    def type_abbr(self):
        """Return the how the type is to be sepresented in the index."""
        return self.type_[0].upper()

    @property
    def status_abbr(self):
        """Return how the status should be sepresented in the index."""
        if self.status in ('Draft', 'Active'):
            return u' '
        else:
            return self.status[0].upper()

    @property
    def author_abbr(self):
        """Return the author list as a comma-separated with only last names."""
        return u', '.join(x.nick for x in self.authors)

    @property
    def title_abbr(self):
        """Shorten the title to be no longer than the max title length."""
        if len(self.title) <= constants.title_length:
            return self.title
        wrapped_title = textwrap.wrap(self.title, constants.title_length - 4)
        return wrapped_title[0] + u' ...'

    def __unicode__(self):
        """Return the line entry for the SEP."""
        sep_info = {'type': self.type_abbr, 'number': str(self.number),
                'title': self.title_abbr, 'status': self.status_abbr,
                'authors': self.author_abbr}
        return constants.column_format % sep_info
