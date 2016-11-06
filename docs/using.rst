Using Issuelabeler
==================


You can use Issuelabeler in two mode:

* console mode

* web mode

.. _console-label:

Console mode
------------

Console mode is started with following command:

.. code::

   issuelabeler console [OPTIONS]

List of available options:

\-c, \-\-config TEXT
   Configuration file with authorization tokens.

\-r, \-\-repository TEXT
   Target repository which going to be processed.

\-f, \-\-rules TEXT
   File with rules.

\-x, \-\-rate INTEGER
   How long to wait to another run (in seconds).

\-d, \-\-default TEXT
   Default label if none of rules will match.

\-k, \-\-comments
   Controls if you also search in comments.

\-v, \-\-verbose
   Enables verbose output. (You can enable verbose output multiple times for more detailed output.)

\-\-help
   Shows help.

.. _web-label:

Web mode
--------

Web mode is started with command:

.. code::

   issuelabeler web

This mode will listen on route /hook for incoming POST requests from GitHub. This is called Webhook.

You can create Webhook in your repository settings. When you creating webhook you must specify URL of webhook, which has route /hook.
For example, if your application is running on domain mydomain.com, you have to specify URL of webhook: mydomain.com/hook.

Furthermore you have to specify secret, which is used for preventing of unauthorized usage of your hooks.
Secret is just string which has to be same in auth configuration file and in webhook settings.

Content-type must be application/json.

Last option when creating webhook is event which will trigger webhook. Select individual events and then select Issues.

This settings will send POST request to URL mydomain.com/hook each time new issue is created/edited/commented, etc.