--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

-- Started on 2026-01-02 19:40:24

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
-- TOC entry 2 (class 3079 OID 16622)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5245 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 16472)
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    id integer NOT NULL,
    client_id integer NOT NULL,
    account_number character varying NOT NULL,
    account_type character varying,
    currency character varying NOT NULL,
    status character varying NOT NULL,
    opened_at character varying,
    closed_at character varying
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16471)
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accounts_id_seq OWNER TO postgres;

--
-- TOC entry 5246 (class 0 OID 0)
-- Dependencies: 220
-- Name: accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;


--
-- TOC entry 229 (class 1259 OID 16563)
-- Name: asset_class; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asset_class (
    asset_class_id integer NOT NULL,
    asset_code character varying(20) NOT NULL,
    asset_name character varying(100) NOT NULL
);


ALTER TABLE public.asset_class OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16562)
-- Name: asset_class_asset_class_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asset_class_asset_class_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asset_class_asset_class_id_seq OWNER TO postgres;

--
-- TOC entry 5247 (class 0 OID 0)
-- Dependencies: 228
-- Name: asset_class_asset_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asset_class_asset_class_id_seq OWNED BY public.asset_class.asset_class_id;


--
-- TOC entry 253 (class 1259 OID 16844)
-- Name: attribute_conflicts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attribute_conflicts (
    conflict_id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id integer NOT NULL,
    attribute_id integer NOT NULL,
    detected_at timestamp with time zone DEFAULT now() NOT NULL,
    values_by_source jsonb NOT NULL,
    resolved boolean DEFAULT false NOT NULL,
    resolution_notes text,
    resolved_at timestamp with time zone
);


ALTER TABLE public.attribute_conflicts OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 16727)
-- Name: attribute_dictionary; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attribute_dictionary (
    attribute_id integer NOT NULL,
    canonical_name character varying(100) NOT NULL,
    data_type character varying(30) NOT NULL,
    is_mandatory boolean DEFAULT false NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.attribute_dictionary OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 16726)
-- Name: attribute_dictionary_attribute_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attribute_dictionary_attribute_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attribute_dictionary_attribute_id_seq OWNER TO postgres;

--
-- TOC entry 5248 (class 0 OID 0)
-- Dependencies: 243
-- Name: attribute_dictionary_attribute_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attribute_dictionary_attribute_id_seq OWNED BY public.attribute_dictionary.attribute_id;


--
-- TOC entry 252 (class 1259 OID 16824)
-- Name: attribute_precedence_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attribute_precedence_rules (
    precedence_rule_id integer NOT NULL,
    attribute_id integer NOT NULL,
    source_system_id integer NOT NULL,
    precedence_rank integer NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.attribute_precedence_rules OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 16823)
-- Name: attribute_precedence_rules_precedence_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attribute_precedence_rules_precedence_rule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attribute_precedence_rules_precedence_rule_id_seq OWNER TO postgres;

--
-- TOC entry 5249 (class 0 OID 0)
-- Dependencies: 251
-- Name: attribute_precedence_rules_precedence_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attribute_precedence_rules_precedence_rule_id_seq OWNED BY public.attribute_precedence_rules.precedence_rule_id;


--
-- TOC entry 259 (class 1259 OID 16955)
-- Name: audit_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_events (
    audit_event_id uuid DEFAULT gen_random_uuid() NOT NULL,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    actor character varying(200) NOT NULL,
    event_type character varying(80) NOT NULL,
    client_id integer,
    source_record_id uuid,
    evidence_bundle_id uuid,
    details jsonb
);


ALTER TABLE public.audit_events OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 16807)
-- Name: client_cluster_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_cluster_members (
    cluster_id uuid NOT NULL,
    client_id integer NOT NULL,
    role character varying(30) DEFAULT 'member'::character varying NOT NULL
);


ALTER TABLE public.client_cluster_members OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 16798)
-- Name: client_clusters; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_clusters (
    cluster_id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    rationale text
);


ALTER TABLE public.client_clusters OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16594)
-- Name: client_data_lineage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_data_lineage (
    lineage_id integer NOT NULL,
    client_id integer NOT NULL,
    data_source character varying(100) NOT NULL,
    field_name character varying(100) NOT NULL,
    transformation_description text,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.client_data_lineage OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16593)
-- Name: client_data_lineage_lineage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.client_data_lineage_lineage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.client_data_lineage_lineage_id_seq OWNER TO postgres;

--
-- TOC entry 5250 (class 0 OID 0)
-- Dependencies: 232
-- Name: client_data_lineage_lineage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.client_data_lineage_lineage_id_seq OWNED BY public.client_data_lineage.lineage_id;


--
-- TOC entry 255 (class 1259 OID 16881)
-- Name: client_operational_state; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_operational_state (
    state_id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id integer NOT NULL,
    as_of timestamp with time zone DEFAULT now() NOT NULL,
    processing_stage character varying(50) NOT NULL,
    status character varying(30) NOT NULL,
    message text,
    details jsonb
);


ALTER TABLE public.client_operational_state OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 16865)
-- Name: client_regulatory_enrichment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_regulatory_enrichment (
    enrichment_id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id integer NOT NULL,
    fatca_status character varying(50),
    crs_status character varying(50),
    onboarding_status character varying(50),
    kyc_overall_status character varying(50),
    derived_risk_notes text,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.client_regulatory_enrichment OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 16896)
-- Name: client_source_coverage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_source_coverage (
    client_id integer NOT NULL,
    source_system_id integer NOT NULL,
    last_seen_at timestamp with time zone,
    is_missing boolean DEFAULT false NOT NULL,
    is_stale boolean DEFAULT false NOT NULL,
    notes text
);


ALTER TABLE public.client_source_coverage OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16461)
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    id integer NOT NULL,
    external_id character varying,
    full_name character varying NOT NULL,
    email character varying,
    phone character varying,
    primary_address character varying,
    country character varying,
    tax_id character varying,
    segment character varying,
    risk_rating character varying,
    country_id integer,
    risk_rating_id integer
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16460)
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clients_id_seq OWNER TO postgres;

--
-- TOC entry 5251 (class 0 OID 0)
-- Dependencies: 218
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- TOC entry 227 (class 1259 OID 16530)
-- Name: corporate_kyc_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.corporate_kyc_info (
    corporate_kyc_id integer NOT NULL,
    client_id integer NOT NULL,
    registration_number character varying(100) NOT NULL,
    legal_name character varying(255) NOT NULL,
    business_license character varying(100),
    company_structure character varying(50),
    compliance_status character varying(50) NOT NULL,
    last_reviewed_at timestamp without time zone,
    next_review_due_at timestamp without time zone,
    notes text
);


ALTER TABLE public.corporate_kyc_info OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16529)
-- Name: corporate_kyc_info_corporate_kyc_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.corporate_kyc_info_corporate_kyc_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.corporate_kyc_info_corporate_kyc_id_seq OWNER TO postgres;

--
-- TOC entry 5252 (class 0 OID 0)
-- Dependencies: 226
-- Name: corporate_kyc_info_corporate_kyc_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.corporate_kyc_info_corporate_kyc_id_seq OWNED BY public.corporate_kyc_info.corporate_kyc_id;


--
-- TOC entry 231 (class 1259 OID 16577)
-- Name: corporate_trade_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.corporate_trade_history (
    trade_id integer NOT NULL,
    client_id integer NOT NULL,
    trade_date timestamp without time zone NOT NULL,
    asset_class_id integer NOT NULL,
    instrument character varying(100) NOT NULL,
    direction character varying(4) NOT NULL,
    quantity numeric(18,4) NOT NULL,
    price numeric(18,6) NOT NULL,
    pnl numeric(18,2) NOT NULL
);


ALTER TABLE public.corporate_trade_history OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16576)
-- Name: corporate_trade_history_trade_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.corporate_trade_history_trade_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.corporate_trade_history_trade_id_seq OWNER TO postgres;

--
-- TOC entry 5253 (class 0 OID 0)
-- Dependencies: 230
-- Name: corporate_trade_history_trade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.corporate_trade_history_trade_id_seq OWNED BY public.corporate_trade_history.trade_id;


--
-- TOC entry 235 (class 1259 OID 16609)
-- Name: country; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.country (
    country_id integer NOT NULL,
    country_code character varying(3) NOT NULL,
    country_name character varying(100) NOT NULL
);


ALTER TABLE public.country OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 16608)
-- Name: country_country_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.country_country_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.country_country_id_seq OWNER TO postgres;

--
-- TOC entry 5254 (class 0 OID 0)
-- Dependencies: 234
-- Name: country_country_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.country_country_id_seq OWNED BY public.country.country_id;


--
-- TOC entry 262 (class 1259 OID 17009)
-- Name: crm_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crm_contacts (
    id uuid NOT NULL,
    source_system character varying NOT NULL,
    source_record_id character varying NOT NULL,
    first_name character varying,
    last_name character varying,
    email character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.crm_contacts OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 16940)
-- Name: evidence_artefacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evidence_artefacts (
    artefact_id uuid DEFAULT gen_random_uuid() NOT NULL,
    evidence_bundle_id uuid NOT NULL,
    artefact_type character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    content jsonb,
    storage_ref text,
    content_hash character varying(128)
);


ALTER TABLE public.evidence_artefacts OWNER TO postgres;

--
-- TOC entry 257 (class 1259 OID 16915)
-- Name: evidence_bundles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evidence_bundles (
    evidence_bundle_id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id integer,
    ingestion_run_id uuid,
    match_run_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    bundle_type character varying(50) NOT NULL,
    summary text
);


ALTER TABLE public.evidence_bundles OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 16672)
-- Name: ingestion_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ingestion_runs (
    ingestion_run_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_system_id integer NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    status character varying(30) DEFAULT 'started'::character varying NOT NULL,
    schema_version character varying(50),
    triggered_by character varying(200),
    notes text
);


ALTER TABLE public.ingestion_runs OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16489)
-- Name: kyc_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kyc_flags (
    id integer NOT NULL,
    client_id integer NOT NULL,
    code character varying NOT NULL,
    description character varying,
    status character varying NOT NULL,
    created_at character varying,
    resolved_at character varying
);


ALTER TABLE public.kyc_flags OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16488)
-- Name: kyc_flags_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kyc_flags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kyc_flags_id_seq OWNER TO postgres;

--
-- TOC entry 5255 (class 0 OID 0)
-- Dependencies: 222
-- Name: kyc_flags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kyc_flags_id_seq OWNED BY public.kyc_flags.id;


--
-- TOC entry 248 (class 1259 OID 16772)
-- Name: match_decisions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.match_decisions (
    match_decision_id uuid DEFAULT gen_random_uuid() NOT NULL,
    match_run_id uuid NOT NULL,
    source_record_id uuid NOT NULL,
    decided_at timestamp with time zone DEFAULT now() NOT NULL,
    decision character varying(30) NOT NULL,
    matched_client_id integer,
    confidence numeric(5,4),
    rule_hits jsonb,
    conflict_summary jsonb
);


ALTER TABLE public.match_decisions OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 16762)
-- Name: match_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.match_runs (
    match_run_id uuid DEFAULT gen_random_uuid() NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    status character varying(30) DEFAULT 'started'::character varying NOT NULL,
    ruleset_version character varying(50),
    notes text
);


ALTER TABLE public.match_runs OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16616)
-- Name: risk_rating; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.risk_rating (
    risk_rating_id integer NOT NULL,
    rating_code character varying(20) NOT NULL,
    description character varying(255) NOT NULL
);


ALTER TABLE public.risk_rating OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16615)
-- Name: risk_rating_risk_rating_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.risk_rating_risk_rating_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.risk_rating_risk_rating_id_seq OWNER TO postgres;

--
-- TOC entry 5256 (class 0 OID 0)
-- Dependencies: 236
-- Name: risk_rating_risk_rating_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.risk_rating_risk_rating_id_seq OWNED BY public.risk_rating.risk_rating_id;


--
-- TOC entry 261 (class 1259 OID 16990)
-- Name: service_error_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_error_logs (
    error_log_id uuid DEFAULT gen_random_uuid() NOT NULL,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    service_name character varying(100) NOT NULL,
    severity character varying(20) NOT NULL,
    error_code character varying(50),
    message text NOT NULL,
    details jsonb,
    correlation_id character varying(100)
);


ALTER TABLE public.service_error_logs OWNER TO postgres;

--
-- TOC entry 260 (class 1259 OID 16980)
-- Name: service_health_checks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_health_checks (
    health_check_id uuid DEFAULT gen_random_uuid() NOT NULL,
    checked_at timestamp with time zone DEFAULT now() NOT NULL,
    service_name character varying(100) NOT NULL,
    check_type character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    details jsonb
);


ALTER TABLE public.service_health_checks OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 16740)
-- Name: source_field_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.source_field_mappings (
    mapping_id integer NOT NULL,
    source_system_id integer NOT NULL,
    source_field character varying(200) NOT NULL,
    attribute_id integer NOT NULL,
    transform_rule text,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.source_field_mappings OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 16739)
-- Name: source_field_mappings_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.source_field_mappings_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.source_field_mappings_mapping_id_seq OWNER TO postgres;

--
-- TOC entry 5257 (class 0 OID 0)
-- Dependencies: 245
-- Name: source_field_mappings_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.source_field_mappings_mapping_id_seq OWNED BY public.source_field_mappings.mapping_id;


--
-- TOC entry 241 (class 1259 OID 16688)
-- Name: source_records_raw; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.source_records_raw (
    source_record_id uuid DEFAULT gen_random_uuid() NOT NULL,
    ingestion_run_id uuid NOT NULL,
    source_system_id integer NOT NULL,
    source_record_key character varying(200) NOT NULL,
    received_at timestamp with time zone DEFAULT now() NOT NULL,
    payload jsonb NOT NULL,
    payload_hash character varying(128),
    extracted_external_id character varying(200),
    extracted_email character varying(320),
    extracted_tax_id character varying(100),
    structural_ok boolean DEFAULT true NOT NULL,
    structural_errors jsonb
);


ALTER TABLE public.source_records_raw OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16660)
-- Name: source_systems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.source_systems (
    source_system_id integer NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.source_systems OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 16659)
-- Name: source_systems_source_system_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.source_systems_source_system_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.source_systems_source_system_id_seq OWNER TO postgres;

--
-- TOC entry 5258 (class 0 OID 0)
-- Dependencies: 238
-- Name: source_systems_source_system_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.source_systems_source_system_id_seq OWNED BY public.source_systems.source_system_id;


--
-- TOC entry 225 (class 1259 OID 16505)
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    account_id integer NOT NULL,
    trade_date character varying,
    value_date character varying,
    amount double precision NOT NULL,
    currency character varying NOT NULL,
    txn_type character varying NOT NULL,
    description character varying,
    price double precision,
    pnl double precision
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16504)
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transactions_id_seq OWNER TO postgres;

--
-- TOC entry 5259 (class 0 OID 0)
-- Dependencies: 224
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- TOC entry 242 (class 1259 OID 16710)
-- Name: validation_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.validation_results (
    validation_result_id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_record_id uuid NOT NULL,
    validated_at timestamp with time zone DEFAULT now() NOT NULL,
    validation_type character varying(50) NOT NULL,
    passed boolean NOT NULL,
    details jsonb,
    error_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.validation_results OWNER TO postgres;

--
-- TOC entry 4908 (class 2604 OID 16475)
-- Name: accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);


--
-- TOC entry 4912 (class 2604 OID 16566)
-- Name: asset_class asset_class_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_class ALTER COLUMN asset_class_id SET DEFAULT nextval('public.asset_class_asset_class_id_seq'::regclass);


--
-- TOC entry 4930 (class 2604 OID 16730)
-- Name: attribute_dictionary attribute_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_dictionary ALTER COLUMN attribute_id SET DEFAULT nextval('public.attribute_dictionary_attribute_id_seq'::regclass);


--
-- TOC entry 4943 (class 2604 OID 16827)
-- Name: attribute_precedence_rules precedence_rule_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_precedence_rules ALTER COLUMN precedence_rule_id SET DEFAULT nextval('public.attribute_precedence_rules_precedence_rule_id_seq'::regclass);


--
-- TOC entry 4914 (class 2604 OID 16597)
-- Name: client_data_lineage lineage_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_data_lineage ALTER COLUMN lineage_id SET DEFAULT nextval('public.client_data_lineage_lineage_id_seq'::regclass);


--
-- TOC entry 4907 (class 2604 OID 16464)
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- TOC entry 4911 (class 2604 OID 16533)
-- Name: corporate_kyc_info corporate_kyc_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.corporate_kyc_info ALTER COLUMN corporate_kyc_id SET DEFAULT nextval('public.corporate_kyc_info_corporate_kyc_id_seq'::regclass);


--
-- TOC entry 4913 (class 2604 OID 16580)
-- Name: corporate_trade_history trade_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.corporate_trade_history ALTER COLUMN trade_id SET DEFAULT nextval('public.corporate_trade_history_trade_id_seq'::regclass);


--
-- TOC entry 4916 (class 2604 OID 16612)
-- Name: country country_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.country ALTER COLUMN country_id SET DEFAULT nextval('public.country_country_id_seq'::regclass);


--
-- TOC entry 4909 (class 2604 OID 16492)
-- Name: kyc_flags id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kyc_flags ALTER COLUMN id SET DEFAULT nextval('public.kyc_flags_id_seq'::regclass);


--
-- TOC entry 4917 (class 2604 OID 16619)
-- Name: risk_rating risk_rating_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_rating ALTER COLUMN risk_rating_id SET DEFAULT nextval('public.risk_rating_risk_rating_id_seq'::regclass);


--
-- TOC entry 4933 (class 2604 OID 16743)
-- Name: source_field_mappings mapping_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_field_mappings ALTER COLUMN mapping_id SET DEFAULT nextval('public.source_field_mappings_mapping_id_seq'::regclass);


--
-- TOC entry 4918 (class 2604 OID 16663)
-- Name: source_systems source_system_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_systems ALTER COLUMN source_system_id SET DEFAULT nextval('public.source_systems_source_system_id_seq'::regclass);


--
-- TOC entry 4910 (class 2604 OID 16508)
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- TOC entry 4971 (class 2606 OID 16479)
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- TOC entry 4986 (class 2606 OID 16568)
-- Name: asset_class asset_class_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_class
    ADD CONSTRAINT asset_class_pkey PRIMARY KEY (asset_class_id);


--
-- TOC entry 5034 (class 2606 OID 16853)
-- Name: attribute_conflicts attribute_conflicts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_conflicts
    ADD CONSTRAINT attribute_conflicts_pkey PRIMARY KEY (conflict_id);


--
-- TOC entry 5010 (class 2606 OID 16738)
-- Name: attribute_dictionary attribute_dictionary_canonical_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_dictionary
    ADD CONSTRAINT attribute_dictionary_canonical_name_key UNIQUE (canonical_name);


--
-- TOC entry 5012 (class 2606 OID 16736)
-- Name: attribute_dictionary attribute_dictionary_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_dictionary
    ADD CONSTRAINT attribute_dictionary_pkey PRIMARY KEY (attribute_id);


--
-- TOC entry 5029 (class 2606 OID 16832)
-- Name: attribute_precedence_rules attribute_precedence_rules_attribute_id_source_system_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_precedence_rules
    ADD CONSTRAINT attribute_precedence_rules_attribute_id_source_system_id_key UNIQUE (attribute_id, source_system_id);


--
-- TOC entry 5031 (class 2606 OID 16830)
-- Name: attribute_precedence_rules attribute_precedence_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_precedence_rules
    ADD CONSTRAINT attribute_precedence_rules_pkey PRIMARY KEY (precedence_rule_id);


--
-- TOC entry 5052 (class 2606 OID 16963)
-- Name: audit_events audit_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_pkey PRIMARY KEY (audit_event_id);


--
-- TOC entry 5027 (class 2606 OID 16812)
-- Name: client_cluster_members client_cluster_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_cluster_members
    ADD CONSTRAINT client_cluster_members_pkey PRIMARY KEY (cluster_id, client_id);


--
-- TOC entry 5025 (class 2606 OID 16806)
-- Name: client_clusters client_clusters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_clusters
    ADD CONSTRAINT client_clusters_pkey PRIMARY KEY (cluster_id);


--
-- TOC entry 4990 (class 2606 OID 16602)
-- Name: client_data_lineage client_data_lineage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_data_lineage
    ADD CONSTRAINT client_data_lineage_pkey PRIMARY KEY (lineage_id);


--
-- TOC entry 5041 (class 2606 OID 16889)
-- Name: client_operational_state client_operational_state_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_operational_state
    ADD CONSTRAINT client_operational_state_pkey PRIMARY KEY (state_id);


--
-- TOC entry 5037 (class 2606 OID 16875)
-- Name: client_regulatory_enrichment client_regulatory_enrichment_client_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_regulatory_enrichment
    ADD CONSTRAINT client_regulatory_enrichment_client_id_key UNIQUE (client_id);


--
-- TOC entry 5039 (class 2606 OID 16873)
-- Name: client_regulatory_enrichment client_regulatory_enrichment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_regulatory_enrichment
    ADD CONSTRAINT client_regulatory_enrichment_pkey PRIMARY KEY (enrichment_id);


--
-- TOC entry 5044 (class 2606 OID 16904)
-- Name: client_source_coverage client_source_coverage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_source_coverage
    ADD CONSTRAINT client_source_coverage_pkey PRIMARY KEY (client_id, source_system_id);


--
-- TOC entry 4967 (class 2606 OID 16468)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- TOC entry 4984 (class 2606 OID 16537)
-- Name: corporate_kyc_info corporate_kyc_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.corporate_kyc_info
    ADD CONSTRAINT corporate_kyc_info_pkey PRIMARY KEY (corporate_kyc_id);


--
-- TOC entry 4988 (class 2606 OID 16582)
-- Name: corporate_trade_history corporate_trade_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.corporate_trade_history
    ADD CONSTRAINT corporate_trade_history_pkey PRIMARY KEY (trade_id);


--
-- TOC entry 4992 (class 2606 OID 16614)
-- Name: country country_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.country
    ADD CONSTRAINT country_pkey PRIMARY KEY (country_id);


--
-- TOC entry 5061 (class 2606 OID 17017)
-- Name: crm_contacts crm_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crm_contacts
    ADD CONSTRAINT crm_contacts_pkey PRIMARY KEY (id);


--
-- TOC entry 5049 (class 2606 OID 16948)
-- Name: evidence_artefacts evidence_artefacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_artefacts
    ADD CONSTRAINT evidence_artefacts_pkey PRIMARY KEY (artefact_id);


--
-- TOC entry 5046 (class 2606 OID 16923)
-- Name: evidence_bundles evidence_bundles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_bundles
    ADD CONSTRAINT evidence_bundles_pkey PRIMARY KEY (evidence_bundle_id);


--
-- TOC entry 5000 (class 2606 OID 16681)
-- Name: ingestion_runs ingestion_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingestion_runs
    ADD CONSTRAINT ingestion_runs_pkey PRIMARY KEY (ingestion_run_id);


--
-- TOC entry 4978 (class 2606 OID 16496)
-- Name: kyc_flags kyc_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kyc_flags
    ADD CONSTRAINT kyc_flags_pkey PRIMARY KEY (id);


--
-- TOC entry 5023 (class 2606 OID 16780)
-- Name: match_decisions match_decisions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_decisions
    ADD CONSTRAINT match_decisions_pkey PRIMARY KEY (match_decision_id);


--
-- TOC entry 5019 (class 2606 OID 16771)
-- Name: match_runs match_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_runs
    ADD CONSTRAINT match_runs_pkey PRIMARY KEY (match_run_id);


--
-- TOC entry 4994 (class 2606 OID 16621)
-- Name: risk_rating risk_rating_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_rating
    ADD CONSTRAINT risk_rating_pkey PRIMARY KEY (risk_rating_id);


--
-- TOC entry 5059 (class 2606 OID 16998)
-- Name: service_error_logs service_error_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_error_logs
    ADD CONSTRAINT service_error_logs_pkey PRIMARY KEY (error_log_id);


--
-- TOC entry 5056 (class 2606 OID 16988)
-- Name: service_health_checks service_health_checks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_health_checks
    ADD CONSTRAINT service_health_checks_pkey PRIMARY KEY (health_check_id);


--
-- TOC entry 5015 (class 2606 OID 16748)
-- Name: source_field_mappings source_field_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_field_mappings
    ADD CONSTRAINT source_field_mappings_pkey PRIMARY KEY (mapping_id);


--
-- TOC entry 5017 (class 2606 OID 16750)
-- Name: source_field_mappings source_field_mappings_source_system_id_source_field_attribu_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_field_mappings
    ADD CONSTRAINT source_field_mappings_source_system_id_source_field_attribu_key UNIQUE (source_system_id, source_field, attribute_id);


--
-- TOC entry 5005 (class 2606 OID 16697)
-- Name: source_records_raw source_records_raw_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_records_raw
    ADD CONSTRAINT source_records_raw_pkey PRIMARY KEY (source_record_id);


--
-- TOC entry 4996 (class 2606 OID 16671)
-- Name: source_systems source_systems_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_systems
    ADD CONSTRAINT source_systems_code_key UNIQUE (code);


--
-- TOC entry 4998 (class 2606 OID 16669)
-- Name: source_systems source_systems_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_systems
    ADD CONSTRAINT source_systems_pkey PRIMARY KEY (source_system_id);


--
-- TOC entry 4982 (class 2606 OID 16512)
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- TOC entry 5063 (class 2606 OID 17019)
-- Name: crm_contacts uq_crm_contacts_source_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crm_contacts
    ADD CONSTRAINT uq_crm_contacts_source_key UNIQUE (source_system, source_record_id);


--
-- TOC entry 5008 (class 2606 OID 16719)
-- Name: validation_results validation_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validation_results
    ADD CONSTRAINT validation_results_pkey PRIMARY KEY (validation_result_id);


--
-- TOC entry 4972 (class 1259 OID 16485)
-- Name: ix_accounts_account_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_accounts_account_number ON public.accounts USING btree (account_number);


--
-- TOC entry 4973 (class 1259 OID 16487)
-- Name: ix_accounts_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accounts_client_id ON public.accounts USING btree (client_id);


--
-- TOC entry 4974 (class 1259 OID 16486)
-- Name: ix_accounts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accounts_id ON public.accounts USING btree (id);


--
-- TOC entry 5035 (class 1259 OID 16864)
-- Name: ix_attribute_conflicts_client; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attribute_conflicts_client ON public.attribute_conflicts USING btree (client_id, resolved);


--
-- TOC entry 5032 (class 1259 OID 16843)
-- Name: ix_attribute_precedence_attr; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attribute_precedence_attr ON public.attribute_precedence_rules USING btree (attribute_id, precedence_rank);


--
-- TOC entry 5053 (class 1259 OID 16979)
-- Name: ix_audit_events_client_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_events_client_time ON public.audit_events USING btree (client_id, occurred_at DESC);


--
-- TOC entry 5042 (class 1259 OID 16895)
-- Name: ix_client_operational_state_client_asof; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_client_operational_state_client_asof ON public.client_operational_state USING btree (client_id, as_of DESC);


--
-- TOC entry 4968 (class 1259 OID 16470)
-- Name: ix_clients_external_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_clients_external_id ON public.clients USING btree (external_id);


--
-- TOC entry 4969 (class 1259 OID 16469)
-- Name: ix_clients_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_clients_id ON public.clients USING btree (id);


--
-- TOC entry 5050 (class 1259 OID 16954)
-- Name: ix_evidence_artefacts_bundle; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_evidence_artefacts_bundle ON public.evidence_artefacts USING btree (evidence_bundle_id);


--
-- TOC entry 5047 (class 1259 OID 16939)
-- Name: ix_evidence_bundles_client_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_evidence_bundles_client_created ON public.evidence_bundles USING btree (client_id, created_at DESC);


--
-- TOC entry 5001 (class 1259 OID 16687)
-- Name: ix_ingestion_runs_source_started; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ingestion_runs_source_started ON public.ingestion_runs USING btree (source_system_id, started_at DESC);


--
-- TOC entry 4975 (class 1259 OID 16503)
-- Name: ix_kyc_flags_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kyc_flags_client_id ON public.kyc_flags USING btree (client_id);


--
-- TOC entry 4976 (class 1259 OID 16502)
-- Name: ix_kyc_flags_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kyc_flags_id ON public.kyc_flags USING btree (id);


--
-- TOC entry 5020 (class 1259 OID 16797)
-- Name: ix_match_decisions_client; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_match_decisions_client ON public.match_decisions USING btree (matched_client_id);


--
-- TOC entry 5021 (class 1259 OID 16796)
-- Name: ix_match_decisions_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_match_decisions_run ON public.match_decisions USING btree (match_run_id);


--
-- TOC entry 5057 (class 1259 OID 16999)
-- Name: ix_service_error_logs_service_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_error_logs_service_time ON public.service_error_logs USING btree (service_name, occurred_at DESC);


--
-- TOC entry 5054 (class 1259 OID 16989)
-- Name: ix_service_health_checks_service_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_service_health_checks_service_time ON public.service_health_checks USING btree (service_name, checked_at DESC);


--
-- TOC entry 5013 (class 1259 OID 16761)
-- Name: ix_source_field_mappings_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_source_field_mappings_system ON public.source_field_mappings USING btree (source_system_id);


--
-- TOC entry 5002 (class 1259 OID 16708)
-- Name: ix_source_records_raw_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_source_records_raw_run ON public.source_records_raw USING btree (ingestion_run_id);


--
-- TOC entry 5003 (class 1259 OID 16709)
-- Name: ix_source_records_raw_system_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_source_records_raw_system_key ON public.source_records_raw USING btree (source_system_id, source_record_key);


--
-- TOC entry 4979 (class 1259 OID 16519)
-- Name: ix_transactions_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_account_id ON public.transactions USING btree (account_id);


--
-- TOC entry 4980 (class 1259 OID 16518)
-- Name: ix_transactions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_id ON public.transactions USING btree (id);


--
-- TOC entry 5006 (class 1259 OID 16725)
-- Name: ix_validation_results_record; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_validation_results_record ON public.validation_results USING btree (source_record_id);


--
-- TOC entry 5064 (class 2606 OID 16480)
-- Name: accounts accounts_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 5084 (class 2606 OID 16859)
-- Name: attribute_conflicts attribute_conflicts_attribute_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_conflicts
    ADD CONSTRAINT attribute_conflicts_attribute_id_fkey FOREIGN KEY (attribute_id) REFERENCES public.attribute_dictionary(attribute_id);


--
-- TOC entry 5085 (class 2606 OID 16854)
-- Name: attribute_conflicts attribute_conflicts_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_conflicts
    ADD CONSTRAINT attribute_conflicts_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5082 (class 2606 OID 16833)
-- Name: attribute_precedence_rules attribute_precedence_rules_attribute_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_precedence_rules
    ADD CONSTRAINT attribute_precedence_rules_attribute_id_fkey FOREIGN KEY (attribute_id) REFERENCES public.attribute_dictionary(attribute_id);


--
-- TOC entry 5083 (class 2606 OID 16838)
-- Name: attribute_precedence_rules attribute_precedence_rules_source_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attribute_precedence_rules
    ADD CONSTRAINT attribute_precedence_rules_source_system_id_fkey FOREIGN KEY (source_system_id) REFERENCES public.source_systems(source_system_id);


--
-- TOC entry 5094 (class 2606 OID 16964)
-- Name: audit_events audit_events_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE SET NULL;


--
-- TOC entry 5095 (class 2606 OID 16974)
-- Name: audit_events audit_events_evidence_bundle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_evidence_bundle_id_fkey FOREIGN KEY (evidence_bundle_id) REFERENCES public.evidence_bundles(evidence_bundle_id) ON DELETE SET NULL;


--
-- TOC entry 5096 (class 2606 OID 16969)
-- Name: audit_events audit_events_source_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_events
    ADD CONSTRAINT audit_events_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES public.source_records_raw(source_record_id) ON DELETE SET NULL;


--
-- TOC entry 5080 (class 2606 OID 16818)
-- Name: client_cluster_members client_cluster_members_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_cluster_members
    ADD CONSTRAINT client_cluster_members_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5081 (class 2606 OID 16813)
-- Name: client_cluster_members client_cluster_members_cluster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_cluster_members
    ADD CONSTRAINT client_cluster_members_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES public.client_clusters(cluster_id) ON DELETE CASCADE;


--
-- TOC entry 5070 (class 2606 OID 16603)
-- Name: client_data_lineage client_data_lineage_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_data_lineage
    ADD CONSTRAINT client_data_lineage_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5087 (class 2606 OID 16890)
-- Name: client_operational_state client_operational_state_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_operational_state
    ADD CONSTRAINT client_operational_state_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5086 (class 2606 OID 16876)
-- Name: client_regulatory_enrichment client_regulatory_enrichment_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_regulatory_enrichment
    ADD CONSTRAINT client_regulatory_enrichment_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5088 (class 2606 OID 16905)
-- Name: client_source_coverage client_source_coverage_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_source_coverage
    ADD CONSTRAINT client_source_coverage_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5089 (class 2606 OID 16910)
-- Name: client_source_coverage client_source_coverage_source_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_source_coverage
    ADD CONSTRAINT client_source_coverage_source_system_id_fkey FOREIGN KEY (source_system_id) REFERENCES public.source_systems(source_system_id);


--
-- TOC entry 5067 (class 2606 OID 16538)
-- Name: corporate_kyc_info corporate_kyc_info_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.corporate_kyc_info
    ADD CONSTRAINT corporate_kyc_info_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 5068 (class 2606 OID 16588)
-- Name: corporate_trade_history corporate_trade_history_asset_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.corporate_trade_history
    ADD CONSTRAINT corporate_trade_history_asset_class_id_fkey FOREIGN KEY (asset_class_id) REFERENCES public.asset_class(asset_class_id);


--
-- TOC entry 5069 (class 2606 OID 16583)
-- Name: corporate_trade_history corporate_trade_history_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.corporate_trade_history
    ADD CONSTRAINT corporate_trade_history_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 5093 (class 2606 OID 16949)
-- Name: evidence_artefacts evidence_artefacts_evidence_bundle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_artefacts
    ADD CONSTRAINT evidence_artefacts_evidence_bundle_id_fkey FOREIGN KEY (evidence_bundle_id) REFERENCES public.evidence_bundles(evidence_bundle_id) ON DELETE CASCADE;


--
-- TOC entry 5090 (class 2606 OID 16924)
-- Name: evidence_bundles evidence_bundles_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_bundles
    ADD CONSTRAINT evidence_bundles_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id) ON DELETE CASCADE;


--
-- TOC entry 5091 (class 2606 OID 16929)
-- Name: evidence_bundles evidence_bundles_ingestion_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_bundles
    ADD CONSTRAINT evidence_bundles_ingestion_run_id_fkey FOREIGN KEY (ingestion_run_id) REFERENCES public.ingestion_runs(ingestion_run_id) ON DELETE SET NULL;


--
-- TOC entry 5092 (class 2606 OID 16934)
-- Name: evidence_bundles evidence_bundles_match_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evidence_bundles
    ADD CONSTRAINT evidence_bundles_match_run_id_fkey FOREIGN KEY (match_run_id) REFERENCES public.match_runs(match_run_id) ON DELETE SET NULL;


--
-- TOC entry 5071 (class 2606 OID 16682)
-- Name: ingestion_runs ingestion_runs_source_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingestion_runs
    ADD CONSTRAINT ingestion_runs_source_system_id_fkey FOREIGN KEY (source_system_id) REFERENCES public.source_systems(source_system_id);


--
-- TOC entry 5065 (class 2606 OID 16497)
-- Name: kyc_flags kyc_flags_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kyc_flags
    ADD CONSTRAINT kyc_flags_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- TOC entry 5077 (class 2606 OID 16781)
-- Name: match_decisions match_decisions_match_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_decisions
    ADD CONSTRAINT match_decisions_match_run_id_fkey FOREIGN KEY (match_run_id) REFERENCES public.match_runs(match_run_id) ON DELETE CASCADE;


--
-- TOC entry 5078 (class 2606 OID 16791)
-- Name: match_decisions match_decisions_matched_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_decisions
    ADD CONSTRAINT match_decisions_matched_client_id_fkey FOREIGN KEY (matched_client_id) REFERENCES public.clients(id);


--
-- TOC entry 5079 (class 2606 OID 16786)
-- Name: match_decisions match_decisions_source_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.match_decisions
    ADD CONSTRAINT match_decisions_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES public.source_records_raw(source_record_id) ON DELETE CASCADE;


--
-- TOC entry 5075 (class 2606 OID 16756)
-- Name: source_field_mappings source_field_mappings_attribute_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_field_mappings
    ADD CONSTRAINT source_field_mappings_attribute_id_fkey FOREIGN KEY (attribute_id) REFERENCES public.attribute_dictionary(attribute_id);


--
-- TOC entry 5076 (class 2606 OID 16751)
-- Name: source_field_mappings source_field_mappings_source_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_field_mappings
    ADD CONSTRAINT source_field_mappings_source_system_id_fkey FOREIGN KEY (source_system_id) REFERENCES public.source_systems(source_system_id);


--
-- TOC entry 5072 (class 2606 OID 16698)
-- Name: source_records_raw source_records_raw_ingestion_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_records_raw
    ADD CONSTRAINT source_records_raw_ingestion_run_id_fkey FOREIGN KEY (ingestion_run_id) REFERENCES public.ingestion_runs(ingestion_run_id) ON DELETE CASCADE;


--
-- TOC entry 5073 (class 2606 OID 16703)
-- Name: source_records_raw source_records_raw_source_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_records_raw
    ADD CONSTRAINT source_records_raw_source_system_id_fkey FOREIGN KEY (source_system_id) REFERENCES public.source_systems(source_system_id);


--
-- TOC entry 5066 (class 2606 OID 16513)
-- Name: transactions transactions_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id);


--
-- TOC entry 5074 (class 2606 OID 16720)
-- Name: validation_results validation_results_source_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validation_results
    ADD CONSTRAINT validation_results_source_record_id_fkey FOREIGN KEY (source_record_id) REFERENCES public.source_records_raw(source_record_id) ON DELETE CASCADE;


-- Completed on 2026-01-02 19:40:24

--
-- PostgreSQL database dump complete
--

