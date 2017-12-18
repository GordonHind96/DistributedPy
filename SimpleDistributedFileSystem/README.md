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

## TODO
* update directory server to return more information ie file found but locked or file not found
* unlock file after a certain time period
* REPLICATION
* set so that user can specify number of versions of file default 1
* create version replicated or version column, and update all files when edit is made
* think of how to react ot user deleteing file with replicated copies
* make it so fileservers are no longer sharing the same database
* Auth Server
* user accounts
* only users can access usertaged files
* groups and groupd access of files

### Bonus
* create a nice user interface
