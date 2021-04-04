
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


CREATE TABLE public."user" (
    id text NOT NULL primary key,
    name text NOT NULL,
    email text NOT NULL,
    status smallint NOT NULL,
    otp text,
    otp_gen_time timestamp with time zone,
    last_login_time timestamp with time zone ,
    created_on timestamp with time zone,
    custom_attrs public.hstore,
    updated_on timestamp with time zone
);
ALTER TABLE public."user" OWNER TO postgres;


CREATE TABLE public.products
(
    id text COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    unit_price numeric NOT NULL,
    billing_frequency smallint NOT NULL,
    status smallint NOT NULL,
    created_on timestamp with time zone,
    created_by text COLLATE pg_catalog."default",
    updated_by text COLLATE pg_catalog."default",
    currency text COLLATE pg_catalog."default" NOT NULL,
    custom_attrs public.hstore,
    updated_on timestamp with time zone,
    primary key (id) ,
	FOREIGN KEY(created_by) REFERENCES public."user" (id),
	FOREIGN KEY(updated_by) REFERENCES public."user" (id)
);
ALTER TABLE public."products" OWNER TO postgres;

CREATE TABLE public.carts
(
    id text COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default",
    status smallint NOT NULL,
    created_on timestamp with time zone,
    created_by text COLLATE pg_catalog."default",
    updated_by text COLLATE pg_catalog."default",
    updated_on timestamp with time zone,
    custom_attrs public.hstore,
    primary key (id) ,
	FOREIGN KEY(created_by) REFERENCES public."user" (id),
	FOREIGN KEY(updated_by) REFERENCES public."user" (id)
);

ALTER TABLE public."carts" OWNER TO postgres;

CREATE TABLE public.cart_products
(
    cart_id text COLLATE pg_catalog."default" NOT NULL,
    product_id text COLLATE pg_catalog."default" NOT NULL,
    qty smallint NOT NULL,
    created_on timestamp with time zone,
    created_by text COLLATE pg_catalog."default",
    updated_by text COLLATE pg_catalog."default",
    updated_on timestamp with time zone,
    custom_attrs public.hstore,
	primary key (cart_id,product_id) ,
	FOREIGN KEY(cart_id) REFERENCES public.carts(id),
	FOREIGN KEY(product_id) REFERENCES public.products(id)
);
ALTER TABLE public."cart_products" OWNER TO postgres;





