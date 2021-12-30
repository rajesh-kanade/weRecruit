
 
ALTER TABLE public.wr_jds
    ADD COLUMN client_jd bytea ;

ALTER TABLE public.wr_resumes
    ADD COLUMN resume_content bytea ;
    
/* successfully upgrade prod on 29-Dec-2021 
 
ALTER TABLE public.wr_resumes
    ADD COLUMN json_resume jsonb ;
*/
