-- This is useful if you want to reset just your newsitems
-- and not your locations.
-- If you want to reset ALL of the db models, use `django-admin.py sqlreset db`

truncate table db_attribute cascade;
truncate table db_lookup cascade;
truncate table db_newsitem cascade;
truncate table db_newsitemlocation cascade;
truncate table db_schemafield cascade;
truncate table db_schema cascade;
truncate table db_aggregate cascade;

alter sequence db_lookup_id_seq restart with 1;
alter sequence db_attribute_id_seq restart with 1;
alter sequence db_schemafield_id_seq restart with 1;
alter sequence db_schema_id_seq restart with 1;
alter sequence db_newsitem_id_seq restart with 1;
