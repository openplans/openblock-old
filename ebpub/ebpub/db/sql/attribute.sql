-- AFAICT this is a query-planner optimization: The default STATISTICS
-- level is 10.  Lowering it means: Do less work generating stats on
-- this column, because it has a "simple distribution" (just a few
-- possible integer values), so we don't need to expend much time or
-- space on helping out the query planner.
-- Presumably, somebody at everyblock.com found that this improved
-- performance.
-- See http://www.postgresql.org/docs/8.2/static/planner-stats.html
-- and http://www.postgresql.org/docs/8.2/static/runtime-config-query.html

ALTER TABLE db_attribute ALTER COLUMN schema_id SET STATISTICS 5;
