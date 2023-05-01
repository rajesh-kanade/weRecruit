
## Setting up dev environment
- install vscode
- install python 3.8 or above
- install postgres 14 
- install git.
- clone repository
- Resolve all dependencies for the project captured in requirements.txt
- run following db scripts in the conf folder to create database
    - admin_create_ddl.sql
    - upgrade_db.sql
- create .env file. 

    This file needs to be created in the top level or root folder of the repository. ***Under no circumstances should this file be committed or pushed to the github for security reason.***


That's it.. Hopefully you are all set...


# Contribution process overview
* Create a branch for the issue you are working on. Branch creation can be done from the issue UI itself.
* Work in the branch you created above. You can commit and push to your branch as frequently as possible.
* It is good to pull frequently so your branch is as close to the master branch. We recommend you pull atleast once a day and resolve conflicts asap.
* When your coding is done, please do thorough unit , functional , non functional, edge, negative scenarios testing.
* If your code changes involve database changes, please make sure you have updated the upgrade_db.sql file with your changes.
* If you have added python libraries, please ensure you have changed the requirements.txt file.
* Create a pull request & provide detailed information about the fix you have, testing you have done etc in the PR.

Please note, if you are working on multiple issues, please create one branch per issue.

## Frequently used Linux commands
- nano to edit files
- chmod +x for sh scripts where permissions are lost as we do git pull
- nohup <command to be executed> &
- grep ERROR wr_job.log

## Frequently used Linux commands
- `docker exec -it werecruit_prod /bin/bash` -> to get shell acess to werecruit_prod container.
    - To get out the container shell without stopping the container ,  please enter *ctrl+p followed by ctrl+q*
- `docker ps -a`
- `docker start werecruit_prod`
-  `docker pause werecruit_prod`
- `docker commit werecruit_prod werecruit_image`
-  `docker images` 
- `docker unpause werecruit_prod`


- `git pull`
- `git status`
- `git restore`
- `git clone <repo name>` . - only done once
- `git tag -l`
- `git tag <tag-name>`
- `git push origin <tag-name>`
- `git log master  --oneline -20`
- 
## External resources

https://www.kdnuggets.com/2022/06/14-essential-git-commands-data-scientists.html
https://www.markdownguide.org/cheat-sheet/


# Prod Notes : weRecruit on Ubuntu

## Accessing prod from host server
On main contabo machine , switch to weRecruit folder and execute the shell script to get into docker machine.

This can also be done manually in following fashion
From main contabo machine do `docker exec -it werecruit_prod /bin/bash` to login to werecruit container.

## First time installation checklist
* get a docker image based on ubuntu 20 LTS
* Python is installed ( 3.8 )
* git is installed
* postgres is installed ( 14.x )
* run command `mkdir /etc/werecruit`
* run command `cd /etc/werecruit`
* run command `git clone <repo url> . `.
* run command `pip install -r requirements.txt` 
* create .env file & make sure all keys are configured

## starting weRecruit
* cd to `etc/werecruit` .
* Run `./werecruit_start.sh`
* if you get permission error please run `chmod +X werecruit_start.sh`. Typically file permissions are lost after you do git pull.

## stopping weRecruit
- cd to /etc/werecruit
- run ./wr_stop.sh. This should stop gunicorn processes & also display the pid for scheduler python process.
- To stop weRecruit scheduler note down the pid listed in above step and run kill <pid>
Confirm it is stopped by visiting werecruit website from browser & verify you get a gateway error.

## Maintenance checklist 
- if you want to stop and start werecruit, please follow the steps in [stop](#stopping-weRecruit) and [start](#starting-weRecruit) section respectively.

- Run `wr_maintain.sh` script to clean up *.log & *.out files 
- cleanup sessions related folder by ( TODO -> automate this step )
    - `cd /etc/werecruit/sessions`
    - `rm *`
- DB backups ( Need to automate it)
    - currently backups are being taken by connecting to pg thru pg admin and taking back up on laptop. **Needs a better way**

- once in a while container may crash or stop , to restart do following from main contabo machine
    - run `docker ps -a` command to ensure werecruit_prod is listed.
    - run `docker start werecruit_prod` command to start the werecruit prod container

- Please note : To come out of werecruit_prod container without stopping it , please enter *ctrl+p followed by ctrl+q*. You will be taken back to the main host machine.

## Upgrade checklist ( TODO -> write script for this)
- from terminal login to the werecruit container. For creds contact admin.
- run  `cd /etc/werecruit` 
- [stop](#stopping-werecruit) werecruit  
    - run `git status` to list files you may changed on the prod.  
    - if the werecruit_start.sh is changed then you may first want to restore it on server b by running `git restore werecruit_start.sh`
- Db upgrade *if applicable*
- .env file update *if applicable*.
- pip install if there are new dependencies.
- *optionally* clean up flask sessions folder
- *optionally* clean up werecruit.log folder.
- run `git pull` to get all the latest code
- do `chmod +x werecruit_start.sh`. Note executable permisions are lost in every git pull which has a **modified version of wercecruit_start.sh**.
- run `we_recruit_start.sh`
- sanity test with test data 
    - test user acct -> rkanade@gmail.com
- Tag the repo with new build number
    - To get all current tags run `git tag -l`. Note down the highest build number. New build number should be current highest + 1. Replace n with new build number and run following 2 commands.
      - `git tag -a <v1.1.Buildn> -m "weRecruit 1.1 Build n"`  //used to tag the commit 
      - `git push origin <v1.1.Buildn>`  // to push the tag onto remote 

## How to create an docker image & move to another node - 
From the main host machine run following commands
- `docker pause werecruit_prod` ( this is our container name)
- `docker commit werecruit_prod werecruit_image`
- verify image is created by running `docker images` & ensure the new image is listed.
- `docker unpause werecruit_prod`.
- If you want to move the image created above from one machine (A) to another machine ( say B), run following commands
    - on machine A `docker save werecruit_image > werecruit_prod.tar`
    - copy the above tar file from A to B using scp from machine A to B.
    - on machine B, run `docker load --input werecruit_prod.tar`
    - on machine B, for **first time only** you need to run `docker run -dit -p 0.0.0.0:8280:5000/tcp --name werecruit_prod werecruit_image`. This will create and start the container.

## Getting out of prod container
- To get out the container shell without stopping the container , please enter ctrl+p followed by ctrl+q



