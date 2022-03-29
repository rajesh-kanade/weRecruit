
/* ******** successfully upgrade prod on 28-March-2022 on contabo2 server ******************

ALTER TABLE public.wr_resumes
    ADD COLUMN is_deleted boolean NOT NULL DEFAULT false ;

ALTER TABLE public.wr_jds
    ADD COLUMN is_deleted boolean NOT NULL DEFAULT false ;


insert into public.application_status_codes(id,description,is_deleted) values (1,'Initial screening scheduled',false);
insert into public.application_status_codes(id,description,is_deleted) values (2,'Initial screening cleared',false);
insert into public.application_status_codes(id,description,is_deleted) values (3,'Initial screening failed',false);


 **********************************  */



/* ******** successfully upgrade prod on 14-March-2022 *****************
ALTER TABLE public.wr_jds
  RENAME COLUMN yrs_of_exp TO min_yrs_of_exp;

ALTER TABLE public.wr_jds
    ADD COLUMN max_yrs_of_exp NUMERIC(4,2) ;
 *********************************  */


/* successfully upgrade prod on 12-Feb-2022 
ALTER TABLE public.wr_jds
    ADD COLUMN client_jd bytea ;

ALTER TABLE public.wr_resumes
    ADD COLUMN resume_content bytea ;

ALTER TABLE public.wr_resumes ADD COLUMN ts tsvector 
    GENERATED ALWAYS AS (to_tsvector('english', json_resume)) STORED;

CREATE INDEX ts_idx ON wr_resumes USING GIN (ts);
*/

 
/* successfully upgrade prod on 29-Dec-2021 
 
ALTER TABLE public.wr_resumes
    ADD COLUMN json_resume jsonb ;
*/
