========
calligra
========

:Author: `Elie ROUDNINSKI <mailto:xademax@gmail.com>`_

**calligra** is a pure Python package that tries to modelize a subset of the C langage syntax in order to reason about C types, from Python scripts.
Its main goals are to do metaprogrammation and code generation. It does **not parse** C code itself at all.

**calligra** was first designed to (un)serialize complex (but not too complex ...) C structures from JSON.

.. contents::
    :backlinks: none

.. sectnum::

Installation
==============

Requirements
----------------

**calligra** requires Python 3. It has been tested on Python 3.6 on Linux but it should work on 3.4 and 3.6 and on Windows also.
At the moment, it does not require any external Python modules/packages, but this might change in the future.

As **calligra** is intended to generate code, some external dependencies might be needed to compile the generated code.

From github
---------------

You can clone this repository and install it with setuptools directly::

    $ python3 setup.py install --user

From pip
------------

As every pip available package, you can install it easily with the pip package::

    $ python3 -m pip install --user calligra

Tests
-----

Tests are available in the source distribution (either from github or from pip) and are located in the |tests/|_ directory.
You can run them with setuptools::

    $ python3 setup.py test

.. |tests/| replace:: ``tests/``
.. _tests/: tests/

Howto
=====

Introduction
------------

As specified before, **calligra** is intended to reason about C types at a Python level.

Currently, you can modelize the following types:

- primary types like char, int, float, double etc.
- C strings (char*)
- enum
- struct, named and anonymous
- union, named and anonymous

and the following declaration modifiers:

- pointers
- array

Nested array of pointers or pointers to array are not supported.

At the moment, you have two choices:

- define everything from Python
- parse C code with the cparser importer module

In the future, you will be able to import definitions from:

- JSON Schema

Examples
--------

Lets start with a basic example.
In the following code snippets we will be defining a C structure called `person` with 2 members:

- a string `name`
- an unsigned integer `age`

And then we will generate the associated C code.

First import the main modules:

.. code-block:: Python

    import calligra
    import calligra.stdlib

`calligra` module is where the C type/declaration syntax is modelized.
`calligra.stdlib` is where standard C types are defined.

Then define the structure:

.. code-block:: Python

    namespace = calligra.stdlib.namespace
    person = calligra.struct(namespace, 'person')
    person.add(
        calligra.declaration(
            namespace, namespace.get('char'), 'name', pointer = True
        )
    )
    person.add(
        calligra.declaration(
            namespace, namespace.get('uint8_t'), 'age'
        )
    )

Finally, generate the C code:

.. code-block:: Python

    print(person.define())

This should generate something similar to:

.. code-block:: C

    struct person {
        char *name;
        uint8_t age;
    };

More advanced examples are located in the |examples/|_ directory.

.. |examples/| replace:: ``examples/``
.. _examples/: examples/

Modules
=======

Conversion
----------

Conversion modules are located in the |calligra/convert/|_ directory and are meant to (un)serialize C types to and from another format (like JSON).

.. |calligra/convert/| replace:: ``calligra/convert/``
.. _calligra/convert/: calligra/convert/

Currently available conversion modules are:

- `calligra.convert.jansson`: to convert C types to and from JSON using the `Jansson <https://github.com/akheron/jansson/>`_ library.

Jansson
~~~~~~~

In order to use the jansson conversion module, just import the `calligra.convert.jansson` module:

.. code-block:: Python

    import calligra.convert.jansson

After that, every type should now have a `to_json` and a `from_json` method.
Those are actually `calligra.functions` object which you can `define` to generate the corresponding C code:

.. code-block:: Python

    print(person.to_json.define())

Which should generate something similar to:

.. code-block:: C

    json_t *person_to_json(struct person const *person);

And for the function body:

.. code-block:: Python

    print(person.to_json.code(body = True))

Which should generate something similar to (non-contractual code):

.. code-block:: C

    json_t *person_to_json(struct person const *person) {
        json_t *json = json_object(), *child;
        if(!json) {
            return NULL;
        }
        /*name*/
        if((person != NULL) && ((*person).name != NULL) && (*(*person).name != 0)) {
            child = json_string((*person).name);
            if(!child || json_object_set_new_nocheck(json, "name", child) != 0) {
                if(child) {
                    json_decref(child);
                }
                json_decref(json);
                return NULL;
            }
        }
        /*age*/
        if(person != NULL) {
            child = json_integer((*person).age);
            if(!child || json_object_set_new_nocheck(json, "age", child) != 0) {
                if(child) {
                    json_decref(child);
                }
                json_decref(json);
                return NULL;
            }
        }
        return json;
    }

Importer
--------

Importer modules are located in the |calligra/importer/|_ directory and are meant to import C types from another format (like C).

.. |calligra/importer/| replace:: ``calligra/importer/``
.. _calligra/importer/: calligra/importer/

Currently available importer modules are:

- `calligra.importer.cparser`: to import C types directly from C code using the `pycparser <https://github.com/eliben/pycparser/>`_ package.
