================
Running Scrapers
================

Once you've written your :doc:`scraper scripts <scraper_tutorial>`,
you'll need to re-run them frequently to keep the news on your site up
to date.

You can do this any way you like; `cron
<http://en.wikipedia.org/wiki/Cron>`_ would work fine.
But there is a daemon that comes with OpenBlock which is tailor-made
for this purpose.

Updaterdaemon Configuration
===========================

The daemon script is named ``runner.py`` and it lives in
:doc:`packages/ebdata`, more specifically at ``ebdata/retrieval/updaterdaemon/runner.py``.  To configure it, you need to write a (small)
Python script that contains a list of ``TASKS``.

There is an example config file at
``ebdata/retrieval/updaterdaemon/config.py``,
and the one we use for :doc:`packages/obdemo` is at ``obdemo/sample_scraper_config.py``.

What goes in the config file? Let's put together a (small) example based on
the one for obdemo.

First, we need a function that imports and runs one of our scrapers,
just once.  Let's use the one from ``obdemo`` that creates
"Events". Our function can look like::

  def do_events():
      from obdemo.scrapers.add_events import main
      return main()

(Note that this function could do anything we want to run
periodically; updaterdaemon actually doesn't know anything about
scrapers per se. One other thing you probably want to do regularly is
send out openblock's :ref:`email_alerts`.)

Next, we need a way to know when, or how often, that function should
run.  We'll use another function for that; let's call it a "time
callback". The time callback takes one argument - a Python `datetime
<http://docs.python.org/library/datetime.html#datetime-objects>`_ -
and returns ``True`` if we should run our scraper now, and ``False`` otherwise.
Here's one that runs every ten minutes::

  def every_ten_minutes(datetime):
      if datetime.minute % 10 == 0:
          return True
      return False

(Note that runner.py only wakes up and checks the time once per
minute, so we don't need to be very careful here about the time
check - we won't accidentally run this many times in one minute.)

(Note also that the example config file in
``ebdata/retrieval/updaterdaemon/config.py`` already contains
factories to generate a number of useful time callbacks, such as
``multiple_daily``, ``daily,`` and ``weekly``. We could just import
and call one of those. Read the source to see how they work.)

Finally, we need to wrap all this up in a list (or tuple) calles
``TASKS``. This is what the runner.py script looks for in the config
file.  ``TASKS`` is a list of tuples, each in the form
``(time_callback, function_to_run, {keyword args}, {environ})``.

We've already got the first two of those. What about the last two?
``keyword args`` is a dictionary of extra arguments to pass to our
function.  Ours doesn't actually need any, so we'll use an empty
dictionary, like ``{}``.

``environ`` is a dictionary of environment variables to set before
running our function.  Generally this will need to set
``DJANGO_SETTINGS_MODULE``.  For the demo, we set it to
``obdemo.settings`` by default, unless there is already an environment
variable by that name.  This looks like::

  env = {'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'obdemo.settings')}




Putting it all together, we get this complete config file::

  from ebdata.retrieval.updaterdaemon.config import multiple_hourly

  def do_events():
      from obdemo.scrapers.add_events import main
      return main()

  def every_ten_minutes(datetime):
      if datetime.minute % 10 == 0:
          return True
      return False

  env = {'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'obdemo.settings')}

  TASKS = (
      (every_ten_minutes, do_events, {}, env),
  )



Testing the daemon
===================

Give it a try::

  python ebdata/ebdata/retrieval/updaterdaemon/runner.py --config=/path/to/config.py  start

If it works, nothing obvious should happen :) It's running in the
background.  You shouldn't expect anything to happen until the next
multiple of 10 minutes.  When it's time, check the log file to see if
anything's happening::

  tail -f /tmp/updaterdaemon.log

(Hit Ctrl-C to get out of that.)


If there's nothing in the main log, check the error log::

  less /tmp/updaterdaemon.err

To stop the daemon, do this::

  python ebdata/ebdata/retrieval/updaterdaemon/runner.py stop


Installing the init script
==========================

UpdaterDaemon also comes with a script suitable for putting in
``/etc/init.d``, so it will be restarted whenever the system is
rebooted. To install this script, copy it from
``ebdata/retrieval/updaterdaemon/initscript`` into something like
``/etc/init.d/openblock-updaterdaemon``.  It is known to work on
Ubuntu; let us know if you have trouble with it on other linux
systems.

After copying, edit the script, setting a few crucial environment variables:

``HERE`` should point to the virtualenv where you installed OpenBlock.

``CONFIG`` should point to a config file as described in the previous
sections.

``SU_USER`` should be the name of the user account to use for running
the daemon.

You might also want to set ``LOGFILE`` and ``ERRLOGFILE`` to control
where the logs go.

Now try running the script as root::

  sudo /etc/init.d/openblock-updaterdaemon start

Check the log files to make sure it's working.

