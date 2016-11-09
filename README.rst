.. image:: https://travis-ci.com/pklejch/GitHub-Issues-Bot.svg?token=Wsjf89ecpz1KadZ1RsAF&branch=master

GitHub-Issues-Bot
=================
GitHub Issues Bot scans issues of selected repository and tags those issues.

Don't forget to fill auth.conf configuration file. 

How to test
-----------
Run:

.. code::

   python setup.py test

or

.. code::

   pytest -v tests/test_app.py

If you have filled auth.conf with right values, you can use online testing. With real HTTP requests. Old cassettes will be rewrited. Eg:

.. code::

   AUTH_FILE=issuelabeler/auth.conf pytest -v tests/test_app.py

If you dont specify enviroment variable AUTH_FILE, test will use recorded betamax cassettes.


How to build documentation
--------------------------

Create virtual enviroment with:

.. code::

   python3 -m venv env

Activate virtual enviroment:

.. code::

   . env/bin/activate

Change your working directory to docs:

.. code::

   cd docs/

Install dependencies:

.. code::

   python -m pip install -r requirements.txt

To build documentation in HTML format, run following command:

.. code::

   make html

This will create documentantion in HTML format in _build/html.
You can start reading documentation by opening _build/html/index.html in your browser.

To run doctests run command:

.. code::

   make doctest
