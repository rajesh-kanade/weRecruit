# Dev Notes

from docker machine do `docker exec -it werecruit_prod /bin/bash` to loginto werecruit container.

To figure out all resumes where we did *not parse resume*, run following your query
select count(*) from wr_resumes 
where json_resume is NULL and resume_content is not null

To figure out all *open connections on pg*, run following sql on db


## frequently used linux commands
- nano to edit files
- chmod +x for sh scripts where permissions are lost as we do git pull
- nohup <command to be executed> &


## frequently used git commands
- git pull
- git status
- git restore
- git clone <repo name> . - only done once


# Prod Notes : weRecruit on Ubuntu

from main machine do `docker exec -it werecruit_prod /bin/bash` to loginto werecruit container.

## First time installation checklist
* get a docker image based on ubuntu 20 LTS
* Python is installed ( 3.8 )
* git is installed
* postgres is installed ( 12 or above )
* run command `mkdir \etc\werecruit`
* run command `cd \etc\werecruit`
* run command `git clone <repo url> . `.
* run command `pip install -r requirements.txt` 
* create .env file & make sure all keys are configured

## starting weRecruit
* cd to `etc/werecruit` .
* Run `./werecruit_start.sh`
* if you get permission error please run `chmod +X werecruit_start.sh`. Typically file permissions are lost after you do git pull.

## stopping weRecruit
- find weRecruit scheduler process by running command `ps ax|grep python`. In theory you should see only python process listed ( excluding gunicorn related python processes if any.)
- To stop weRecruit scheduler note down the pid listed in above step and run `kill <pid>`
- find running gunicorn processes by running `ps ax|grep gunicorn`.
- stop gunicorn by running `pkill gunicorn` .
- Confirm it is stopped by vising werecruit website from browser & verify you get a gateway error.

## Maintenance checklist ( TODO -> write script for this )
- if you want to stop and start werecruit, please follow the steps in [stop](#stopping-weRecruit) and [start](#starting-weRecruit) section respectively.
- cleanup sessions related folder by 
    - `cd /etc/werecruit/sessions`
    - `rm *`
- cleanup werecruit.log file by running following commands 
    - `cd /etc/werecruit` 
    - `rm werecruit.log`

- DB backups 
    - Coming soon

## Upgrade checklist ( TODO -> write script for this)
- from terminal login to the werecruit container. For creds contact admin.
- run  `cd /etc/werecruit` 
- [stop](#stopping-werecruit) werecruit  
    - run `git status` to list files you may changed on the prod.  
    - if the werecruit_start.sh is changed then you may first want to restore it on server b by running `git restore werecruit_start.sh`
- Db upgrade *if applicable*
- .env file update *if applicable*.
- *optionally* clean up flask sessions folder
- *optionally* clean up werecruit.log folder.
- run `git pull` to get all the latest code
- do `chmod +x werecruit_start.sh`. Note executable permisions are lost in every git pull which has a *modified version of wercecruit_start.sh*.
- run `we_recruit_start.sh`
- sanity test with test data 
    - test user acct -> rkanade@gmail.com

## How to create an docker image - 
From the main contabo machine run following commands
1. `docker pause werecruit_prod` ( this is our container name)
2. `docker commit werecruit_prod werecruit_image`
3. verify image is created by running `docker images` & ensure the new image is listed.
3. `docker unpause werecruit_prod`

## How to take Database backup
**coming soon**




