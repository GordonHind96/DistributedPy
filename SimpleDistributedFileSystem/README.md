# SIMPLE DISTRIBUTED FILE SYSTEM

## WHAT's DONE

### FileServer
* endpoints for creating a file
* endpoints for retrieving a specific file
* endpoints for retreiving all files
* endpoints for updating file
* endpoints for deleteing file

### Directory Server
* endpoints to write a file on the directory server and receive location info in return
* endpoints to request a file by name and have its location and id returned
* returns next available version of file if locked

### Lock Server
* endpoint for lock, calls lock in fileserver, returns lock id
* endpoint for unlock, calls unlock in fileserver, deletes lock
* users can only unlock a file if they have a lock id
* users can not lock a file that has been locked

### Replication
* when creating file, file is saved to each server sequentially, this will ideally be changed to a more dynamic model
* when update is made to primary version of file, it goes and updates all secondary versions of the file via the directory server
* when update is made to secondary version of file, it informs the dirctory server to update the primary, and the primary updates the rest of the secondarys
## TODO
* update directory server to return more information ie file found but locked or file not found
* unlock file after a certain time period
* set so that user can specify number of versions of file default 1
* think of how to react ot user deleteing file with replicated copies
* make it so fileservers are no longer sharing the same database
* Auth Server
* user accounts
* only users can access usertaged files
* groups and groupd access of files

### Bonus
* create a nice user interface
