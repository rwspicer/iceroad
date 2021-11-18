# ice-road-project

Code and docs for the ice road project


## Co registration process

The co-registration process has 3 main steps

- Orthorectification
- clipping
- co-registration 

## Orthorectification

Use `code/python/orthorectify-utility.py`

run 

    python code/python/orthorectify-utility.py config.yml

`orthorectification-config-example.yml` describes how to set up the config file


## Clipping

Take out put from orthorectification and Clip data to areas of interest

Use `code/python/clipping-utility.py`

run 

    python code/python/clipping-utility.py config.yml

`clipping-config-example.yml` describes how to set up the config file

## Co registration

Take out put from  clipping and co-register. Add a column 
to the report file from clipping called `co-register` assign 
one row as the `reference` image, and other rows as `target`. Leave 
rows in this column blank to skip. See `co-register-in-example.csv` for an example of how this should look.

Use `code/python/co-register-utility.py`

run 

    python code/python/co-register-utility.py config.yml

`co-registration-config-example.yml` describes how to set up the config file

