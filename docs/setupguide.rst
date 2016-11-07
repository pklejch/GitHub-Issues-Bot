Installation guide
==================

Download
--------
From GitHub
...........

You can download this tool either from GitHub repository (https://github.com/pklejch/GitHub-Issues-Bot) as zip.

Or clone it to you computer using

.. code::

   git clone https://github.com/pklejch/GitHub-Issues-Bot

From TestPYPi
.............
You can download this tool from TestPYPi (https://testpypi.python.org/pypi/issuelabeler) in tar.gz format.

Alternatively you can use pip tool:

.. code::

  python -m pip install --extra-index-url https://testpypi.python.org/pypi issuelabeler

Installation
------------

Run following command in the downloaded directory and install it system-wide:

.. code::

   python3 setup.py install


Or you can create virtual environment using:

.. code::

   python3 -m venv env

Start virtual environment:

.. code::

   . env/bin/activate

And then install it into virtual environment:

.. code::

   python setup.py install

Configuration
-------------

There are two configuration files:

* auth.conf

* rules.conf

Auth configuration file
.......................

Auth configuration file contains 3 directives:

* token

* username

* secret

**Token** directive contains access token. You can create new access token on URL https://github.com/settings/tokens.
Create new token, copy it into clipboard and paste it into configuration file.

**Username** directive contains username of user, who created repository, which will be processed.

**Secret** directive is used only in web mode.
It contains secret which has to be same as you specified while creating webhook.
For instructions to create webhook see chapter :ref:`web-label`.

Package already contains sample configuration file *auth.conf.sample*, you can rename it to *auth.conf* by using following command

.. code::

   mv auth.conf.sample auth.conf

And then edit it and fill correct values.

.. _rules-label:

Rules configuration file
........................

Rules configuration file contains rules for labeling. Each line has to contain at most one rule. The syntax is following:

.. code::

   rule = label[,color]

Color is optional, if you dont specify any color, it will be used default grey color. Color is specified in RGB hex format without "#" prefix.
As rule you can enter regular expression.

For example:

.. code::

   ([0-9]{1,3}\.){3}[0-9]{1,3}=ipv4,66cccc

This rule will label all issues which contain IPv4 address with tag "ipv4" with color #66cccc.
