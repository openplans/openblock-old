================
Sending Alerts
================

OpenBlock users can subscribe to email alerts from any location
they're interested in.

In order to support this feature, there is a script that needs to be
called regularly. You can do this any way you like; `cron
<http://en.wikipedia.org/wiki/Cron>`__ would work fine.

Here's an example crontab file that sends the daily alerts once a day,
and the weekly alerts once a week. Adjust the environment variables as
needed::

  DJANGO_SETTINGS_MODULE=obdemo.settings
  VIRTUAL_ENV=/path/to/my/environment
  @daily $VIRTUAL_ENV/bin/send_alerts  --frequency daily
  @weekly $VIRTUAL_ENV/bin/send_alerts --frequency weekly


Alerts get sent for 24-hour periods *starting and ending at
midnight*.  Running the daily alerts will send all news from the
start to the end of yesterday.  Weekly alerts will send all news for
the 168 hours ending at midnight last night.  It won't send any alerts
about news added on the same day that you run the script.

Note that OpenBlock does not remember which alerts have already been
sent, so you *should not* send daily alerts more than once a day,
or weekly alerts more than once a week --
or your users will get duplicate alert messages.



Disabling Alerts
-----------------

Disabling Email Alerts entirely is easy. In your ``settings.py``,
just remove ``"ebpub.alerts"`` from ``settings.INSTALLED_APPS``.
(You can copy the setting from ``ebpub/default_settings.py`` and
modify it.)  This will remove the alerts sign-up links from all
OpenBlock pages.
