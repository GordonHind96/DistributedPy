# SIMPLE DISTRIBUTED FILE SYSTEM

## WHAT's DONE

### FileServer
* endpoints for creating a file
* endpoints for retrieving a specific file
* endpoints for retreiving all files
* endpoints for updating file
* endpoints for deleteing file
* code to begin updating secondary files when primary updated
* code to notify primary when secondary is updated

### Directory Server
* endpoints to write a file on the directory server and receive location info in return
* endpoints to request a file by name and have its location and id returned
* returns next available version of file if locked
* directory server queries lock server about files to determine if they are locked or not

### Lock Server
* endpoint for lock, checks if lock exists for file and then creates lock on lockserver
* endpoint for unlock, check if lock exists, deletes lock
* users can only unlock a file if they have a lock id
* users can not lock a file that has been locked
* validate lock, when given a lock id and a file id returns true or false that the lock is valid for id
* check lock, given file info determine if file is locked

### Replication
* when creating file, file is saved to each server sequentially, this will ideally be changed to a more dynamic model
* when update is made to primary version of file, it goes and updates all secondary versions of the file via the directory server
* when update is made to secondary version of file, it informs the dirctory server to update the primary, and the primary updates the rest of the secondarys

## TODO
* client library
* unlock file after a certain time period
* set so that user can specify number of versions of file default 1
* think of how to react to user deleteing file with replicated copies
* ~~make it so fileservers are no longer sharing the same database~~ this will be solved by running on different machines
* Auth Server
* user accounts
* only users can access usertaged files
* groups and groupd access of files

## Report
Explanation of some of the design choices.
### Directory Server
Stores in locations of the fileservers, fileservers register and unregister with the directory server. When queried for a file the directory server will search for the file and return the first available version of that file.
#### Issues and Improvements
Currenrtly replication and storage is done naively, replicating all files to all available fileservers, and ordering files in terms of times written. Imrpovement order fileservers alphabetically,by user or by filetype to reduce search time. Replicate to different servers

### File Server
Stores the information about the files. including contents,name, serverid and version (either primary or secondary) when a file is updated of deleted (if primary all versions will be updated or deleted), if secondary primary will be updated, but not deleted.

#### Issues and Improvements
Currently as all fileservers run on a single maching the share use of the same database, meaning technically I can query the contents of server 2 on server 1. This would be solved by running the servers on seperate machines via docker.

### Lock Server
Stores the information about locks. Lock information is info on the file that is locked, the port it is locked on and when it was locked.
Locks can be unlocked if a valid lock id is given. Locks can be validated with lock id and file id or with file id and port number.

