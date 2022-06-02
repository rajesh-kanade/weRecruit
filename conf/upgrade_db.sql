
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

/***** changed precision for max_years_of_exp for wr_jds *****/

ALTER TABLE wr_jds
ALTER COLUMN max_yrs_of_exp TYPE numeric(5,2);

/*** end upgrade on 2/06/2022 ****/