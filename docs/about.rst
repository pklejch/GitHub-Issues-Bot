About Issuelabeler
==================

This tool is used for labeling unlabeled issues in your GitHub repository.

Issues are labeled based on rules specified in configuration file. For more information see :ref:`rules-label`.

You can run this tool either in console mode or in web mode.

In :ref:`console-label` you run this tool from command line. It will check your repository in specified intervals and label unlabeled issues.

In :ref:`web-label` you run this tool as web application. Then you use GitHub Webhook to send HTTP POST request to your web application.
This will label your issues only when issue event is triggered (e.g. new issue created). For more information see :ref:`web-label`.