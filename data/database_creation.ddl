-- *********************************************
-- * SQL PostgreSQL generation                 
-- *--------------------------------------------
-- * DB-MAIN version: 11.0.2              
-- * Generator date: Sep 14 2021              
-- * Generation date: Wed Nov 12 14:28:28 2025 
-- * LUN file: C:\Users\clemc\Documents\ECL\ECL4A\MOD\Systèmes de bases de données\projet\rally_v3.lun 
-- * Schema: rally/1 
-- ********************************************* 


-- Database Section
-- ________________ 

create database rally;


-- Tables Section
-- _____________ 

create table city (
     id serial not null,
     name text not null,
     country text not null,
     long real not null,
     lat real not null,
     constraint ID_CITY primary key (id));

create table contestant (
     id serial not null,
     last_name text not null,
     first_name text not null,
     address text not null,
     participation_number integer not null,
     citizenship text not null,
     id_crew integer not null,
     constraint ID_CONTESTANT primary key (id));

create table crew (
     id serial not null,
     id_team integer not null,
     number integer not null,
     constraint ID_CREW_ID primary key (id),
     constraint FKappartient_ID unique (id_team));

create table participation (
     id_rally integer not null,
     id_team integer not null,
     constraint ID_participe primary key (id_rally, id_team));

create table rally (
     id serial not null,
     name text not null,
     year integer not null,
     constraint ID_RALLY_ID primary key (id));

create table rally_sponsor (
     id serial not null,
     name text not null,
     id_rally integer not null,
     constraint ID_RALLY_SPONSOR primary key (id));

create table result (
     id serial not null,
     time real not null,
     disqualification boolean not null,
     id_crew integer not null,
     id_stage integer not null,
     constraint ID_RESULT primary key (id));

create table stage (
     id serial not null,
     number integer not null,
     kilometers integer not null,
     type text not null,
     max_time real not null,
     id_rally integer not null,
     id_ending_city integer not null,
     id_starting_city integer not null,
     constraint ID_STAGE_ID primary key (id));

create table supplier (
     id serial not null,
     name text not null,
     id_rally integer not null,
     constraint ID_SUPPLIER primary key (id));

create table team (
     id serial not null,
     name text not null,
     budget real not null,
     type text not null,
     official boolean not null,
     constraint ID_TEAM_ID primary key (id));

create table team_sponsor (
     id serial not null,
     name text not null,
     id_team integer not null,
     constraint ID_TEAM_SPONSOR primary key (id));

create table vehicle (
     id serial not null,
     id_crew integer not null,
     number integer not null,
     constructor text not null,
     engine_size real not null,
     serie_number text not null,
     constraint ID_VEHICLE primary key (id),
     constraint FKconduit_ID unique (id_crew));


-- Standard Constraints Section
-- ___________________ 

alter table contestant add constraint FKcompose_FK
     foreign key (id_crew)
     references crew(id);

--Not implemented
--alter table crew add constraint ID_CREW_CHK
--     check(exists(select * from vehicle
--                  where vehicle.id_crew = id)); 

--Not implemented
--alter table crew add constraint ID_CREW_CHK
--     check(exists(select * from contestant
--                  where contestant.id_crew = id)); 

alter table crew add constraint FKappartient_FK
     foreign key (id_team)
     references team;

alter table participation add constraint FKpar_TEA_FK
     foreign key (id_team)
     references team;

alter table participation add constraint FKpar_RAL
     foreign key (id_rally)
     references rally;

--Not implemented
--alter table rally add constraint ID_RALLY_CHK
--     check(exists(select * from stage
--                  where stage.id_rally = id)); 

--Not implemented
--alter table rally add constraint ID_RALLY_CHK
--     check(exists(select * from participation
--                  where participation.id_rally = id)); 

alter table rally_sponsor add constraint FKsponsorise_FK
     foreign key (id_rally)
     references rally;

alter table result add constraint FKobtient_FK
     foreign key (id_crew)
     references crew;

alter table result add constraint FKpossede_FK
     foreign key (id_stage)
     references stage;

--Not implemented
--alter table stage add constraint ID_STAGE_CHK
--     check(exists(select * from result
--                  where result.id_stage = id)); 

alter table stage add constraint FKforme_FK
     foreign key (id_rally)
     references rally;

alter table stage add constraint FKfinit_FK
     foreign key (id_ending_city)
     references city;

alter table stage add constraint FKdemarre_FK
     foreign key (id_starting_city)
     references city;

alter table supplier add constraint FKfournit_FK
     foreign key (id_rally)
     references rally;

--Not implemented
--alter table team add constraint ID_TEAM_CHK
--     check(exists(select * from crew
--                  where crew.id_team = id)); 

alter table team_sponsor add constraint FKfinance_FK
     foreign key (id_team)
     references team;

alter table vehicle add constraint FKconduit_FK
     foreign key (id_crew)
     references crew;


-- Index Section
-- _____________ 

create index FKcompose_IND
     on contestant (id_crew);

create index FKpar_TEA_IND
     on participation (id_team);

create index FKsponsorise_IND
     on rally_sponsor (id_rally);

create index FKobtient_IND
     on result (id_crew);

create index FKpossede_IND
     on result (id_stage);

create index FKforme_IND
     on stage (id_rally);

create index FKfinit_IND
     on stage (id_ending_city);

create index FKdemarre_IND
     on stage (id_starting_city);

create index FKfournit_IND
     on supplier (id_rally);

create index FKfinance_IND
     on team_sponsor (id_team);


-- Domain constraints Section
-- _____________ 

ALTER TABLE team
ADD CONSTRAINT vehicle_type_check
CHECK (type IN ('car', 'truck', 'motorbike'));

ALTER TABLE stage
ADD CONSTRAINT stage_type_check
CHECK (type IN ('linking', 'special'));

ALTER TABLE city
ADD CONSTRAINT city_lat_long_check
CHECK (
    lat BETWEEN -90 AND 90
    AND long BETWEEN -180 AND 180
);

ALTER TABLE stage
ADD CONSTRAINT stage_number_check
CHECK (number >= 0);

ALTER TABLE stage
ADD CONSTRAINT stage_kilometers_check
CHECK (kilometers >= 0);

ALTER TABLE stage
ADD CONSTRAINT stage_max_time_check
CHECK (max_time >= 0);

ALTER TABLE result
ADD CONSTRAINT result_time_check
CHECK (time >= 0);

ALTER TABLE rally
ADD CONSTRAINT rally_year_check
CHECK (year >= 0);

ALTER TABLE team
ADD CONSTRAINT team_budget_check
CHECK (budget >= 0);

ALTER TABLE vehicle
ADD CONSTRAINT vehicle_engine_size_check
CHECK (engine_size >= 0);

ALTER TABLE contestant
ADD CONSTRAINT contestant_participation_number_check
CHECK (participation_number >= 0);

-- Vue Section
-- _____________

CREATE VIEW race_by_team AS
SELECT rally.id, rally.name, rally.year, participation.id_team FROM rally
JOIN participation ON participation.id_rally = rally.id
ORDER BY year ASC;

CREATE VIEW team_info AS
SELECT team.name, team.budget, team.type, crew.id as id_crew,
vehicle.constructor, vehicle.engine_size, vehicle.serie_number, team.id as id_team
FROM team
JOIN crew ON crew.id_team = team.id
JOIN vehicle ON vehicle.id_crew = crew.id;
