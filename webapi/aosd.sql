CREATE TABLE main_subscription (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    region character varying(50) NOT NULL,
    subscriptor_id integer NOT NULL
);


CREATE SEQUENCE main_subscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE main_subscription_id_seq OWNED BY main_subscription.id;



CREATE TABLE main_subscriptor (
    id integer NOT NULL,
    email character varying(254) NOT NULL,
    password character varying(128) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    last_login timestamp with time zone
);


CREATE SEQUENCE main_subscriptor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE main_subscriptor_id_seq OWNED BY main_subscriptor.id;



CREATE TABLE main_term (
    id integer NOT NULL,
    term character varying(150) NOT NULL,
    subscription_id integer NOT NULL
);


CREATE SEQUENCE main_term_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE main_term_id_seq OWNED BY main_term.id;



ALTER TABLE ONLY main_subscription ALTER COLUMN id SET DEFAULT nextval('main_subscription_id_seq'::regclass);

ALTER TABLE ONLY main_subscriptor ALTER COLUMN id SET DEFAULT nextval('main_subscriptor_id_seq'::regclass);

ALTER TABLE ONLY main_term ALTER COLUMN id SET DEFAULT nextval('main_term_id_seq'::regclass);



ALTER TABLE ONLY main_subscription ADD CONSTRAINT main_subscription_pkey PRIMARY KEY (id);

ALTER TABLE ONLY main_subscriptor ADD CONSTRAINT main_subscriptor_email_key UNIQUE (email);

ALTER TABLE ONLY main_subscriptor ADD CONSTRAINT main_subscriptor_pkey PRIMARY KEY (id);

ALTER TABLE ONLY main_term ADD CONSTRAINT main_term_pkey PRIMARY KEY (id);




CREATE INDEX main_subscription_fd423cdb ON main_subscription USING btree (subscriptor_id);

CREATE INDEX main_subscriptor_email_57c54c9f673ad35e_like ON main_subscriptor USING btree (email varchar_pattern_ops);

CREATE INDEX main_term_ef42673f ON main_term USING btree (subscription_id);



ALTER TABLE ONLY main_subscription
    ADD CONSTRAINT main_sub_subscriptor_id_404b845db9e535d9_fk_main_subscriptor_id FOREIGN KEY (subscriptor_id) REFERENCES main_subscriptor(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY main_term
    ADD CONSTRAINT main_t_subscription_id_49a416bff5c485cc_fk_main_subscription_id FOREIGN KEY (subscription_id) REFERENCES main_subscription(id) DEFERRABLE INITIALLY DEFERRED;


