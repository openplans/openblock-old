=================
Theming OpenBlock
=================

The recommended way to create a custom theme for OpenBlock
is by :doc:`../install/custom`.

.. _custom_look_feel:

Overriding Templates
====================

Note that default templates are included in ``ebpub/templates``.
At the very least,
you'll want to override ``base.html`` to design your ebpub-powered site. (The
design of EveryBlock.com is copyrighted and not free for you to use;
but the default templates, css, and images that ship with OpenBlock
and ebpub are of course free for your use under the same license terms
as the rest of OpenBlock (GPL)).

Familiarize yourself with
:py:mod:`ebpub's custom template tags <ebpub.db.templatetags>`,
there's a lot of useful features and time-savers in there.

Many parts of OpenBlock's markup can be customized on a per-schema
basis.

This is accomplished by following simple naming conventions.  In each
case described below, all you need to do is create a template, with a
filename based on the Schema's slug, in a directory whose name is
based on the view that uses the template.  Details follow.

Custom NewsItem lists
----------------------------

When NewsItems are displayed as lists, for example by the
``schema_filter`` or ``location_detail`` views, generally templates
should use the
:py:func:`newsitem_list_by_schema
<ebpub.db.templatetags.eb.do_newsitem_list_by_schema>` template tag.
Usage looks like:

.. code-block:: html+django

  {% load eb %}
  {% newsitem_list_by_schema list_of_newsitems %}

This tag takes a list of NewsItems (in
which it is assumed that the NewsItems are ordered by schema) and renders them
through separate templates, depending on the schema. These templates should be
defined in the ``templates/db/snippets/newsitem_list`` directory of
your app, and named
``[schema_slug].html``.

If no such template exists for a particular schema, the generic default is
``ebpub/templates/db/snippets/newsitem_list.html``.

We've included two sample schema-specific newsitem_list templates,
``ebpub/templates/db/snippets/newsitem_list/news-articles.html``
and
``ebpub/templates/db/snippets/newsitem_list/photos.html``.


Custom NewsItem detail pages
----------------------------

Similarly to the newsitem_list snippets, you can customize the newsitem_detail
page on a per-schema basis. Just create a subdirectory named
``templates/db/newsitem_detail`` in your app, and add a template named
``[schema_slug].html`` inside it.

If no such template exists, the default is
``ebpub/templates/db/newsitem_detail.html``.

.. _custom-map-popups:

Custom Map Popups
-----------------

To customize the html used in map popups for each
schema, create a template snippet named ``newsitem_popup_[schema_slug].html`` in a
subdirectory ``richmaps/`` on your template path.

If no such template exists, the default is
``ebpub/richmaps/templates/richmaps/newsitem_popup.html``.


Custom Schema filter pages
---------------------------

To customize the schema_filter page for a schema --
the landing page for each schema -- create a
``templates/db/schema_filter`` subdirectory in your app,
and add a template named
``[schema_slug].html`` in that directory.

If no such template exists, the default is
``ebpub/templates/db/schema_filter.html``.

Custom Schema detail pages
--------------------------

To customize the schema_detail page for a schema --
the page that normally  shows statistics about recent items of that
schema --
create a
``templates/db/schema_detail`` subdirectory in your app, and add a template named
``[schema_slug].html`` in that directory.

If no such template exists, the default is
``ebpub/templates/db/schema_detail.html``.

Custom Rich Map headlines
-------------------------

The "rich maps" view at ``/maps`` has templates specifically for the
list of news items and places to the left of the map.

For news items: Create a template at
``templates/richmaps/newsitem_headline_[schema_slug].html``.
If none exists, the default generic one is
``templates/richmaps/newsitem_headline.html``.

For places: Create a template at
``templates/richmaps/place_headline_[schema_slug].html``.
If none exists, the default generic one is
``templates/richmaps/place_headline.html``.


This page also uses the same map popup templates
described in :ref:`custom-map-popups`.




Overriding CSS and Images
=========================

TODO

Overriding Views
================

If you want to add data to a page that's not there, or otherwise
change behavior, you will probably not be able to do that by
overriding a template alone.  You will need to modify the view code,
and you will need to know at least a little about Python and Django to do this.

.. admonition:: Help! I don't know Django or Python!

  Sorry, you're going to have to learn :)  If you're starting from square one,
  `Think Python: How to Think Like a Computer Scientist
  <http://www.greenteapress.com/thinkpython/html/>`_ is a good
  Python introduction for novices, and
  `the Django Tutorial
  <https://docs.djangoproject.com/en/dev/intro/tutorial01/>`_
  is a good start for learning about Django.


View code can be overridden in the normal Django way,
by writing a function and adding an appopriate line to your
``urls.py``. Step-by-step:

1. Be sure your app is listed in ``settings.INSTALLED_APPS``.

2. Find the view you need to override. A typical way to do this is to
   find all of openblock's urls.py files and look for a URL pattern
   that matches the page in question.  To make this easier, we have
   included a command (borrowed from ``django-extensions``) to show
   all URL patterns, in the order they are searched:

   .. code-block:: bash

     django-admin.py show_urls

   This will print a bunch of lines that look like::

     /<var>/detail/<var>/	ebpub.db.views.newsitem_detail ebpub-newsitem-detail

   This shows that URLs which look roughly like "/<var>/detail/<var>/" will be
   served by the :py:func:`ebpub.db.views.newsitem_detail` view function
   from the :py:mod:`ebpub.db.views` module.
   The last part of the line is the name ``ebpub-newsitem-detail``,
   which Django may need when generating URLs.

   Once you find that out, you'll want to find which ``urls.py`` file
   sets this up, so you can copy what it does. Unfortunately the
   ``show_urls`` command doesn't tell you this, so try this unix command:

   .. code-block:: bash

      find . -name urls.py | xargs grep "ebpub-newsitem-detail"

   That will show you the file that contains the relevant code, and
   show you the code, e.g.::

      ./ebpub/ebpub/urls.py:    url(r'^([-\w]{4,32})/detail/(\d{1,8})/$', views.newsitem_detail, name='ebpub-newsitem-detail'),

3. Copy that URL pattern into your own ``urls.py`` file in your
   custom app, changing the second argument to point to your own view.
   An example ``urls.py`` file that overrides the newsitem detail view
   from the previous example might look like:

   .. code-block:: python

       from django.conf.urls.defaults import *
       
       urlpatterns = patterns(
          '',
          # My URL overrides come first.
          url(r'^([-\w]{4,32})/detail/(\d{1,8})/$', 'myapp.views.newsitem_detail',
              name='ebpub-newsitem-detail'),
          # ebpub's built-in URLs are hooked up AFTER my overrides.
          (r'^', include('ebpub.urls')),
       )

   (Change "myapp" to your custom app's name.)   See
   https://docs.djangoproject.com/en/1.3/topics/http/urls/ for more
   about Django URL configuration.

4. Now write your URL function. In your urls.py you specified
   ``myapp.views.newsitem_detail``, so first make sure your app
   has a ``views.py`` file.  Then copy the ``newsitem_detail``
   function definition from ``ebpub/db/views.py`` and paste it into
   your ``views.py`` and edit as you like.

   Before doing anything fancy, I highly recommend temporarily changing the
   view to print a simple message, just to be sure you've got all the
   above working. Something like:

   .. code-block:: python

       def newsitem_detail(request, schema_slug, newsitem_id):
           return HttpResponse("Hello there!")

   Then restart Django, reload the URL in your browser, and check if
   you see the message.  If you can't get that much working, you can
   `ask for help <https://docs.djangoproject.com/en/dev/faq/help/>`_.

.. admonition:: How to Ask for Help

   Always try to be specific: nobody can guess what exactly "it
   doesn't work" might mean.  Have patience and a thick skin -- people
   on mailing lists and IRC channels are often busy professions who
   are there in their spare time, and may at first assume you know
   more than you do, and don't have time to teach you everything.
   If you are persistent and polite, you will learn much.


OpenBlock features available in views
-------------------------------------

For database queries, see especially the models in
:py:mod:`ebpub.db.models`.

Most of it is plain vanilla `Django database queries
<https://docs.djangoproject.com/en/1.3/topics/db/queries/>`_, but a
few items are worth noting:

* NewsItems may have attribute values that you may want to search by,
  using :py:meth:`item.objects.by_attribute(schemafield, 'value')  <ebpub.db.models.NewsItemQuerySet.by_attribute>`.

TODO: what else? NewsItemQuerySet.text_search()?

