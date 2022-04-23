# Dev WIKI

## Quick Tips
- from docker machine do `docker exec -it werecruit_prod /bin/bash` to loginto werecruit container.
- To figure out all *open connections on pg*, run following sql on db

## Setting up dev environment
- install vscode
- install python 3.8 or above
- install postgres 14 
- install git.
- clone repository
- run db scripts to create database
-- create
-- upgrade
- create .env file
- resolve all library dependencies.

That's it.. Hopefully you are all set...

## Coding guidelines
** Coming soon **

## Frequently used linux commands
- nano to edit files
- chmod +x for sh scripts where permissions are lost as we do git pull
- nohup <command to be executed> &
- grep ERROR wr_job.log


## Frequently used git commands
- `git pull`
- `git status`
- `git restore`
- `git clone <repo name>` . - only done once

## Frequently used docker commands
- `docker exec -it werecruit_prod /bin/bash` -> to get shell acess to werecruit_prod container.
    - To get out the container shell without stopping the container ,  please enter *ctrl+p followed by ctrl+q*
- `docker ps -a`
- `docker start werecruit_prod`
-  `docker pause werecruit_prod`
- `docker commit werecruit_prod werecruit_image`
-  `docker images` 
- `docker unpause werecruit_prod`
