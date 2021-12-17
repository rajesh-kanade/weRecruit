# Dev Notes

# Prod Notes : weRecruit on Ubuntu

# First time installation checklist
* get a docker image based on ubuntu 20 LTS
* Python is installed ( 3.8 )
* git is installed
* postgres is installed ( 12 or above )
* `mkdir \etc\werecruit`
* `cd \etc\werecruit`
* `git clone <repo url> . `.
* `pip install -r requirements.txt` 
* create .env file & make sure all keys are configured

# starting weRecruit
* Run the werecruit_start.sh scripts to start following python programs 
    nohup python3 webApp.py & 
    nohup python3 ./src/werecruit/cronjobs.py & 

# Maintenance checklist ( TODO -> write script for this )
1. stop both python processes related to werecruit/cronjobs
2. cleanup sessions related folder
3. cleanup werecruit.log file
4. DB backups ?

# Upgrade checklist ( TODO -> write script for this)
1. stop both python processes related to werecruit.
    1.1 run top command & note down the process IDs related to 2 python running. Issue kill <pid> for each process id noted. 
2. git pull 
3. Db upgrade if applicable
4. .env file update if applicable
5. optionally clean up flask sessions folder
6. optionally clean up werecruit.log folder
7. do chmod +x werecruit_start.sh file. Executable permisions are lost after git pull.
8. run we_recruit_start.sh
9. sanity test

# How to create an docker image - from the main contabo machine run following commands
1. docker pause werecruit_prod ( this is our container name)
2. docker commit werecruit_prod werecruit_image
3. verify image is created by running docker images & ensure the new image is listed.
3. docker unpause werecruit_prod

# How to take Database backup
** coming soon **


