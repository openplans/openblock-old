#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

"""
This file contains monkey-patches for upstream code that we don't wish
to fork, eg. core Django features that haven't landed in the version
of Django we need, etc.

"""


from django.utils.encoding import smart_unicode
from django.core.serializers import base

####################################################################
# Support for "natural keys" in fixtures.
# See http://code.djangoproject.com/ticket/13252
####################################################################


# django.core.serializers.base.build_instance
def build_instance(Model, data, db):
    """
    Build a model instance.

    If the model instance doesn't have a primary key and the model supports
    natural keys, try to retrieve it from the database.
    """
    obj = Model(**data)
    if obj.pk is None and hasattr(Model, 'natural_key') and\
            hasattr(Model._default_manager, 'get_by_natural_key'):
        pk = obj.natural_key()
        try:
            obj.pk = Model._default_manager.db_manager(db)\
                                           .get_by_natural_key(*pk).pk
        except Model.DoesNotExist:
            pass
    return obj

# python.Serializer.end_object
def end_object(self, obj):
    data = {
        "model": smart_unicode(obj._meta),
        "fields": self._current
    }
    if not self.use_natural_keys or not hasattr(obj, 'natural_key'):
        data['pk'] = smart_unicode(obj._get_pk_val(), strings_only=True)
    self.objects.append(data)
    self._current = None



from django.db import models, DEFAULT_DB_ALIAS

# django.core.serializers.python.Deserializer
def Deserializer(object_list, **options):
    """
    Deserialize simple Python objects back into Django ORM instances.

    It's expected that you pass the Python objects themselves (instead of a
    stream or a string) to the constructor
    """
    # Too bad this is so big, we only add a tiny bit of code
    # near the beginning and end; but not such that we can just wrap it.
    from django.conf import settings
    from django.core.serializers import python
    _get_model = python._get_model

    db = options.pop('using', DEFAULT_DB_ALIAS)
    models.get_apps()
    for d in object_list:
        # Look up the model and starting build a dict of data for it.
        Model = _get_model(d["model"])
        data = {}
        if 'pk' in d:
            data[Model._meta.pk.attname] = Model._meta.pk.to_python(d['pk'])
        m2m_data = {}

        # Handle each field
        for (field_name, field_value) in d["fields"].iteritems():
            if isinstance(field_value, str):
                field_value = smart_unicode(field_value, options.get("encoding", settings.DEFAULT_CHARSET), strings_only=True)

            field = Model._meta.get_field(field_name)

            # Handle M2M relations
            if field.rel and isinstance(field.rel, models.ManyToManyRel):
                if hasattr(field.rel.to._default_manager, 'get_by_natural_key'):
                    def m2m_convert(value):
                        if hasattr(value, '__iter__'):
                            return field.rel.to._default_manager.db_manager(db).get_by_natural_key(*value).pk
                        else:
                            return smart_unicode(field.rel.to._meta.pk.to_python(value))
                else:
                    m2m_convert = lambda v: smart_unicode(field.rel.to._meta.pk.to_python(v))
                m2m_data[field.name] = [m2m_convert(pk) for pk in field_value]

            # Handle FK fields
            elif field.rel and isinstance(field.rel, models.ManyToOneRel):
                if field_value is not None:
                    if hasattr(field.rel.to._default_manager, 'get_by_natural_key'):
                        if hasattr(field_value, '__iter__'):
                            obj = field.rel.to._default_manager.db_manager(db).get_by_natural_key(*field_value)
                            value = getattr(obj, field.rel.field_name)
                            # If this is a natural foreign key to an object that
                            # has a FK/O2O as the foreign key, use the FK value
                            if field.rel.to._meta.pk.rel:
                                value = value.pk
                        else:
                            value = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                        data[field.attname] = value
                    else:
                        data[field.attname] = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)

                else:
                    data[field.attname] = None

            # Handle all other fields
            else:
                data[field.name] = field.to_python(field_value)

        obj = base.build_instance(Model, data, db)

        yield base.DeserializedObject(obj, m2m_data)

# django.core.serializers.xml_serializer.Serializer.start_object
def start_object(self, obj):
    """
    Called as each object is handled.
    """
    if not hasattr(obj, "_meta"):
        raise base.SerializationError("Non-model object (%s) encountered during serialization" % type(obj))

    self.indent(1)
    object_data = {"model": smart_unicode(obj._meta)}
    if not self.use_natural_keys or not hasattr(obj, 'natural_key'):
        object_data['pk'] = smart_unicode(obj._get_pk_val())
    self.xml.startElement("object", object_data)



# django.core.serializers.xml_serializer.Deserializer._handle_object
def _handle_object(self, node):
    """
    Convert an <object> node to a DeserializedObject.
    """
    from django.core.serializers import xml_serializer
    getInnerText = xml_serializer.getInnerText

    # Look up the model using the model loading mechanism. If this fails,
    # bail.

    Model = self._get_model_from_node(node, "model")

    # Start building a data dictionary from the object.
    data = {}
    if node.hasAttribute('pk'):
        data[Model._meta.pk.attname] = Model._meta.pk.to_python(
                                                node.getAttribute('pk'))

    # Also start building a dict of m2m data (this is saved as
    # {m2m_accessor_attribute : [list_of_related_objects]})
    m2m_data = {}

    # Deseralize each field.
    for field_node in node.getElementsByTagName("field"):
        # If the field is missing the name attribute, bail (are you
        # sensing a pattern here?)
        field_name = field_node.getAttribute("name")
        if not field_name:
            raise base.DeserializationError("<field> node is missing the 'name' attribute")

        # Get the field from the Model. This will raise a
        # FieldDoesNotExist if, well, the field doesn't exist, which will
        # be propagated correctly.
        field = Model._meta.get_field(field_name)

        # As is usually the case, relation fields get the special treatment.
        if field.rel and isinstance(field.rel, models.ManyToManyRel):
            m2m_data[field.name] = self._handle_m2m_field_node(field_node, field)
        elif field.rel and isinstance(field.rel, models.ManyToOneRel):
            data[field.attname] = self._handle_fk_field_node(field_node, field)
        else:
            if field_node.getElementsByTagName('None'):
                value = None
            else:
                value = field.to_python(getInnerText(field_node).strip())
            data[field.name] = value

    obj = base.build_instance(Model, data, self.db)

    # Return a DeserializedObject so that the m2m data has a place to live.
    return base.DeserializedObject(obj, m2m_data)

####################################################################
# End of "natural keys" fixture support.
####################################################################


####################################################################
# Patch django.utils.xmlutils to put newlines after closing tags,
# for some modicum of readability.
####################################################################

def endElement(self, name):
    self._write('</%s>\n' % name)



####################################################################
# End of patches.
####################################################################

import threading
_PATCHED = False
_lock = threading.Lock()
def patch_once():
    with _lock:
        global _PATCHED
        if _PATCHED:
            return

        ####################################################
        # Natural keys.
        base.build_instance = build_instance

        # Serialization.
        from django.core.serializers import python
        python.Deserializer = Deserializer
        python.Serializer.end_object = end_object
        # have to patch stuff that's already been loaded with a 'from' import, yay
        from django.core.serializers import json
        json.PythonDeserializer = Deserializer

        from django.core.serializers import xml_serializer
        xml_serializer.Serializer.start_object = start_object
        xml_serializer.Deserializer._handle_object = _handle_object

        ####################################################
        # XML output
        from django.utils import xmlutils
        xmlutils.SimplerXMLGenerator.endElement = endElement

        _PATCHED = True
