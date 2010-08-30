-- Trigger that updates db_newsitemlocation whenever the location is changed in
-- db_newsitem.

-- Ending statements with "--" as workaround described at http://code.djangoproject.com/ticket/3214.

CREATE OR REPLACE FUNCTION update_newsitem_location() RETURNS TRIGGER AS $location_updater$
    DECLARE
        loc_id integer; --
    BEGIN
        IF (TG_OP = 'UPDATE') THEN
            -- In a sane programming language, the following IF statement could
            -- have been combined into the previous one. But we can't do that,
            -- because short-circuit evaluation of boolean expressions is not
            -- guaranteed. See here:
            -- http://archive.netbsd.se/?ml=pgsql-sql&a=2005-09&t=1337824

            IF NEW.location IS DISTINCT FROM OLD.location THEN 
	    -- ...or maybe we want (NOT ST_Equals(NEW.location, OLD.Location))?
                IF (OLD.location IS NOT NULL) THEN
                    DELETE FROM db_newsitemlocation WHERE news_item_id = OLD.id; --
                END IF; --
                IF (NEW.location IS NOT NULL) THEN
                    IF (GeometryType(NEW.location) = 'GEOMETRYCOLLECTION') THEN
                        FOR i IN 1..ST_NumGeometries(NEW.location) LOOP
                                FOR loc_id IN SELECT id FROM db_location WHERE intersects(db_location.location, ST_GeometryN(NEW.location, i)) LOOP
                                    PERFORM * FROM db_newsitemlocation WHERE news_item_id = NEW.id AND location_id = loc_id; --
                                    IF NOT FOUND THEN
                                        INSERT INTO db_newsitemlocation (news_item_id, location_id) VALUES (NEW.id, loc_id); --
                                    END IF; --
                                END LOOP; --
                        END LOOP; --
                    ELSE
                        INSERT INTO db_newsitemlocation (news_item_id, location_id)
                        SELECT NEW.id, id FROM db_location WHERE intersects(db_location.location, NEW.location); --
                    END IF; --
                END IF; --
            END IF; --
            -- Update "Unknown" locations
            INSERT INTO db_newsitemlocation (news_item_id, location_id)
            SELECT NEW.id AS news_item_id, (SELECT id FROM db_location WHERE location_type_id=db_locationtype.id AND slug='unknown') AS location_id
            FROM db_locationtype
            WHERE NOT EXISTS (SELECT 1 FROM db_newsitemlocation WHERE news_item_id=NEW.id)
            AND db_locationtype.is_significant = true
	    AND EXISTS (SELECT 1 FROM db_location WHERE location_type_id=db_locationtype.id AND slug='unknown')
	    ; --
        ELSIF (TG_OP = 'INSERT') THEN
            -- See the above comment for why this statement isn't combined into
            -- the previous one.
            IF (NEW.location IS NOT NULL) THEN
                IF (GeometryType(NEW.location) = 'GEOMETRYCOLLECTION') THEN
                    FOR i IN 1..ST_NumGeometries(NEW.location) LOOP
                            FOR loc_id IN SELECT id FROM db_location WHERE intersects(db_location.location, ST_GeometryN(NEW.location, i)) LOOP
                                PERFORM * FROM db_newsitemlocation WHERE news_item_id = NEW.id AND location_id = loc_id; --
                                IF NOT FOUND THEN
                                    INSERT INTO db_newsitemlocation (news_item_id, location_id) VALUES (NEW.id, loc_id); --
                                END IF; --
                            END LOOP; --
                    END LOOP; --
                ELSE
                    INSERT INTO db_newsitemlocation (news_item_id, location_id)
                    SELECT NEW.id, id FROM db_location WHERE intersects(db_location.location, NEW.location); --
                END IF; --
            END IF; --
            -- Update "Unknown" locations
            INSERT INTO db_newsitemlocation (news_item_id, location_id)
            SELECT NEW.id AS news_item_id, (SELECT id FROM db_location WHERE location_type_id=db_locationtype.id AND slug='unknown') AS location_id
            FROM db_locationtype
            WHERE NOT EXISTS (SELECT 1 FROM db_newsitemlocation WHERE news_item_id=NEW.id)
            AND db_locationtype.is_significant = true
	    AND EXISTS (SELECT 1 FROM db_location WHERE location_type_id=db_locationtype.id AND slug='unknown')
	    ; --
        ELSIF (TG_OP = 'DELETE') THEN
            DELETE FROM db_newsitemlocation WHERE news_item_id = OLD.id; --
            RETURN OLD; --
        END IF; --
        RETURN NEW; --
    END; --
$location_updater$ LANGUAGE plpgsql; --

CREATE TRIGGER location_updater
BEFORE INSERT OR UPDATE OR DELETE ON db_newsitem
    FOR EACH ROW EXECUTE PROCEDURE update_newsitem_location(); --

-- To delete:
-- DROP TRIGGER location_updater ON db_newsitem;
-- DROP FUNCTION update_newsitem_location();

-- To populate for a new location:
-- INSERT INTO db_newsitemlocation (news_item_id, location_id)
-- SELECT ni.id, loc.id FROM db_newsitem ni, db_location loc
-- WHERE intersects(loc.location, ni.location) AND loc.id = 826;
