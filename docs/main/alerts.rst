================
Sending Alerts
================

OpenBlock users can subscribe to email alerts from any location
they're interested in.

In order to support this feature, there is a script that needs to be
called regularly. You can do this any way you like; `cron
<http://en.wikipedia.org/wiki/Cron>`_ would work fine.
So would :ref:`updaterdaemon <updaterdaemon>`.

Here's an example crontab file that sends the daily alerts once a day,
and the weekly alerts once a week::

  @daily /path/to/virtualenv/bin/send_alerts  --frequency daily
  @weekly /path/to/virtualenv/bin/send_alerts --frequency weekly

Note that the script does not remember which alerts have already been
sent, so you *should not* send eg. daily alerts more than once a day,
or your users will get duplicate alert messages.

Disabling Alerts
-----------------

Disabling Email Alerts entirely is easy. In your ``settings.py``,
just remove ``"ebpub.alerts"`` from ``settings.INSTALLED_APPS``.
(You can copy the setting from ``ebpub/default_settings.py`` and
modify it.)  This will remove the alerts sign-up links from all
OpenBlock pages.
