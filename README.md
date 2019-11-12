#GSIP QGIS demonstration

This is essentially the same application than the web version, but running in QGIS

----

important notes (for Windows only I think)

rdflib is not available in QGIS, so it must be installed in QGIS own python3 environment.

This explains what to do :

https://gis.stackexchange.com/questions/273870/osgeo4w-shell-with-python3/277842#277842

Once OSGeo4W shell is running, just type

`py3_env`

this should set up the environment to run pip. You can try launching python with
 
 `python3`
 
Once you managed to get a python3 running, go back to console (exit python3) and run

`python3 -m pip install rdflib`

and then install the json-ld plugin

`python3 -m pip install rdflib-jsonld`

Now, you're not totally off the hook.  There is a bug (?) in rdflib that does not consider the possibility that stdout might be None - which is apparently the case when ran from QGIS, so you will get a

`AttributeError: 'NoneType' object has no attribute 'isatty' `

you must fix this by editing the RDFlib  __init__.py file

on my installation, it's located :

`C:\Program Files\QGIS 3.10\apps\Python37\Lib\site-packages\rdflib\__init__.py`

and line 78 has

```python
if not hasattr(__main__, '__file__') and sys.stdout.isatty():
```

just add another condition to check if stdout is not None

```python
if not hasattr(__main__, '__file__') and sys.stdout is not None and sys.stdout.isatty():
```
This worked for me.







