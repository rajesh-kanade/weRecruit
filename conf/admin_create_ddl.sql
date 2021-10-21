
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

ALTER TABLE public.roles
    OWNER to postgres;


CREATE TABLE public.users
(
    email text COLLATE pg_catalog."default" NOT NULL UNIQUE,
    name text COLLATE pg_catalog."default" NOT NULL,
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

insert into public.roles(id,name,is_deleted, status) values (1,'admin',false,0);
