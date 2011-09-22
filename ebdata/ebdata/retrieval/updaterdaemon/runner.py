#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebdata
#
#   ebdata is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebdata is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebdata.  If not, see <http://www.gnu.org/licenses/>.
#

from ebdata.utils.daemon import Daemon
import datetime
import os
import sys
import time

class EveryMinuteDaemon(Daemon):
    """
    A daemon that calls handle_time() every minute.
    """
    def run(self):
        while 1:
            # Calculate the next minute. We don't care about handling the
            # current minute, because if we did that, it would be handled
            # twice if this program were stopped and restarted during that
            # minute.
            next_minute = datetime.datetime.now() + datetime.timedelta(minutes=1)
            next_minute = next_minute.replace(second=0, microsecond=0)

            # Sleep until the next minute. Add 5 seconds to the sleep time to
            # avoid edge cases and off-by-one errors. Messy but effective.
            sleep_delta = next_minute - datetime.datetime.now()
            time.sleep(sleep_delta.seconds + 5)

            # Call the hook.
            self.handle_time(next_minute)

    def handle_time(self, timestamp):
        pass

class EveryTwoSecondsDaemon(Daemon):
    """
    A daemon that calls handle_time() every two seconds.

    This is useful for debugging -- just replace EveryMinuteDaemon with
    EveryTwoSecondsDaemon in your subclass.
    """
    def run(self):
        while 1:
            self.handle_time(datetime.datetime.now())
            time.sleep(2)

    def handle_time(self, timestamp):
        pass

class UpdaterDaemon(EveryMinuteDaemon):
    """
    A (deprecated) daemon for running OpenBlock scrapers based on a config file.

    We now recommend just using cron or your preferred scheduling tool instead.
    """

    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn("UpdaterDaemon is deprecated, see http://openblockproject.org/docs/main/running_scrapers.html",
                      DeprecationWarning)

        super(UpdaterDaemon, self).__init__(*args, **kwargs)
        self.parser.add_option("-c", "--config",
                               help="path to configuration file (python).",
                               action="store", default=None)
        self.parser.add_option("--error-log",
                               help="path to error log.",
                               action="store", default="/tmp/updaterdaemon.log")
        self.parser.add_option("--log-file",
                               help="path to log file.",
                               action="store", default="/tmp/updaterdaemon.err")

    def parse_args(self, argv):
        """Given sys.argv, parses the command-line arguments.
        """
        super(UpdaterDaemon, self).parse_args(argv)

        self.stdout = self.options.log_file
        self.stderr = self.options.error_log

        config = self.options.config
        if config is None:
            config = os.path.join(os.path.dirname(__file__), 'config.py')
        config = os.path.normpath(os.path.abspath(config))
        configdir, configfile = os.path.split(config)
        configfile, ext = os.path.splitext(configfile)
        if configdir not in sys.path:
            sys.path.insert(0, configdir)
        self.config = __import__(configfile)

    def handle_time(self, timestamp):
        # Get the tasks for the given timestamp, and run any that need to be
        # run. Reload the config to take into account any changes that might
        # have been made.
        reload(self.config)
        for check, func, kwargs, env in self.config.TASKS:
            if check(timestamp):
                # Fork a child process and grandchild process, and kill the
                # child process immediately so that it doesn't block.
                # For more on this technique, see the final paragraph at
                # http://www.faqs.org/faqs/unix-faq/faq/part3/section-13.html
                try:
                    pid = os.fork()
                except OSError, e:
                    sys.stderr.write("fork failed: %d (%s)\n" % (e.errno, e.strerror))
                    os._exit(1)
                if pid == 0: # child
                    try:
                        pid2 = os.fork()
                    except OSError, e:
                        sys.stderr.write("inner fork failed: %d (%s)\n" % (e.errno, e.strerror))
                        os._exit(1)
                    if pid2 == 0: # child
                        os.environ.update(env)
                        # Log the function call and PID.
                        # TODO: use logging module.
                        sys.stdout.write('%s\t%s\t%r\t%s\n' % (datetime.datetime.now(), func.func_name, kwargs, os.getpid()))
                        sys.stdout.flush()

                        try:
                            func(**kwargs)
                        except Exception, e:
                            from django.core.mail import mail_admins
                            import traceback
                            traceback_string = '\n'.join(traceback.format_exception(*sys.exc_info()))
                            sys.stderr.write("ERROR AT %s\n" % datetime.datetime.now())
                            sys.stderr.write(traceback_string)
                            sys.stderr.write("\n========================================\n")
                            subject = '%s %s' % (func.func_name, str(kwargs).replace('\n', ' '))
                            try:
                                mail_admins(subject, traceback_string)
                            except Exception, e:
                                sys.stderr.write("Got error mailing admins: %s\n" % e)
                            # Don't call sys.exit() for this,
                            # because we're in a child process.
                            os._exit(1)
                        sys.stdout.flush()
                    os._exit(0)
                else: # parent
                    os.waitpid(pid, 0)

if __name__ == "__main__":
    daemon = UpdaterDaemon('/tmp/updaterdaemon.pid')
    daemon.run_from_command_line(sys.argv[1:])
