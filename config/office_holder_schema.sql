CREATE TYPE electionenum AS ENUM ('primary','general','state','Primary','General','State');
CREATE TYPE oddevenenum AS ENUM ('odd','even','both','BOTH','EVEN','ODD');
CREATE TYPE usstate AS ENUM ('AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MH', 'MA', 'MI', 'FM', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY');
CREATE SEQUENCE pksq START 1;

CREATE TABLE "office" (
	"id" int4 DEFAULT nextval('pksq'),
	"office_level" varchar(255),
	"state" varchar(10),
	"name" text,
	"body_name" text,
	"body_represents_state" text,
	"body_represents_county" text,
	"body_represents_muni" text
	"source" text,
	"electoral_district_name" text,
	"electoral_district_type" text,
	"electoral_district_id" int4,
	"ed_matched" bool,
	"identifier" text,
	"election_key" varchar(50),
	"state_key" varchar(10),
	"updated" timestamp,
	PRIMARY KEY("id")
);

CREATE TABLE "office_holder" (
"id" int4 DEFAULT nextval('pksq'),
"source" text,
"name" varchar(255),
"party" varchar(255),
"website" varchar(255),
"phone" varchar(255),
"mailing_address" text,
"email" varchar(255),
"google_plus_url" varchar(255),
"twitter_name" varchar(255),
"facebook_url" text,
"wiki_word" varchar(255),
"youtube" text,
"election_key" varchar(50),
"state_key" varchar(10),
"dob" timestamp,
"expires" timestamp,
"identifier" text,
"updated" timestamp,
PRIMARY KEY ("id") 
);

CREATE TABLE "office_holder_to_office" (
"source" text,
"election_key" varchar(50),
"state_key" varchar(10),
"sort_order" int4,
"office_id" int4,
"office_holder_id" int4,
PRIMARY KEY ("office_id", "office_holder_id") 
);

CREATE TABLE "precinct" (
"id" int4 DEFAULT nextval('pksq'),
"source" text,
"is_split" bool,
"parent_id" int4,
"name" varchar(255),
"number" varchar(255),
"electoral_district_id" int4,
--"locality_id" varchar(255),
"locality_id" int4,
"ward" varchar(50),
"mail_only" bool,
"polling_location_id" int4,
"early_vote_site_id" int4,
"ballot_style_image_url" varchar(255),
"election_administration_id" int4,
"state_id" int4,
"election_key" varchar(50),
"state_key" varchar(10),
"identifier" text,
"updated" timestamp,
PRIMARY KEY ("id") 
);

CREATE TABLE "locality" (
"id" int4 DEFAULT nextval('pksq')
"source" text,
"election_key" varchar(50),
"state_key" varchar(10),
"name" varchar(255),
"type" varchar(255),
"updated" timestamp,
"identifier" text,
PRIMARY KEY ("id")
);

CREATE TABLE "electoral_district" (
"id" int4 DEFAULT nextval('pksq'),
"source" text,
"name" varchar(255),
"type" varchar(255),
"number" int4,
"state_id" int4,
"election_key" varchar(50),
"state_key" varchar(10),
"identifier" text,
"updated" timestamp,
PRIMARY KEY ("id") 
);

CREATE TABLE "electoral_district__precinct" (
"electoral_district_id" int4,
"precinct_id" int4,
"source" text,
"election_key" varchar(50),
"state_key" varchar(10),
PRIMARY KEY ("electoral_district_id", "precinct_id") 
);

ALTER TABLE "candidate_in_contest" ADD CONSTRAINT "fk_candidate__contest_contest_1" FOREIGN KEY ("contest_id") REFERENCES "contest" ("id");
ALTER TABLE "candidate_in_contest" ADD CONSTRAINT "fk_candidate__contest_candidate_1" FOREIGN KEY ("candidate_id") REFERENCES "candidate" ("id");
ALTER TABLE "ballot_response" ADD CONSTRAINT "fk_ballot_response_referendum_1" FOREIGN KEY ("referendum_id") REFERENCES "referendum" ("id");
ALTER TABLE "referendum" ADD CONSTRAINT "fk_referendum_contest" FOREIGN KEY ("contest_id") REFERENCES "contest" ("id");
ALTER TABLE "electoral_district__precinct" ADD CONSTRAINT "fk_electoral_district__precinct_electoral_district_1" FOREIGN KEY ("electoral_district_id") REFERENCES "electoral_district" ("id");
ALTER TABLE "electoral_district__precinct" ADD CONSTRAINT "fk_electoral_district__precinct_precinct_1" FOREIGN KEY ("precinct_id") REFERENCES "precinct" ("id");
ALTER TABLE "precinct" ADD CONSTRAINT "fk_precinct_election_administration_1" FOREIGN KEY ("election_administration_id") REFERENCES "election_administration" ("id");
ALTER TABLE "election" ADD CONSTRAINT "fk_election_state_1" FOREIGN KEY ("state_id") REFERENCES "state" ("id");
ALTER TABLE "precinct" ADD CONSTRAINT "fk_precinct_state_1" FOREIGN KEY ("state_id") REFERENCES "state" ("id");
ALTER TABLE "contest" ADD CONSTRAINT "fk_contest_electoral_district_1" FOREIGN KEY ("electoral_district_id") REFERENCES "electoral_district" ("id");
ALTER TABLE "precinct" ADD CONSTRAINT "fk_precinct_split_precinct_1" FOREIGN KEY ("parent_id") REFERENCES "precinct" ("id");
