--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.9
-- Dumped by pg_dump version 9.1.9
-- Started on 2013-07-05 14:20:09 MSK

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 171 (class 3079 OID 11681)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

--CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 1955 (class 0 OID 0)
-- Dependencies: 171
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

--COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_with_oids = false;

--
-- TOC entry 161 (class 1259 OID 16385)
-- Dependencies: 5
-- Name: extensions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE extensions (
    id integer NOT NULL,
    package text NOT NULL
);


--
-- TOC entry 162 (class 1259 OID 16391)
-- Dependencies: 161 5
-- Name: extensions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE extensions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 1956 (class 0 OID 0)
-- Dependencies: 162
-- Name: extensions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE extensions_id_seq OWNED BY extensions.id;


--
-- TOC entry 163 (class 1259 OID 16393)
-- Dependencies: 1919 5
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE projects (
    id integer NOT NULL,
    title text NOT NULL,
    created_time timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    slug text NOT NULL
);


--
-- TOC entry 164 (class 1259 OID 16400)
-- Dependencies: 5
-- Name: projects__extensions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE projects__extensions (
    project_id integer NOT NULL,
    extension_id integer NOT NULL
);


--
-- TOC entry 165 (class 1259 OID 16403)
-- Dependencies: 5 163
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE projects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 1957 (class 0 OID 0)
-- Dependencies: 165
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE projects_id_seq OWNED BY projects.id;


--
-- TOC entry 166 (class 1259 OID 16405)
-- Dependencies: 1921 1922 5
-- Name: tests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE tests (
    id integer NOT NULL,
    data bytea NOT NULL,
    comment text DEFAULT ''::text NOT NULL,
    script text DEFAULT ''::text NOT NULL,
    project_id integer NOT NULL,
    start_time timestamp without time zone NOT NULL,
    finish_time timestamp without time zone
);


--
-- TOC entry 167 (class 1259 OID 16413)
-- Dependencies: 166 5
-- Name: tests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE tests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 1958 (class 0 OID 0)
-- Dependencies: 167
-- Name: tests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE tests_id_seq OWNED BY tests.id;


--
-- TOC entry 168 (class 1259 OID 16415)
-- Dependencies: 1924 5
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE users (
    id integer NOT NULL,
    name text NOT NULL,
    password text NOT NULL,
    created_time timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    "group" text NOT NULL
);


--
-- TOC entry 169 (class 1259 OID 16422)
-- Dependencies: 5
-- Name: users__projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE users__projects (
    user_id integer NOT NULL,
    project_id integer NOT NULL
);


--
-- TOC entry 170 (class 1259 OID 16425)
-- Dependencies: 5 168
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 1959 (class 0 OID 0)
-- Dependencies: 170
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- TOC entry 1918 (class 2604 OID 16427)
-- Dependencies: 162 161
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY extensions ALTER COLUMN id SET DEFAULT nextval('extensions_id_seq'::regclass);


--
-- TOC entry 1920 (class 2604 OID 16428)
-- Dependencies: 165 163
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects ALTER COLUMN id SET DEFAULT nextval('projects_id_seq'::regclass);


--
-- TOC entry 1923 (class 2604 OID 16429)
-- Dependencies: 167 166
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests ALTER COLUMN id SET DEFAULT nextval('tests_id_seq'::regclass);


--
-- TOC entry 1925 (class 2604 OID 16430)
-- Dependencies: 170 168
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- TOC entry 1927 (class 2606 OID 16644)
-- Dependencies: 161 161 1950
-- Name: extensions_package_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY extensions
    ADD CONSTRAINT extensions_package_key UNIQUE (package);


--
-- TOC entry 1929 (class 2606 OID 16646)
-- Dependencies: 161 161 1950
-- Name: extensions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY extensions
    ADD CONSTRAINT extensions_pkey PRIMARY KEY (id);


--
-- TOC entry 1935 (class 2606 OID 16648)
-- Dependencies: 164 164 164 1950
-- Name: projects__extensions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects__extensions
    ADD CONSTRAINT projects__extensions_pkey PRIMARY KEY (project_id, extension_id);


--
-- TOC entry 1931 (class 2606 OID 16650)
-- Dependencies: 163 163 1950
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- TOC entry 1933 (class 2606 OID 16759)
-- Dependencies: 163 163 1950
-- Name: projects_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_slug_key UNIQUE (slug);


--
-- TOC entry 1937 (class 2606 OID 16652)
-- Dependencies: 166 166 1950
-- Name: tests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests
    ADD CONSTRAINT tests_pkey PRIMARY KEY (id);


--
-- TOC entry 1943 (class 2606 OID 16654)
-- Dependencies: 169 169 169 1950
-- Name: users__projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY users__projects
    ADD CONSTRAINT users__projects_pkey PRIMARY KEY (user_id, project_id);


--
-- TOC entry 1939 (class 2606 OID 16656)
-- Dependencies: 168 168 1950
-- Name: users_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_name_key UNIQUE (name);


--
-- TOC entry 1941 (class 2606 OID 16658)
-- Dependencies: 168 168 1950
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 1944 (class 2606 OID 16659)
-- Dependencies: 164 1928 161 1950
-- Name: projects__extensions_extension_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects__extensions
    ADD CONSTRAINT projects__extensions_extension_id_fkey FOREIGN KEY (extension_id) REFERENCES extensions(id);


--
-- TOC entry 1945 (class 2606 OID 16664)
-- Dependencies: 164 163 1930 1950
-- Name: projects__extensions_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY projects__extensions
    ADD CONSTRAINT projects__extensions_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id);


--
-- TOC entry 1946 (class 2606 OID 16669)
-- Dependencies: 163 166 1930 1950
-- Name: tests_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY tests
    ADD CONSTRAINT tests_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id);


--
-- TOC entry 1947 (class 2606 OID 16674)
-- Dependencies: 1930 163 169 1950
-- Name: users__projects_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY users__projects
    ADD CONSTRAINT users__projects_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id);


--
-- TOC entry 1948 (class 2606 OID 16679)
-- Dependencies: 168 169 1940 1950
-- Name: users__projects_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY users__projects
    ADD CONSTRAINT users__projects_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


-- Completed on 2013-07-05 14:20:09 MSK

--
-- PostgreSQL database dump complete
--

