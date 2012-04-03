# $Id: __init__.py 6328 2010-05-23 21:20:29Z gbrandl $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
SEP HTML Writer.
"""

__docformat__ = 'reStructuredText'


import sys
import os
import os.path
import codecs
import docutils
from docutils import frontend, nodes, utils, writers
from docutils.writers import html4css1


class Writer(html4css1.Writer):

    default_stylesheet = 'sep.css'

    default_stylesheet_path = utils.relative_path(
        os.path.join(os.getcwd(), 'dummy'),
        os.path.join(os.path.dirname(__file__), default_stylesheet))

    default_template = 'template.txt'

    default_template_path = utils.relative_path(
        os.path.join(os.getcwd(), 'dummy'),
        os.path.join(os.path.dirname(__file__), default_template))

    settings_spec = html4css1.Writer.settings_spec + (
        'SEP/HTML-Specific Options',
        'For the SEP/HTML writer, the default value for the --stylesheet-path '
        'option is "%s", and the default value for --template is "%s". '
        'See HTML-Specific Options above.'
        % (default_stylesheet_path, default_template_path),
        (('ROS\'s home URL.  Default is "http://ros.org".',
          ['--ros-home'],
          {'default': 'http://ros.org', 'metavar': '<URL>'}),
         ('Home URL prefix for SEPs.  Default is "." (current directory).',
          ['--sep-home'],
          {'default': '.', 'metavar': '<URL>'}),
         # For testing.
         (frontend.SUPPRESS_HELP,
          ['--no-random'],
          {'action': 'store_true', 'validator': frontend.validate_boolean}),))

    settings_default_overrides = {'stylesheet_path': default_stylesheet_path,
                                  'template': default_template_path,}

    relative_path_settings = (html4css1.Writer.relative_path_settings
                              + ('template',))

    config_section = 'sep_html writer'
    config_section_dependencies = ('writers', 'html4css1 writer')

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator

    def interpolation_dict(self):
        subs = html4css1.Writer.interpolation_dict(self)
        settings = self.document.settings
        roshome = settings.ros_home
        subs['roshome'] = roshome
        subs['sephome'] = settings.sep_home
        if roshome == '..':
            subs['sepindex'] = '.'
        else:
            subs['sepindex'] = roshome + '/seps/sep-0000.html'
        index = self.document.first_child_matching_class(nodes.field_list)
        header = self.document[index]
        self.sepnum = header[0][1].astext()
        subs['sep'] = self.sepnum
        if settings.no_random:
            subs['banner'] = 0
        else:
            import random
            subs['banner'] = random.randrange(64)
        try:
            subs['sepnum'] = '%04i' % int(self.sepnum)
        except ValueError:
            subs['sepnum'] = self.sepnum
        self.title = header[1][1].astext()
        subs['title'] = self.title
        subs['body'] = ''.join(
            self.body_pre_docinfo + self.docinfo + self.body)
        return subs

    def assemble_parts(self):
        html4css1.Writer.assemble_parts(self)
        self.parts['title'] = [self.title]
        self.parts['sepnum'] = self.sepnum


class HTMLTranslator(html4css1.HTMLTranslator):

    def depart_field_list(self, node):
        html4css1.HTMLTranslator.depart_field_list(self, node)
        if 'rfc2822' in node['classes']:
             self.body.append('<hr />\n')
