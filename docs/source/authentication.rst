Authentication
==============

Access to the `Open Supply Hub API <https://opensupplyhub.org>`_ requires an access token. You can 
create, view (copy), or re-create yours from the `Setting page "Token" tab at <https://openapparel.org/settings>`_.

.. warning::
    Never include credentials of any form in your source code, not even for debugging. Once
    you decide to share your code, or upload it to public repositories, such as github, 
    or gitlab, they will easily leak to others. 
    
    Even removing them from the code will not remove them from a prior version if you use
    a config management system, and can be retrieved in the future.

    Please recreate your token from `setting page "Token" tab at <https://openapparel.org/settings>`_ after
    you inadvertenly used this token in your code. 

We support three methods of supplying the token, one is, supplying it as a parameter when creating an `OSH_API` object,
one is to supply is as part of a setting, or environment file, and lastly via setting it via an environment variable.

The latter is mostly likely the method of choice when using containers, or running managed services, where they may be
called secrets.

Supply as parameter
-------------------

.. code-block:: python
   :linenos:
   
   import pyosh

   osh_api = pyosh.OSH_API(token='a584abce2b159c4d8cf88eac3a26fbe3b1a13b8e')
  

Supply as part of an .env file
------------------------------

Supply via an environment variable
----------------------------------


