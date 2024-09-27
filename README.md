## Task is to setup PostgreSQL with DataSunrise

1. Create a table in PostgreSQL and fill it with arbitrary data
Table requirements:
  * at least 5 columns containing columns of the following types: string, numeric and date/time
  * at least 1000 rows
  * at least 5% of string data must be empty
  * at least 5% in each data column must be NULL
2. Register a PostgreSQL database in Data Sun rise.
3. In Data Sun rise, create a masking rule with masking the first 2 characters of the string to all columns of the string data type.
4. In Data Sun rise, create an audit rule for SELECT queries with the "Log query results" option enabled.
5. Write code to verify the operation of the masking rule. The data received through the proxy request must be masked.
6. Write code to verify that an audit event has appeared in the list of Events, and masked data has been saved inside it.
7. Write the result of the check to a file indicating the received and expected result. Compare the expected and actual results in the form of tables.


### DONE
- initial_db.py creates table and inserts data
- ds_script.py connects to DataSunrise and creates masking and audit rules
- check.py checks masking and audit rules 
