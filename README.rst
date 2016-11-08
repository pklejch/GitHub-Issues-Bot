How to build documentation
==========================

Create virtual enviroment with:

:: code

   python3 -m venv env

Activate virtual enviroment:

:: code

   . env/bin/activate

Change your working directory to docs:

:: code

   cd docs/

Install dependencies:

:: code 

   python -m pip install -r requirements.txt

To build documentation in HTML format, run following command:

:: code

   make html

This will create documentantion in HTML format in _build/html.
You can start reading documentation by opening _build/html/index.html in your browser.

To run doctests run command:

:: code

   make doctest
