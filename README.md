PHaEDRA EAD Archive
============

An archive of files related to the EAD for Project PHaEDRA.  Including the history of updates to the EAD xml file as we obtain more metadata about the material.

Current finding aid found at:
http://nrs.harvard.edu/urn-3:FCOR.WOLBACH:wol00001

Proceedure:

1) Double check that all entries in the PHaEDRA database using the queries below.  Check that all items have:
- a marked "first" author or NO authors
- have date ranges that do NOT end *before* they begin
  - if updating the date without checking the item, add a "status note" in the database to flag for recheck later
2) Run phaedra_ead.py to generate the XML file.
3) Validate generated EAD against LoC schema (ead.xsd) using http://xmlvalidator.new-studio.org/
4) Log into ArchivesSpace and Delete the current resource.
5) Upload EAD as new Background Job.
6) After it uploads, navigate to the main Resource entry and Publish all.
7) Should recieve notification of sucecss or failure at the next top/bottom of the hour.


SQL Queries:

*This query verifies that no item in the database has a start date that is greater than its end date.
An item returned by the script has a start date that comes after its end date (or a combination of start year, start month, and start day that comes after the end year (or end year and month))*

SELECT item_id, STR_TO_DATE(CONCAT_WS('-', CAST(start_year AS CHAR), CAST(start_month AS CHAR), CAST(start_day AS CHAR)), '%Y-%m-%d') AS start_date,
STR_TO_DATE(CONCAT_WS('-', CAST(end_year AS CHAR), CAST(end_month AS CHAR), CAST(end_day AS CHAR)), '%Y-%m-%d') AS end_date
FROM items
HAVING start_date > end_date AND end_date > '0000-00-00';

*This script selects any item with a person attached but none marked as first.
It does so by creating two "virtual" tables:
t1 is all items listed in item_persons where a position other than 1 is specified.
t2 is all items listed in item_persons which have only one person specified.
It then selects all items that appear in both t1 and t2.*

SELECT t1.item_id FROM
(SELECT item_id
FROM item_persons
WHERE item_person_position != 1) AS t1
INNER JOIN (SELECT item_id, COUNT(item_person_id) AS number_of_people
FROM item_persons
GROUP BY item_id
HAVING number_of_people = 1) AS t2 on t1.item_id = t2.item_id;


*This script selects all items which have multiple people but none marked as first.
To do so, it creates two "virtual" tables:
t1 is all items listed in item_persons where no position is specified.
t2 is all items listed in item_persons where a position of 1 is specified.
It then selects all items that appear in t1 and not in t2.*

SELECT t1.item_id FROM
(SELECT item_id
FROM item_persons
WHERE item_person_position IS NULL) AS t1
LEFT JOIN (SELECT item_id
FROM item_persons
WHERE item_person_position = 1) AS t2 ON t1.item_id = t2.item_id
WHERE t2.item_id IS NULL
GROUP BY item_id;