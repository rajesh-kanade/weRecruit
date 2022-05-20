
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

-- application status codes category and subcategory tables introduced

CREATE TABLE IF NOT EXISTS public.resume_application_status_codes_category
(
    id smallint NOT NULL,
    description VARCHAR NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    CONSTRAINT resume_application_status_codes_category_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.resume_application_status_codes_sub_category
(
    id smallint NOT NULL,
    description character varying COLLATE pg_catalog."default" NOT NULL,
    category_id smallint,
    CONSTRAINT resume_application_status_codes_sub_category_pkey PRIMARY KEY (id),
    CONSTRAINT category_id FOREIGN KEY (category_id)
        REFERENCES public.resume_application_status_codes_category (id)
);

INSERT INTO public.resume_application_status_codes_category(id,description)
VALUES (1,'Resume'),
    (2,'Initial Screening'),
    (3,'Round 1'),
    (4,'Round 2'),
    (5,'Hiring Manager'),
    (6,'HR'),
    (7,'Offer'),
    (8,'Onboarding');

INSERT INTO public.resume_application_status_codes_sub_category(id,description,category_id)
VALUES (0,'Shortlisted',1),
    (1,'Scheduled',2),
    (2,'Cleared',2),
    (3,'Failed',2),
    (10,'Scheduled',3),
    (20,'Cleared',3),
    (30,'Failed',3),
    (31,'No Show',3),
    (40,'Scheduled',4),
    (50,'Cleared',4),
    (60,'Failed',4),
    (61,'No Show',4),
    (70,'Scheduled',5),
    (80,'Cleared',5),
    (90,'Failed',5),
    (91,'No Show',5),
    (100,'Scheduled',6),
    (110,'Cleared',6),
    (120,'Failed',6),
    (121,'No Show',6),
    (130,'Pending with HR',7),
    (140,'Released to candidate',7),
    (150,'Accepted by candidate',7),
    (160,'Done',8),
    (170,'No Show',8);

-- changes end here dated 18/05/2022