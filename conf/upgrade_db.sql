
 
ALTER TABLE public.wr_jds
    ADD COLUMN client_jd bytea ;

ALTER TABLE public.wr_resumes
    ADD COLUMN resume_content bytea ;

ALTER TABLE public.wr_resumes ADD COLUMN ts tsvector 
    GENERATED ALWAYS AS (to_tsvector('english', json_resume)) STORED;

CREATE INDEX ts_idx ON wr_resumes USING GIN (ts);

 
/* successfully upgrade prod on 29-Dec-2021 
 
ALTER TABLE public.wr_resumes
    ADD COLUMN json_resume jsonb ;
*/
