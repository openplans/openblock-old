"""
This file contains monkey-patches for upstream code that we don't wish
to fork, eg. core Django features that haven't landed in the version
of Django we need, etc.

"""


from django.utils.encoding import smart_unicode
from django.core.serializers import base

####################################################################
# Support for "natural keys" in fixtures.
####################################################################

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

# Too bad this is so big, we only add a tiny bit of code
# near the beginning and end; but not such that we can just wrap it.
def Deserializer(object_list, **options):
    """
    Deserialize simple Python objects back into Django ORM instances.

    It's expected that you pass the Python objects themselves (instead of a
    stream or a string) to the constructor
    """
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

##########################################################################
# "Final" syncdb signal - based on patch for Django issue #7561
# (allows a workaround for Django #13826 which affected us by
# prevented our custom sql in ebpub/db/sql/location.sql from being
# loaded)
##########################################################################

from django.db.models import signals
from django.core.management.commands import syncdb

final_post_syncdb = signals.Signal(providing_args=["class", "app", "created_models", "verbosity", "interactive"])

def emit_post_sync_signal(created_models, verbosity, interactive, db):
    return emit_signal_to_models(models.signals.post_syncdb,"post-sync",created_models,verbosity,interactive,db)

def emit_final_post_sync_signal(created_models, verbosity, interactive, db):
    return emit_signal_to_models(models.signals.final_post_syncdb,"final-post-sync",created_models,verbosity,interactive,db)

def emit_signal_to_models(signal, signal_name, created_models, verbosity, interactive, db):
    # Emit the post_sync signal for every application.
    for app in models.get_apps():
        app_name = app.__name__.split('.')[-2]
        if verbosity >= 2:
            print "Running", signal_name,"handlers for application", app_name
        signal.send(sender=app, app=app,
            created_models=created_models, verbosity=verbosity,
            interactive=interactive, db=db)

from django.conf import settings
from django.core.management.color import no_style
from django.core.management.sql import custom_sql_for_model
from django.db import connections, router, transaction
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module
import sys

def handle_noargs(self, **options):
    verbosity = int(options.get('verbosity', 1))
    interactive = options.get('interactive')
    show_traceback = options.get('traceback', False)

    self.style = no_style()

    # Import the 'management' module within each installed app, to register
    # dispatcher events.
    for app_name in settings.INSTALLED_APPS:
        try:
            import_module('.management', app_name)
        except ImportError, exc:
            # This is slightly hackish. We want to ignore ImportErrors
            # if the "management" module itself is missing -- but we don't
            # want to ignore the exception if the management module exists
            # but raises an ImportError for some reason. The only way we
            # can do this is to check the text of the exception. Note that
            # we're a bit broad in how we check the text, because different
            # Python implementations may not use the same text.
            # CPython uses the text "No module named management"
            # PyPy uses "No module named myproject.myapp.management"
            msg = exc.args[0]
            if not msg.startswith('No module named') or 'management' not in msg:
                raise

    db = options.get('database', DEFAULT_DB_ALIAS)
    connection = connections[db]
    cursor = connection.cursor()

    # Get a list of already installed *models* so that references work right.
    tables = connection.introspection.table_names()
    seen_models = connection.introspection.installed_models(tables)
    created_models = set()
    pending_references = {}

    # Build the manifest of apps and models that are to be synchronized
    all_models = [
        (app.__name__.split('.')[-2],
            [m for m in models.get_models(app, include_auto_created=True)
            if router.allow_syncdb(db, m)])
        for app in models.get_apps()
    ]
    def model_installed(model):
        opts = model._meta
        converter = connection.introspection.table_name_converter
        return not ((converter(opts.db_table) in tables) or
            (opts.auto_created and converter(opts.auto_created._meta.db_table) in tables))

    manifest = SortedDict(
        (app_name, filter(model_installed, model_list))
        for app_name, model_list in all_models
    )

    # Create the tables for each model
    for app_name, model_list in manifest.items():
        for model in model_list:
            # Create the model's database table, if it doesn't already exist.
            if verbosity >= 2:
                print "Processing %s.%s model" % (app_name, model._meta.object_name)
            sql, references = connection.creation.sql_create_model(model, self.style, seen_models)
            seen_models.add(model)
            created_models.add(model)
            for refto, refs in references.items():
                pending_references.setdefault(refto, []).extend(refs)
                if refto in seen_models:
                    sql.extend(connection.creation.sql_for_pending_references(refto, self.style, pending_references))
            sql.extend(connection.creation.sql_for_pending_references(model, self.style, pending_references))
            if verbosity >= 1 and sql:
                print "Creating table %s" % model._meta.db_table
            for statement in sql:
                cursor.execute(statement)
            tables.append(connection.introspection.table_name_converter(model._meta.db_table))


    transaction.commit_unless_managed(using=db)

    # Send the post_syncdb signal, so individual apps can do whatever they need
    # to do at this point.
    emit_post_sync_signal(created_models, verbosity, interactive, db)

    # The connection may have been closed by a syncdb handler.
    cursor = connection.cursor()

    # Install custom SQL for the app (but only if this
    # is a model we've just created)
    for app_name, model_list in manifest.items():
        for model in model_list:
            if model in created_models:
                custom_sql = custom_sql_for_model(model, self.style, connection)
                if custom_sql:
                    if verbosity >= 1:
                        print "Installing custom SQL for %s.%s model" % (app_name, model._meta.object_name)
                    try:
                        for sql in custom_sql:
                            cursor.execute(sql)
                    except Exception, e:
                        sys.stderr.write("Failed to install custom SQL for %s.%s model: %s\n" % \
                                            (app_name, model._meta.object_name, e))
                        if show_traceback:
                            import traceback
                            traceback.print_exc()
                        transaction.rollback_unless_managed(using=db)
                    else:
                        transaction.commit_unless_managed(using=db)
                else:
                    if verbosity >= 2:
                        print "No custom SQL for %s.%s model" % (app_name, model._meta.object_name)

    # Install SQL indicies for all newly created models
    for app_name, model_list in manifest.items():
        for model in model_list:
            if model in created_models:
                index_sql = connection.creation.sql_indexes_for_model(model, self.style)
                if index_sql:
                    if verbosity >= 1:
                        print "Installing index for %s.%s model" % (app_name, model._meta.object_name)
                    try:
                        for sql in index_sql:
                            cursor.execute(sql)
                    except Exception, e:
                        sys.stderr.write("Failed to install index for %s.%s model: %s\n" % \
                                            (app_name, model._meta.object_name, e))
                        transaction.rollback_unless_managed(using=db)
                    else:
                        transaction.commit_unless_managed(using=db)

    # XXX START OF PATCH
    # Send the final_post_syncdb signal, so individual apps can do
    # whatever they need to do at this point.
    emit_final_post_sync_signal(created_models, verbosity, interactive, db)
    # The connection may have been closed by a syncdb handler.
    cursor = connection.cursor()
    # XXX END OF PATCH
    from django.core.management import call_command
    call_command('loaddata', 'initial_data', verbosity=verbosity, database=db)


####################################################################
# End of final syncdb signal support.
####################################################################



_PATCHED = False
def patch_once():
    global _PATCHED
    if _PATCHED:
        return

    base.build_instance = build_instance

    ####################################################
    # Serialization
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
    # post-syncdb signals
    signals.final_post_syncdb = final_post_syncdb
    from django.core.management import sql
    sql.emit_post_sync_signal = emit_post_sync_signal
    sql.emit_final_post_sync_signal = emit_final_post_sync_signal
    sql.emit_signal_to_models = emit_signal_to_models
    syncdb.emit_final_post_sync_signal = emit_final_post_sync_signal
    syncdb.Command.handle_noargs = handle_noargs
    _PATCHED = True
