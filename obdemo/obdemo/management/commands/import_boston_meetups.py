#   Copyright 2011 OpenPlans and contributors
#
#   This file is part of OpenBlock
#
#   OpenBlock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OpenBlock is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OpenBlock.  If not, see <http://www.gnu.org/licenses/>.
#


from django.core.management.base import BaseCommand
from ebdata.scrapers.general.meetup.meetup_retrieval import MeetupScraper, parser
from optparse import OptionParser


class Command(BaseCommand):
    help = 'Import Boston meetups.'
    option_list = BaseCommand.option_list + tuple(parser.option_list)

    def handle(self, *args, **options):
        # We get passed options as a dict, but need them as attrs. Sigh.
        class Bag(object):
            pass
        opts = Bag()
        for k, v in options.items():
            setattr(opts, k, v)
        scraper = MeetupScraper(opts)
        scraper.update()

    def create_parser(self, prog_name, subcommand):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.

        Overridden to add conflict_handler='resolve'
        """
        return OptionParser(prog=prog_name,
                            usage=self.usage(subcommand),
                            version=self.get_version(),
                            conflict_handler="resolve",
                            option_list=self.option_list)
