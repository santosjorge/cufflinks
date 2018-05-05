# Cufflinks Documentation

Generated using Sphinx. 

### Creating Documentation Scaffold

We first create the configuration as outlined [here](https://gisellezeno.com/tutorials/sphinx-for-python-documentation.html).
We create a docs folder and using the configuration in this tutorial we run:

```
sphinx-quickstart
``` 

We then have to setup the conf.py file in /source as detailed in the above link.

We create the .rst files which outline how the documentation is to be compiled. 
From the docs folder, we run:

```
sphinx-apidoc -f --separate -o source/ ../cufflinks/
```

### Generation of Documentation

To generate the documentation from the .rst templates, run the following from /docs:

```
make html
```

Documentation should be generated in a folder called html! 

The "source" folder contains the templates to generate the documentation, and can be edited to customize as desired. 
