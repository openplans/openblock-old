#   Copyright 2007,2008,2009 Everyblock LLC
#
#   This file is part of ebwiki
#
#   ebwiki is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebwiki is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebwiki.  If not, see <http://www.gnu.org/licenses/>.
#

from django.db import models
import re

class PageManager(models.Manager):
    def create_with_auto_version(self, slug, headline, content, change_message, change_user, change_ip, minor_edit):
        """
        Creates and returns a Page object with the given attributes.
        Automatically sets version to the next available version number for
        the given slug, in a way that avoids race conditions.
        """
        from django.db import connection
        db_table = self.model._meta.db_table
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO %s
                (slug, headline, content, version, change_date, change_message, change_user, change_ip, minor_edit)
            VALUES
                (%%s, %%s, %%s, (SELECT COALESCE(MAX(version), 0) + 1 FROM %s WHERE slug=%%s), NOW(), %%s, %%s, %%s, %%s)""" %\
            (db_table, db_table),
            (slug, headline, content, slug, change_message, change_user, change_ip, minor_edit))
        new_id = connection.ops.last_insert_id(cursor, db_table, 'id')
        connection._commit()
        return self.get(id=new_id)

    def select_all_latest(self):
        """
        Returns a QuerySet of the most recent version of each Page.
        """
        from django.db import connection
        db_table = self.model._meta.db_table
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT ON (slug) ID FROM %s ORDER BY slug, version DESC" % db_table)
        return self.filter(id__in=cursor.fetchall())

    def find_orphans(self):
        """
        Returns a list of Pages which aren't linked to by any other Page.
        """
        link_re = re.compile(r'''(?x)
            (?<=\]\() # A link starts with an open paren immediately after a close square bracket
            [^)]+     # Match everything up to the close paren
            (?=\))    # Sanity check: look ahead for the close paren
        ''')
        pages = self.select_all_latest()
        orphans = dict([(p.slug, p) for p in pages])
        for page in pages:
            for slug in link_re.findall(page.content):
                if not slug.startswith("http://"):
                    try:
                        del orphans[slug]
                    except KeyError:
                        pass
        return orphans.values()

class Page(models.Model):
    slug = models.CharField(max_length=30)
    headline = models.CharField(max_length=80)
    content = models.TextField()
    version = models.PositiveIntegerField()
    change_date = models.DateTimeField()
    change_message = models.CharField(max_length=100)
    change_user = models.CharField(max_length=64)
    change_ip = models.IPAddressField()
    minor_edit = models.BooleanField()
    objects = PageManager()

    class Meta:
        unique_together = (('slug', 'version'),)

    def __unicode__(self):
        return self.slug

    def url(self):
        return '/%s/' % self.slug

    def edit_url(self):
        return '/%s/edit/' % self.slug

    def history_url(self):
        return '/%s/history/' % self.slug

    def version_url(self):
        return '/%s/history/%s/' % (self.slug, self.version)

    def diff_url(self):
        return '/%s/history/%s/diff/' % (self.slug, self.version)
