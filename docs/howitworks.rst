How it works
============

Lets see simple example how to label unlabeled issues in your GitHub repository.

.. testsetup::

   import issuelabeler
   directory = issuelabeler.issuelabel.getDir()

1. You have to read auth configuration file to get token, username and secret (only used in Web mode).
   Then you can check if you parsed the configuration file successfully.

* To read token and username use function :func:`readConfig`.

.. testcode::
   :hide:

   token, username = issuelabeler.issuelabel.readConfig(directory+"/auth.conf.sample")
   print(token)
   print(username)

.. code::

   token, username = issuelabeler.issuelabel.readConfig("auth.conf")
   print(token)
   print(username)

.. testoutput::

   sampletoken
   killerbot

* To read secret use function :func:`readSecret`.

.. testcode::
   :hide:

   secret = issuelabeler.issuelabel.readSecret(directory+"/auth.conf.sample")
   print(secret)

.. code::

   secret = issuelabeler.issuelabel.readSecret("auth.conf")
   print(secret)

.. testoutput::

   secretsecret

2. After that create session from parsed token, using :func:`createSession`.

.. code::

   session = createSession(token)

3. Read all rules from rules configuration file, using :func:`readRules`. And check if it it successfully parsed.

.. testcode::
   :hide:

   content = issuelabeler.issuelabel.readRules(directory+"/rules.conf")
   for line in content:
      print(line,end="")

.. code::

   content = issuelabeler.issuelabel.readRules("rules.conf")
   for line in content:
      print(line)

.. testoutput::

   #Configuration file with rules for GitHub Issue Bot

   #Syntax: rule = label[,color]
   #if color isnt specified, it will be used default color: 7a7a7a (grey)


   #Examples:
   #bug=bug,ff0000
   #(E|e)rror=error


   bug=bug,ff0000
   error=bug,ff0000
   bot=bot,0000ff
   .*=all,ffffff
   0x[a-fA-F0-9]+=hexa,00ff00
   klejcpet=cool,3e4dd4
   @fit.cvut.cz=FIT,238cec
   ([0-9]{1,3}\.){3}[0-9]{1,3}=ipv4,66cccc

4. Label issues using function :func:`labelIssues`, with enabled output.


..   issuelabeler.issuelabel.labelIssues(betamax_session, 'MI-PYT-TestRepo', '<USERNAME>', 'default', False, 2, content, None)

.. code::

   issuelabeler.issuelabel.labelIssues(session, "myrepository", username, "default", False, 2, content, None)
