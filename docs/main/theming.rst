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

Many parts of OpenBlock's markup can be customized on a per-schema
basis.

This is accomplished by following simple naming conventions.  In each
case described below, all you need to do is create a template, with a
filename based on the Schema's slug, in a directory whose name is
based on the view that uses the template.  Details follow.

Custom NewsItem lists
---------------------

When NewsItems are displayed as lists, for example by the
``schema_filter`` or ``location_detail`` views, generally templates
should use the
:py:func:`newsitem_list_by_schema <ebpub.db.templatetags.eb.do_newsitem_list_by_schema>` template tag.  Usage looks like::

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
                     ]

This page also uses the same map popup templates
described in :ref:`custom-map-popups`.


Overriding CSS and Images
=========================

TODO

Overriding Views
================

View code can be overridden in the normal Django way:

1. Be sure your app is in ``settings.INSTALLED_APPS``.

2. Create a view function in your ``views.py`` file.

3. Add a line in your ``urls.py`` which routes the relevant
   URL to your view function instead of the default ebpub view.

Note that there are several ``urls.py`` files throughout the ``ebpub``
code; you may have to look through several to find the relevant URL
pattern registration you want to override.  Be sure to preserve the view name,
if used in the original ``urls.py``; this is likely used by OpenBlock
for reverse URL generation.
