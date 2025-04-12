# How to run backend

## Start backend

* `pip install`
* `python create_db.py` this will execute the ddl and it will create empty tables schemas for you but we do not have any data. 
*  You will need some insert from Dbeaver and just run some sql script to do some insertions.
* `python controller.py` or rename it to app.py, to start the http server and serve all the restful endpoints.
* This is currently in debugging mode. The port is defined and used in reactjs code.