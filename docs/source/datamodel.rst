.. _datamodel:

Data Model
==========

contributor_lists
-----------------

Inputs
~~~~~~

JSON Schema
~~~~~~~~~~~

.. code-block:: json
   :linenos:

   {
     "$schema": "https://json-schema.org/draft/2020-12/schema",
     "contributor_id": {
        "anyOf": [
            {
                "type": "integer"
            },
            {
                "type":"string",
                "minLength": 1,
                "maxLength": 200
            }
        ]
   }



Return Values
~~~~~~~~~~~~~

JSON-LD
```````

.. code-block:: json
   :linenos:

   {
     "@context": {
       "@vocab": "https://json-ld.opensupplyhub.org/contexts/contributor_list.jsonld",
       "list_id": "ContributorListID",
       "list_name": "ContributorListName"
     }
   }

Object Diagram
``````````````

.. uml:: 
   
   @startuml
   class contributor_list {
     list_id : int 
     list_name : str
   }
   @enduml