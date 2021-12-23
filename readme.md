# Dev Notes

from docker machine do `docker exec -it werecruit_prod /bin/bash` to loginto werecruit container.

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
1. [stop](#stopping-werecruit) werecruit 
2. git pull 
3. Db upgrade if applicable
4. .env file update if applicable
5. optionally clean up flask sessions folder
6. optionally clean up werecruit.log folder
7. do `chmod +x werecruit_start.sh`. Note executable permisions are lost after every git pull.
8. run `we_recruit_start.sh`
9. sanity test

## How to create an docker image - 
From the main contabo machine run following commands
1. `docker pause werecruit_prod` ( this is our container name)
2. `docker commit werecruit_prod werecruit_image`
3. verify image is created by running `docker images` & ensure the new image is listed.
3. `docker unpause werecruit_prod`

## How to take Database backup
**coming soon**




