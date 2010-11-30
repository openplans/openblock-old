begin;

ALTER TABLE db_schema ADD COLUMN short_description text NOT NULL DEFAULT '';
ALTER TABLE db_schema ADD COLUMN summary text NOT NULL DEFAULT '';
ALTER TABLE db_schema ADD COLUMN source text NOT NULL DEFAULT '';
ALTER TABLE db_schema ADD COLUMN grab_bag_headline varchar(128) NOT NULL DEFAULT '';
ALTER TABLE db_schema ADD COLUMN grab_bag text NOT NULL DEFAULT '';
ALTER TABLE db_schema ADD COLUMN short_source varchar(128) NOT NULL DEFAULT '';
ALTER TABLE db_schema ADD COLUMN update_frequency  varchar(64) NOT NULL DEFAULT '';
ALTER TABLE db_schema ADD COLUMN intro text NOT NULL DEFAULT '';

UPDATE db_schema s SET short_description = si.short_description,
                       summary = si.summary,
                       source = si.source,
                       grab_bag_headline = si.grab_bag_headline,
                       grab_bag = si.grab_bag,
                       short_source = si.short_source,
                       update_frequency = si.update_frequency,
                       intro = si.intro
FROM db_schemainfo si WHERE s.id = si.schema_id;

DROP TABLE db_schemainfo;


commit;

begin;
DROP TABLE db_schemafieldinfo;
commit;
