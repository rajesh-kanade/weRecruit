
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE EXTENSION IF NOT EXISTS hstore WITH SCHEMA public;
COMMENT ON EXTENSION hstore IS 'data type for storing sets of (key, value) pairs';


SET default_tablespace = '';

SET default_with_oids = false;

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE public.tenants
(
    name text COLLATE pg_catalog."default" NOT NULL,
    status smallint NOT NULL,
    is_deleted boolean not null,
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    primary key (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.tenants
    OWNER to postgres;


CREATE TABLE public.roles
(
    name text COLLATE pg_catalog."default" NOT NULL,
    status smallint NOT NULL,
    is_deleted boolean not null,
    id smallint not null,
    primary key (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

CREATE TABLE public.application_status_codes
(
    id smallint not null,
    description text COLLATE pg_catalog."default" NOT NULL,
    is_deleted boolean not null,
    primary key (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.application_status_codes
    OWNER to postgres;


CREATE TABLE public.users
(
    email text COLLATE pg_catalog."default" NOT NULL UNIQUE,
    name text COLLATE pg_catalog."default" NOT NULL UNIQUE,
    status smallint NOT NULL,
    is_deleted boolean NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.users
    OWNER to postgres;

CREATE TABLE public.tenant_user_roles
(
    tid bigint not null,
    uid bigint not null,
    rid bigint not null,
    PRIMARY KEY (tid,uid,rid),
    foreign key ( tid ) references public.tenants(id),
    foreign key (uid) references public.users(id),
    foreign key ( rid) references public.roles(id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.tenant_user_roles
    OWNER to postgres;

CREATE TABLE public.wr_jds
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    title text COLLATE pg_catalog."default" NOT NULL,
    details text COLLATE pg_catalog."default" ,
    positions smallint ,
    client text COLLATE pg_catalog."default" ,
    location text COLLATE pg_catalog."default",

    yrs_of_exp NUMERIC(4,2) ,
    primary_skills text COLLATE pg_catalog."default",
    secondary_skills text COLLATE pg_catalog."default",
    jd_file_name text COLLATE pg_catalog."default",
    ctc_min NUMERIC(15,2),
    ctc_max NUMERIC(15,2),
    ctc_currency text COLLATE pg_catalog."default",

    fees_in_percent  NUMERIC (4, 2),
    warranty_period_in_months smallint ,

    hiring_mgr_name text COLLATE pg_catalog."default" ,
    hiring_mgr_emailid text COLLATE pg_catalog."default",
    hiring_mgr_phone text COLLATE pg_catalog."default",

    open_date timestamp with time zone ,
    status smallint NOT NULL,
    recruiter_id bigint not null,

    ip_name_1 text COLLATE pg_catalog."default",
    ip_emailid_1 text COLLATE pg_catalog."default",
    ip_phone_1 text COLLATE pg_catalog."default",

    ip_name_2 text COLLATE pg_catalog."default",
    ip_emailid_2 text COLLATE pg_catalog."default",
    ip_phone_2 text COLLATE pg_catalog."default",

    hr_name text COLLATE pg_catalog."default" ,
    hr_emailid text COLLATE pg_catalog."default",
    hr_phone text COLLATE pg_catalog."default",
    
    jd_stats jsonb,

    PRIMARY KEY (id),
    foreign key ( recruiter_id) references public.users(id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.wr_jds
    OWNER to postgres;


create table public.wr_resumes
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    name text COLLATE pg_catalog."default" not null,
    email text COLLATE pg_catalog."default" not null,
    phone text COLLATE pg_catalog."default" not null,
    recruiter_id bigint not null,
    resume_filename text COLLATE pg_catalog."default",
    PRIMARY KEY (id),
    foreign key ( recruiter_id) references public.users(id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.wr_resumes
    OWNER to postgres;

create table public.wr_jd_resumes
(
    jd_id bigint NOT NULL ,
    resume_id bigint not null,
    application_date timestamp with time zone not null,
    status smallint not null,
    notes text COLLATE pg_catalog."default",
    PRIMARY KEY (jd_id, resume_id),
    foreign key (jd_id) references public.wr_jds(id),
    foreign key(resume_id) references public.wr_resumes(id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.wr_jd_resumes
    OWNER to postgres;


create table public.wr_jd_resume_status_audit_log
(
    jd_id bigint NOT NULL ,
    resume_id bigint not null,
    change_date timestamp with time zone not null,
    changed_by bigint NOT NULL,
    status smallint NOT NULL,
    notes text COLLATE pg_catalog."default",
    foreign key (jd_id) references public.wr_jds(id),
    foreign key(resume_id) references public.wr_resumes(id),
    foreign key (status) references public.application_status_codes(id),
    foreign key(changed_by) references public.users(id)

)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.wr_jd_resume_status_audit_log
    OWNER to postgres;


insert into public.roles(id,name,is_deleted, status) values (1,'admin',false,0);
insert into public.roles(id,name,is_deleted, status) values (2,'recruiter',false,0);


insert into public.application_status_codes(id,description,is_deleted) values (0,'Shortlisted',false);

insert into public.application_status_codes(id,description,is_deleted) values (10,'Round #1 Interview Scheduled',false);
insert into public.application_status_codes(id,description,is_deleted) values (20,'Round #1 Interview Cleared',false);
insert into public.application_status_codes(id,description,is_deleted) values (30,'Round #1 Interview Failed',false);
insert into public.application_status_codes(id,description,is_deleted) values (31,'Round #1 Interview No-show',false);

insert into public.application_status_codes(id,description,is_deleted) values (40,'Round #2 Interview Scheduled',false);
insert into public.application_status_codes(id,description,is_deleted) values (50,'Round #2 Interview Cleared',false);
insert into public.application_status_codes(id,description,is_deleted) values (60,'Round #2 Interview Failed',false);
insert into public.application_status_codes(id,description,is_deleted) values (61,'Round #2 Interview No-show',false);

insert into public.application_status_codes(id,description,is_deleted) values (70,'Hiring Manager Interview Scheduled',false);
insert into public.application_status_codes(id,description,is_deleted) values (80,'Hiring Manager Interview Cleared',false);
insert into public.application_status_codes(id,description,is_deleted) values (90,'Hiring Manager Interview Failed',false);
insert into public.application_status_codes(id,description,is_deleted) values (91,'Hiring Manager Interview No-show',false);

insert into public.application_status_codes(id,description,is_deleted) values (100,'HR Interview Scheduled',false);
insert into public.application_status_codes(id,description,is_deleted) values (110,'HR Interview Cleared',false);
insert into public.application_status_codes(id,description,is_deleted) values (120,'HR Interview Failed',false);
insert into public.application_status_codes(id,description,is_deleted) values (121,'HR Interview No-show',false);

insert into public.application_status_codes(id,description,is_deleted) values (130,'Offer pending to candidate',false);
insert into public.application_status_codes(id,description,is_deleted) values (140,'Offer released to candidate',false);
insert into public.application_status_codes(id,description,is_deleted) values (150,'Offer accepted by candidate',false);
insert into public.application_status_codes(id,description,is_deleted) values (160,'candidate joined the client',false);
insert into public.application_status_codes(id,description,is_deleted) values (170,'candidate was a no show',false);

