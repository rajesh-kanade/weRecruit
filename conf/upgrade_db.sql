
/* start upgrade prod on 29-Dec-2021 */
 
ALTER TABLE public.wr_resumes
    ADD COLUMN json_resume jsonb ;
/* end upgrade prod on 29-Dec-2021 */


/* start upgrade prod on 12-Feb-2022 */
ALTER TABLE public.wr_jds
    ADD COLUMN client_jd bytea ;

ALTER TABLE public.wr_resumes
    ADD COLUMN resume_content bytea ;

ALTER TABLE public.wr_resumes ADD COLUMN ts tsvector 
    GENERATED ALWAYS AS (to_tsvector('english', json_resume)) STORED;

CREATE INDEX ts_idx ON wr_resumes USING GIN (ts);
/* end upgrade prod on 12-Feb-2022 */


/* ******** start upgrade prod on 14-March-2022 ***************** */
ALTER TABLE public.wr_jds
  RENAME COLUMN yrs_of_exp TO min_yrs_of_exp;

ALTER TABLE public.wr_jds
    ADD COLUMN max_yrs_of_exp NUMERIC(4,2) ;
/* ******** start upgrade prod on 14-March-2022 ***************** */


/* ******** start upgrade prod on 28-March-2022 on contabo2 server *******************/

ALTER TABLE public.wr_resumes
    ADD COLUMN is_deleted boolean NOT NULL DEFAULT false ;

ALTER TABLE public.wr_jds
    ADD COLUMN is_deleted boolean NOT NULL DEFAULT false ;


insert into public.application_status_codes(id,description,is_deleted) values (1,'Initial screening scheduled',false);
insert into public.application_status_codes(id,description,is_deleted) values (2,'Initial screening cleared',false);
insert into public.application_status_codes(id,description,is_deleted) values (3,'Initial screening failed',false);


/* ******** end upgrade prod on 28-March-2022 on contabo2 server *******************/


/* *** #26 location drop down issue new table creation and alter in wr_jds 22/05/2022 ****/ 

CREATE TABLE IF NOT EXISTS public.countries
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    code character varying(3) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT countries_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.countries
    OWNER to werecruit;

CREATE TABLE IF NOT EXISTS public.cities
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    country_id integer NOT NULL,
    CONSTRAINT cities_pkey PRIMARY KEY (id),
    CONSTRAINT fk_country FOREIGN KEY (country_id)
        REFERENCES public.countries (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.cities
    OWNER to werecruit;

insert into countries(name, code) 
values ('India', 'IN');

insert into public.cities(id, name, country_id)
OVERRIDING SYSTEM VALUE 
values (1,	'Mumbai',	1),
(2,	'Delhi',	1),
(3,'Bengaluru',	1),
(4, 'Kolkata',	1),
(5	,'Chennai',	1),
(6	,'Ahmedabad',	1),
(7	,'Hyderabad',	1),
(8	,'Pune',	1),
(9	,'Surat',	1),
(10	,'Kanpur',	1),
(11	,'Jaipur'	,1),
(12	,'Navi Mumbai',	1),
(13	,'Lucknow',	1),
(14	,'Nagpur',	1),
(15	,'Indore',	1),
(16	,'Patna',	1),
(17	,'Bhopal',	1),
(18	,'Ludhiana',	1),
(19	,'Tirunelveli',	1),
(20	,'Agra',	1),
(21	,'Vadodara',	1),
(22	,'Gorakhpur',	1),
(23	,'Nashik',	1),
(24	,'Pimpri',	1),
(25	,'Kalyan',	1),
(26	,'Thane',	1),
(27	,'Meerut',	1),
(28	,'Nowrangapur',	1),
(29	,'Faridabad',	1),
(30	,'Ghaziabad',	1),
(31	,'Dombivli',	1),
(32	,'Rajkot',	1),
(33	,'Varanasi',	1),
(34	,'Amritsar',	1),
(35	,'Allahabad',	1),
(36	,'Visakhapatnam',	1),
(37	,'Teni',	1),
(38	,'Jabalpur',	1),
(39	,'Haora',	1),
(40,'Aurangabad',	1),
(41	,'Shivaji Nagar',	1),
(42	,'Solapur',	1),
(43	,'Srinagar',	1),
(44	,'Chandigarh',	1),
(45	,'Coimbatore',	1),
(46	,'Jodhpur',	1),
(47	,'Madurai',	1),
(48	,'Guwahati',	1),
(49	,'Gwalior',	1),
(50	,'Vijayawada',	1);

alter TABLE if exists public.wr_jds
drop column location;

alter table if exists public.wr_jds
add column city_id int;

/* ******** end upgrade prod on 22/05/2022 for countries and cities *******************/


/* **** 25/05/2022 status codes table creation **** */
CREATE TABLE IF NOT EXISTS public.resume_application_status_codes_category
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    description character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT resume_application_status_codes_category_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.resume_application_status_codes_category
    OWNER to werecruit;

CREATE TABLE IF NOT EXISTS public.resume_application_status_codes_sub_category
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    description character varying(100) COLLATE pg_catalog."default" NOT NULL,
    category_id integer,
    CONSTRAINT resume_application_status_codes_sub_category_pkey PRIMARY KEY (id),
    CONSTRAINT category_fk FOREIGN KEY (category_id)
        REFERENCES public.resume_application_status_codes_category (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.resume_application_status_codes_sub_category
    OWNER to werecruit;

INSERT INTO public.resume_application_status_codes_category(
	id, description)
    OVERRIDING SYSTEM VALUE
	VALUES (1, 'Resume Shortlisted'),
    (2, 'Initial Screening'),
    (3, 'Round 1'),
    (4, 'Round 2'),
    (5, 'Hiring Manager'),
    (6, 'HR'),
    (7, 'Offer'),
    (8, 'Onboarding');

INSERT INTO public.resume_application_status_codes_sub_category(
	id, description, category_id)
    OVERRIDING SYSTEM VALUE
	VALUES (0, 'Shortlisted', 1),
    (1, 'Scheduled', 2),
    (2, 'Cleared', 2),
    (3, 'Failed', 2),
    (10, 'Scheduled', 3),
    (20, 'Cleared', 3),
    (30, 'Failed', 3),
    (31, 'No Show', 3),
    (40, 'Scheduled', 4),
    (50, 'Cleared', 4),
    (60, 'Failed', 4),
    (61, 'No Show', 4),
    (70, 'Scheduled', 5),
    (80, 'Cleared', 5),
    (90, 'Failed', 5),
    (91, 'No Show', 5),
    (100, 'Scheduled', 6),
    (110, 'Cleared', 6),
    (120, 'Failed', 6),
    (121, 'No Show', 6),
    (130, 'Pending with HR', 7),
    (140, 'Released to Candidate', 7),
    (150, 'Accepted by Candidate', 7),
    (160, 'Done', 8),
    (170, 'No Show', 8);

/* ******** end upgrade prod on 25/05/2022 for status codes category and sub category *****/

/* ***** 22/06/2022 wr_clients table creation, added column client_id on wr_jds  ****** */

CREATE TABLE IF NOT EXISTS public.wr_clients
(
    client_id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    client_name text COLLATE pg_catalog."default" NOT NULL,
    tenant_id bigint,
    CONSTRAINT wr_clients_pkey PRIMARY KEY (client_id),
    CONSTRAINT client_name_unique UNIQUE (client_name, tenant_id),

    CONSTRAINT tenant_id FOREIGN KEY (tenant_id)
        REFERENCES public.tenants (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.wr_clients
    OWNER to werecruit;

ALTER TABLE IF EXISTS public.wr_jds
add column client_id bigint;


-- **** WARNING WARNING WARNING BEFORE RUNNING FOLLOWING COMMAND, PLEASE RUN upgrade.py to migrate existing data
ALTER TABLE IF EXISTS public.wr_jds
drop column client;

/* ******** end upgrade prod on 22/06/2022 for status codes category and sub category *****/

/* ***** 26/06/2022 updated status sub categories  ****** */
UPDATE application_status_codes
SET description = 'Initial Screening Scheduled'
WHERE id=1;

UPDATE application_status_codes
SET description = 'Initial Screening Cleared'
WHERE id=2;

UPDATE application_status_codes
SET description = 'Initial Screening Failed'
WHERE id=3;

UPDATE application_status_codes
SET description = 'Offer Pending To Candidate'
WHERE id=130;

UPDATE application_status_codes
SET description = 'Offer Released To Candidate'
WHERE id=140;

UPDATE application_status_codes
SET description = 'Offer Accepted By Candidate'
WHERE id=150;

UPDATE application_status_codes
SET description = 'Candidate Onboarding Completed'
WHERE id=160;

UPDATE application_status_codes
SET description = 'Candidate Was A No Show'
WHERE id=170;
/* ******** end upgrade prod on 26/06/2022 for updated status sub categories **** */

/* ***** start upgrade 16/08/2022 for issue 280  ****** */

ALTER TABLE public.wr_resumes
    ADD COLUMN notes text COLLATE pg_catalog."default";


/* ******** end upgrade prod on 16/08/2022 for issue 280 **** */


/* ***** start upgrade 22/Aug/2022 for issue 281  ****** */

ALTER TABLE tenants
    ADD COLUMN creation_date timestamp with time zone;

UPDATE tenants SET creation_date = '2022-01-01 00:00:00'; 

ALTER TABLE tenants ALTER COLUMN creation_date SET NOT NULL;

ALTER TABLE tenants
    ADD COLUMN updation_date timestamp with time zone;



ALTER TABLE users
    ADD COLUMN creation_date timestamp with time zone;

UPDATE users SET creation_date = '2022-01-01 00:00:00'; 

ALTER TABLE users ALTER COLUMN creation_date SET NOT NULL;

ALTER TABLE users
    ADD COLUMN updation_date timestamp with time zone;

/* ******** end upgrade prod on 22/Aug/2022 for issue 281 **** */

/** start upgrade 13 Sept 2022 **/
CREATE TABLE public.skillsets
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    skillset_name text COLLATE pg_catalog."default" NOT NULL,
    relevancy smallint,
    CONSTRAINT skillsets_pkey PRIMARY KEY (id),
    CONSTRAINT skillset_name_unique UNIQUE (skillset_name)

)

TABLESPACE pg_default;

ALTER TABLE public.skillsets
    OWNER to werecruit;

CREATE TABLE public.skills
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    skillset_id bigint NOT NULL,
    skill_name text COLLATE pg_catalog."default" NOT NULL,
    weight smallint NOT NULL,
    CONSTRAINT skills_pkey PRIMARY KEY (id, skillset_id),
    CONSTRAINT skills_skillset_id_fkey FOREIGN KEY (skillset_id)
        REFERENCES public.skillsets (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.skills
    OWNER to werecruit;

INSERT INTO public.skillsets(id,skillset_name,relevancy) 
OVERRIDING SYSTEM VALUE 
VALUES
(1,'java-core',1),
(2,'web-frontend', 1),
 (3,'db-dev', 1),
(4,'linux', 1),
(5,'web-backend', 1),
(6,'test-automation', 1),
(7,'bi-tools', 1),
(8,'etl', 1),
(9,'dotnet-dev', 1),
(10,'devops', 1),
(11,'test-manual', 1);

DELETE FROM public.skills where skillset_id=1;
INSERT INTO public.skills(
	skillset_id, skill_name,weight)
	VALUES ( 1, 'java',3),(1,'jdbc',2),(1,'spring',2),(1,'spring-boot',2),( 1, 'hibernate',1),(1,'J2EE',1);
	
DELETE FROM public.skills where skillset_id=2;
INSERT INTO public.skills(
	skillset_id, skill_name,weight)
	VALUES ( 2, 'html',3),(2,'css',1), ( 2, 'jquery',2),( 2, 'angular',3),( 2, 'reactjs',3),
	( 2, 'react',3),( 2, 'javascript',2),(2,'bootstrap',2);

ALTER TABLE wr_resumes
    ADD COLUMN creation_date timestamp with time zone;

UPDATE wr_resumes SET creation_date = '2022-01-01 00:00:00'; 

ALTER TABLE wr_resumes ALTER COLUMN creation_date SET NOT NULL;

ALTER TABLE wr_resumes
    ADD COLUMN updation_date timestamp with time zone;

ALTER TABLE wr_jds 
    ADD COLUMN top_skills integer[];

INSERT INTO public.resume_application_status_codes_category(
	id, description)
    OVERRIDING SYSTEM VALUE
	VALUES (-1, 'Resume Auto Shortlisted');

INSERT INTO public.resume_application_status_codes_sub_category(
	id, description, category_id)
    OVERRIDING SYSTEM VALUE
	VALUES (-1, 'Auto Shortlisted', 1);

insert into public.application_status_codes(id,description,is_deleted) 
    values (-1,'Auto Shortlisted',false);

/** end upgrade 13 Sept 2022 ****/

/* Add Tomcat support engineer 
schema uprgaded on 1 Oct 2022 */

INSERT INTO public.skillsets(id,skillset_name,relevancy) 
OVERRIDING SYSTEM VALUE 
VALUES
(12,'Tomcat Support Engineer',1);

DELETE FROM public.skills where skillset_id=12;

INSERT INTO public.skills(
	skillset_id, skill_name,weight)
	VALUES 
    ( 12, 'Tomcat',1),
    ( 12, 'Linux',2),
    ( 12, 'Shell Scripting',2);

/* End tomcat support engineer */