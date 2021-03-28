--
-- PostgreSQL database dump
--

-- Dumped from database version 11.5
-- Dumped by pg_dump version 11.5

-- Started on 2021-03-11 13:25:43

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

--
-- TOC entry 2 (class 3079 OID 16539)
-- Name: hstore; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS hstore WITH SCHEMA public;


--
-- TOC entry 2966 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION hstore; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION hstore IS 'data type for storing sets of (key, value) pairs';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 199 (class 1259 OID 16468)
-- Name: app; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app (
    "ID" text NOT NULL,
    "Desc" text
);


ALTER TABLE public.app OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 16510)
-- Name: cities; Type: TABLE; Schema: public; Owner: postgres
--



--
-- TOC entry 197 (class 1259 OID 16452)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id text NOT NULL,
    name text NOT NULL,
    email text,
    otp text
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 200 (class 1259 OID 16476)
-- Name: user-app; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user-app" (
    "user-id" text NOT NULL,
    "app-id" text NOT NULL
);


ALTER TABLE public."user-app" OWNER TO postgres;

--
-- TOC entry 201 (class 1259 OID 16494)
-- Name: user-app-config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user-app-config" (
    user_id text NOT NULL,
    app_id text NOT NULL,
    key text NOT NULL,
    value text,
    config public.hstore
);


ALTER TABLE public."user-app-config" OWNER TO postgres;

-- DROP TABLE public.products;

CREATE TABLE public.products
(
    id text COLLATE pg_catalog."default" NOT NULL,
    "Description" text COLLATE pg_catalog."default",
    unit_price numeric NOT NULL,
    billing_frequency smallint NOT NULL,
    status smallint NOT NULL,
    created_on timestamp with time zone,
    created_by text COLLATE pg_catalog."default",
    updated_by text COLLATE pg_catalog."default",
    currency text COLLATE pg_catalog."default" NOT NULL,
    custom_attrs public.hstore,
    updated_on timestamp with time zone
);

CREATE TABLE public.carts
(
    id text COLLATE pg_catalog."default" NOT NULL,
    "Description" text COLLATE pg_catalog."default",
    status smallint NOT NULL,
    created_on timestamp with time zone,
    created_by text COLLATE pg_catalog."default",
    updated_by text COLLATE pg_catalog."default",
    updated_on timestamp with time zone,
    custom_attrs public.hstore
);
	

--
-- TOC entry 2955 (class 0 OID 16468)
-- Dependencies: 199
-- Data for Name: app; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.app VALUES ('admin', 'Fulgorithm Admin APIs');



--
-- TOC entry 2821 (class 2606 OID 16475)
-- Name: app app_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app
    ADD CONSTRAINT app_pkey PRIMARY KEY ("ID");

--
-- TOC entry 2825 (class 2606 OID 16501)
-- Name: user-app-config user-app-config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user-app-config"
    ADD CONSTRAINT "user-app-config_pkey" PRIMARY KEY (key, app_id, user_id);


--
-- TOC entry 2823 (class 2606 OID 16483)
-- Name: user-app user-app_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user-app"
    ADD CONSTRAINT "user-app_pkey" PRIMARY KEY ("app-id", "user-id");


--
-- TOC entry 2817 (class 2606 OID 16459)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public."products"
    ADD CONSTRAINT id PRIMARY KEY (id);

ALTER TABLE ONLY public."carts"
    ADD CONSTRAINT cart_id PRIMARY KEY (id);
--
-- TOC entry 2830 (class 2606 OID 16484)
-- Name: user-app user-app_app-id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user-app"
    ADD CONSTRAINT "user-app_app-id_fkey" FOREIGN KEY ("app-id") REFERENCES public.app("ID");


--
-- TOC entry 2831 (class 2606 OID 16489)
-- Name: user-app user-app_user-id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user-app"
    ADD CONSTRAINT "user-app_user-id_fkey" FOREIGN KEY ("user-id") REFERENCES public."user"(id);

ALTER TABLE public.products
    ADD CONSTRAINT "created_by_fkey" FOREIGN KEY ("created_by") REFERENCES public."user"(id);

ALTER TABLE public.products
    ADD CONSTRAINT "updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES public."user"(id);


-- Completed on 2021-03-11 13:25:45

--
-- PostgreSQL database dump complete
--

