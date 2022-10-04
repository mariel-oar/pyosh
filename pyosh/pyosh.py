"""pyosh Package for accessing the https://opensupplyhub.org API using python"""

__version__ = "0.1.0"

import os
import yaml
import requests
import json
import pandas as pd
import urllib
import time
from typing import Union
import io

class OSH_API():
    """This is a class that wraps API access to https://opensupplyhub.org.
       
        Example
        -------
        This is an example of a yaml configuration file which supplies a valid API endpoint URL, and an API token.
                
        .. code-block:: 
            
            OSH_URL: https://opensupplyhub.org
            OSH_TOKEN: 12345abcdef12345abcdef12345abcdef
       
    """
        
    def __init__(self, url : str = "http://opensupplyhub.org", token : str = "", 
                 path_to_env_yml : str = "", url_to_env_yml : str = "", 
                 check_token = False):
        """object generation method
        
        Parameters
        ----------
        url: str, optional, default = "http://opensupplyhub.org"
            URL of endpoint to use, defaults to https://opensupplyhub.org
        token: str, optional, default = ""
            Access token to authenticate to the API if not using any other method described in the `Authentication section <authentication.html>`_
        path_to_env_yml: str, optional, default = ""
            Path to yaml file containing access token and/or endpoint URL
        url_to_env_yml: str, optional, default = ""
            URL from where a text yaml file containing access token and/or endpoint URL can be downloaded
        check_token: bool, optional, default = False
            Whether to check API token validity during initialisation. Note this will cost one API call count.

        """
        result = {}
        self.header = {}
        credentials = {}
        
        if len(path_to_env_yml) > 0:
            with open(path_to_env_yml,"rt") as f:
                credentials = yaml.load(f,yaml.Loader)
        elif len(url_to_env_yml) > 0:
            try:
                r = requests.get(url_to_env_yml)
                credentials = yaml.load(io.StringIO(r.text),yaml.Loader)
            except:
                pass
        elif os.path.exists("./env.yml"):
            try:
                with open("./env.yml","rt") as f:
                    credentials = yaml.load(f,yaml.Loader)
            except:
                pass
        
        if "OSH_URL" in os.environ.keys():
            self.url = os.environ["OSH_URL"]
        elif "OSH_URL" in credentials.keys():
            self.url = credentials["OSH_URL"]
        else:
            self.url = url
            
        if "OSH_TOKEN" in os.environ.keys():
            self.token = os.environ["OSH_TOKEN"]
        elif "OSH_TOKEN" in credentials.keys():
            self.token = credentials["OSH_TOKEN"]
        else:
            self.token = token
         
        
        self.header = {
            "accept": "application/json",
            "Authorization": f"Token {self.token}"
        }
        
        self.last_api_call_epoch = -1
        self.last_api_call_duration = -1
        self.api_call_count = 0
        self.countries = []
        self.countries_active_count = -1
        self.contributors = []
        self.post_facility_results = {
            "NEW_FACILITY":1,
            "MATCHED":2,
            "POTENTIAL_MATCH":0,
            "ERROR_MATCHING":-1
        }
           
        # Check valid URL
        try:
            r = requests.get(f"{self.url}/health-check/",timeout=5)
            self.result = {"code":0,"message":"ok"}
            self.error = False
        except Exception as e:
            self.result = {"code":-1,"message":str(e)}
            self.error = True
            return
        
        # Check header/token validity
        if check_token:
            try:
                r = requests.get(f"{self.url}/api/facilities/count/",headers=self.header)
                self.api_call_count += 1
                if not r.ok:
                    self.result = {"code":r.status_code,"message":str(r)}
                    self.error = True
                else:
                    # Check everything is working
                    try:
                        facilites_count_json = json.loads(r.text)
                        facilites_count = facilites_count_json["count"]
                        self.result = {"code":0,"message":"ok"}
                        self.error = False
                    except Exception as e:
                        self.result = {"code":-1,"message":"JSON error: "+str(e)}
                        self.error = True
                        return
            except Exception as e:
                self.result = {"code":-1,"message":str(e)}
                self.error = True
                return
        
        return 
    
    
    
    def get_contributors(self) -> pd.DataFrame:
        """Get a list of contributors and their ID.
        
        Returns
        -------
        list(dict()) 
        
           A list of dictionaries.
        
           +-----------------+-----------------------------------+------+
           |column           | description                       | type |
           +=================+===================================+======+
           |contributor_id   | The numeric ID of the contributor | int  |
           +-----------------+-----------------------------------+------+
           |contributor_name | The name of the contributor       | str  |
           +-----------------+-----------------------------------+------+
        """
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/contributors",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        self.api_call_count += 1

        if r.ok:
            raw_data = json.loads(r.text)
            data = [{"contributor_id":cid,"contributor_name":con} for cid,con in raw_data]
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.contributors = data
        
        return data
        #return pd.DataFrame(self.contributors,columns=["contributor_id","contributor_name"])
    
    
    def get_contributor_lists(self,contributor_id : Union[int,str]) -> pd.DataFrame:
        """Get lists for specific contributor.
        
        Parameters
        ----------
        contributor_id: str
           numeric contributor id
           
        Returns
        -------
        pandas.DataFrame   
           +-----------+---------------------------------+------+
           |column     | description                     | type |
           +===========+=================================+======+
           |list_id    | The numeric ID of the list      | int  |
           +-----------+---------------------------------+------+
           |list_name  | The name of the list            | str  |
           +-----------+---------------------------------+------+
        """
        

        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/contributor-lists/?contributors={contributor_id}",headers=self.header)
        self.api_call_count += 1

        if r.ok:
            raw_data = json.loads(r.text)
            data = [{"list_id":cid,"list_name":con} for cid,con in raw_data]
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.contributors = data
        
        return data
        #return pd.DataFrame(self.contributors,columns=["list_id","list_name"])
            
    
    def get_contributor_embed_configs(self,contributor_id : Union[int,str]) -> pd.DataFrame:
        """Get embedded maps configuration for specific contributor.
        
        Parameters
        ----------
        contributor_id: str
           numeric contributor id
           
        Returns
        -------
        pandas.DataFrame   
           +-----------+---------------------------------+------+
           |column     | description                     | type |
           +===========+=================================+======+
           |list_id    | The numeric ID of the list      | int  |
           +-----------+---------------------------------+------+
           |list_name  | The name of the list            | str  |
           +-----------+---------------------------------+------+
        """
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/contributor-embed-configs/{contributor_id}/",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        
        if r.ok:
            data = json.loads(r.text)
            alldata = {}
            num_undefined = 1
            have_undefined = False
            for k,v in data.items():
                if k == 'embed_fields':
                    for embedded_field in v:
                        for column in ['display_name','visible','order','searchable']:
                            if len(embedded_field["column_name"]) ==  0: # ref  https://github.com/open-apparel-registry/open-apparel-registry/issues/2200
                                have_undefined = True
                                alldata[f'undefined_{num_undefined}_{column}'] = embedded_field[column]
                            else:
                                have_undefined = False
                                alldata[f'{embedded_field["column_name"]}_{column}'] = embedded_field[column]
                        if have_undefined:
                            num_undefined += 1
                            have_undefined = False
                elif k == 'extended_fields':
                    for i in range(len(v)):
                        alldata[f'{k}_{i}'] = v[i]
                else:
                    alldata[k] = [v]
            data = alldata
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        
        return data
        #return pd.DataFrame(data)
        

    
    def get_contributor_types(self) -> pd.DataFrame:
        """Get a list of contributor type choices. The original REST API returns a list of pairs of values and display names.
        As all display names and values are identical, we only return the values used in the database.
        
        Returns
        -------
        pandas.DataFrame   
           +-----------------+---------------------------------+------+
           |column           | description                     | type |
           +=================++================================+======+
           |contributor_type | The values of contributor types | str  |
           +-----------------+---------------------------------+------+
        """
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/contributor-types",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        
        if r.ok:
            data = [value for value,display in json.loads(r.text)]
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.contributors = data
        
        return pd.DataFrame(self.contributors,columns=["contributor_type"])
    
    
    def get_countries(self) -> pd.DataFrame:
        """Get a list of `ISO 3166-2 Alpha 2 country codes and English short names <https://www.iso.org/obp/ui/#search>` used. 
        
        Returns
        -------
        pandas.DataFrame   
           +-----------+---------------------------------+------+
           |column     | description                     | type |
           +===========+=================================+======+
           |iso_3166_2 | ISO 3166-2 Alpha-2 Country Code | str  |
           +-----------+---------------------------------+------+
           |country    | ISO 3166 Country Name           | str  |
           +-----------+---------------------------------+------+
        """
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/countries",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            data = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.countries = data

        return pd.DataFrame(self.countries,columns=["iso_3166_2","country"])
            
        
    def get_countries_active_count(self) -> int:
        """Get a count of disctinct country codes used by active facilities.
        
        Returns
        -------
        int
           disctinct country codes used by active facilities
        """
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/countries/active_count",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            data = int(json.loads(r.text)["count"])
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = -1
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.countries_active_count = data
        
        return data

    
    
    def get_facilities(self,page : int = -1, pageSize : int = -1, q : str = "", contributors : int = -1,
                       lists : int = -1, contributor_types : str = "", countries : str = "",
                       boundary : dict = {}, parent_company : str = "", facility_type : str = "",
                       processing_type : str = "", product_type : str = "", number_of_workers : str = "",
                       native_language_name : str = "", detail : bool =False, sectors : str = ""):
        """Returns a list of facilities in GeoJSON format for a given query. (Maximum of 50 facilities per page if the detail parameter is fale or not specified, 10 if the detail parameter is true.)
        
        Parameters
        ----------
        page : integer, optional
           A page number within the paginated result set.
        pageSize : integer, optional
           Number of results to return per page.
        q : string, optional
           Facility Name or OS ID
        contributors : integer, optional
           Contributor ID
        lists : integer, optional
           List ID
        contributor_types : string, optional
           Contributor Type
        countries : string, optional
           Country Code
        boundary : string, optional
           Pass a GeoJSON geometry to filter by facilities within the boundaries of that geometry.
        parent_company : string, optional
           Pass a Contributor ID or Contributor name to filter by facilities with that Parent Company.
        facility_type : string, optional
           Facility type
        processing_type : string, optional
           Processing type
        product_type : string, optional
           Product type
        number_of_workers : string, optional
           Submit one of several standardized ranges to filter by facilities with a number_of_workers matching those values. Options are: "Less than 1000", "1001-5000", "5001-10000", or "More than 10000".
        native_language_name : string, optional
           The native language name of the facility
        detail : boolean, optional
           Set this to true to return additional detail about contributors and extended fields with each result. setting this to true will make the response significantly slower to return.
        sectors : string, optional
           The sectors that this facility belongs to. Values must match those returned from the `GET /api/sectors` endpoint
           
        Returns
        -------
        pandas.DataFrame

            +------------------+-----------------------------------------------+-------+
            |column            | description                                   | type  |
            +==================+===============================================+=======+
            |os_id             | The OS ID                                     | str   |
            +------------------+-----------------------------------------------+-------+
            |lon               | Geographics longitude in degrees              | float |
            +------------------+-----------------------------------------------+-------+
            |lat               | Geographics latitude in degrees               | float |
            +------------------+-----------------------------------------------+-------+
            |name              | Facility name                                 | str   |
            +------------------+-----------------------------------------------+-------+
            |address           | Facility address                              | str   |
            +------------------+-----------------------------------------------+-------+
            |country_code      |`ISO 3166-2 Alpha country code                 | str   |
            |                  |<https://iso.org/obp/ui/#search/code/>`_       |       |
            +------------------+-----------------------------------------------+-------+
            |country_name      |`ISO 3166 country name                         | str   |
            |                  |<https://iso.org/obp/ui/#search/code/>`_       |       |
            +------------------+-----------------------------------------------+-------+
            |address           | Facility address                              | str   |
            +------------------+-----------------------------------------------+-------+
            |has_approved_claim| Flag indicating if facility has been claimed  | bool  |
            |                  |                                               |       |
            |                  | by owner, manager, or other authorised person |       |
            +------------------+-----------------------------------------------+-------+
            |is_closed         | Flag indicating if facility has been closed   | bool  |
            |                  |                                               |       |
            |                  | (*True*), or is currently open (*False*)      |       |
            +------------------+-----------------------------------------------+-------+
        """
        
        parameters = []
         
        if page != -1:
            parameters.append(f"page={page}")
        if pageSize != -1:
            parameters.append(f"pageSize={pageSize}")
        if len(q) > 0:
            q = urllib.parse.quote_plus(q)
            parameters.append(f"q={q}")
        if contributors != -1:
            parameters.append(f"contributors={contributors}")
        if lists != -1:
            parameters.append(f"lists={lists}")
        if len(contributor_types) > 0:
            contributor_types = urllib.parse.quote_plus(contributor_types)
            parameters.append(f"contributor_types={contributor_types}")
        if len(countries) > 0:
            countries = urllib.parse.quote_plus(countries)
            parameters.append(f"countries={countries}")
        if len(boundary.keys()) > 0:
            boundary = urllib.parse.quote_plus(str(boundary).replace(" ",""))
            parameters.append(f"boundary={boundary}")
        if len(parent_company) > 0:
            parent_company = urllib.parse.quote_plus(parent_company)
            parameters.append(f"parent_company={parent_company}")
        if len(facility_type) > 0:
            facility_type = urllib.parse.quote_plus(facility_type)
            parameters.append(f"facility_type={facility_type}")
        if len(processing_type) > 0:
            processing_type = urllib.parse.quote_plus(processing_type)
            parameters.append(f"processing_type={processing_type}")
        if len(product_type) > 0:
            product_type = urllib.parse.quote_plus(product_type)
            parameters.append(f"product_type={product_type}")
        if len(number_of_workers) > 0:
            number_of_workers = urllib.parse.quote_plus(number_of_workers)
            parameters.append(f"number_of_workers={number_of_workers}")
        if len(native_language_name) > 0:
            native_language_name = urllib.parse.quote_plus(native_language_name)
            parameters.append(f"native_language_name={native_language_name}")
        if detail:
            parameters.append(f"detail=true")
        else:
            parameters.append(f"detail=false")
        if len(sectors) > 0:
            sectors = urllib.parse.quote_plus(sectors)
            parameters.append(f"sectors={sectors}")
        
        parameters = "&".join(parameters)
        have_next = True
        request_url = f"{self.url}/api/facilities/?{parameters}"
        alldata = []
        
        while have_next:
            self.last_api_call_epoch = time.time()
            r = requests.get(request_url,headers=self.header)
            self.last_api_call_duration = time.time()-self.last_api_call_epoch
            if r.ok:
                data = json.loads(r.text)
                
                for entry in data["features"]:
                    new_entry = {
                        "os_id":entry["id"],
                        "lon":entry["geometry"]["coordinates"][0],
                        "lat":entry["geometry"]["coordinates"][1],
                    }
                    for k,v in entry["properties"].items():
                        if not k.startswith("ppe_"):
                            new_entry[k] = v
                    alldata.append(new_entry)
                    
                self.result = {"code":0,"message":f"{r.status_code}"}
                if 'next' in data.keys() and data["next"] is not None:
                    request_url = data["next"]
                else:
                    have_next = False
            else:
                data = []
                self.result = {"code":-1,"message":f"{r.status_code}"}
                have_next = False
        
        return pd.DataFrame(alldata)
    
    
    def _flatten_facilities_json(self,json_data):
        """Convert deep facility data to a flat key,value dict"""
        base_entry = {}
        for k,v in json_data.items():
            if k == "matches":
                continue
            elif k == "geocoded_geometry":
                try:
                    base_entry["lon"] = v["coordinates"][0]
                    base_entry["lat"] = v["coordinates"][1]
                except:
                    base_entry["lon"] = -1
                    base_entry["lat"] = -1
            else:
                if v is not None:
                    base_entry[k] = v
                else:
                    base_entry[k] = ""

        alldata = []
        if len(json_data["matches"])>0:
            match_no = 1
            for match in json_data["matches"]:
                new_data = {"match_no":match_no}
                new_data.update(base_entry)#.copy()
                for k,v in match.items():
                    if isinstance(v,list):
                        a = 1/0
                        pass
                    elif k in ["Feature","type"]:
                        pass
                    elif k == "geometry":
                        new_data["match_lon"] = v["coordinates"][0]
                        new_data["match_lat"] = v["coordinates"][1]
                    elif isinstance(v,dict):
                        for kk,vv in v.items():
                            if isinstance(vv,list):
                                if len(vv) == 0:
                                    new_data[f"match_{kk}"] = ""
                                else:
                                    lines = []
                                    for vvv in vv:
                                        lines.append("|".join([f"{kkkk}:{vvvv}" for kkkk,vvvv in vvv.items()]))
                                    new_data[f"match_{kk}"] = "\n".join(lines).replace("lng:","lon:")
                            elif isinstance(vv,dict):
                                for kkk,vvv in vv.items():
                                    lines = []
                                    for entry in vvv:
                                        if isinstance(entry,dict):
                                            lines.append("|".join([f"{kkkk}:{vvvv}" for kkkk,vvvv in entry.items()]))
                                        elif isinstance(entry,str):
                                            lines = [vvv]
                                        else:
                                            a = 1/0
                                    new_data[f"match_{kk}_{kkk}"] = "\n".join(lines).replace("lng:","lon:")
                                pass
                            elif kk.startswith("ppe_"):
                                continue
                            else:
                                new_data[f"match_{kk}"] = vv
                        pass
                    else:
                        new_data[f"match_{k}"] = v
                alldata.append(new_data)
                match_no += 1
        else:
            alldata.append(base_entry)
            
        return alldata
    
    
    def post_facilities(self, name : str = "", address : str = "", country : str = "", sector : str ="",
                        data : dict = {}, 
                        number_of_workers : str = "",facility_type : str = "",
                        processing_type : str = "", product_type : str = "",
                        parent_company_name : str = "", native_language_name : str = "",
                        create : bool = False, public : bool = True, textonlyfallback : bool = False) -> pd.DataFrame:
        """Add a single facility record.

        There are two ways supplying data, either via the ``name``, ``address``, ``country`` etc parameters,
        or as a dict via the ``data`` parameters, in which case the optional parameters would need
        to be the keys of the dictionary.



        Parameters
        ----------
        name : str
            Name of the facility
        address : str
            Complete address of the facility
        country : str, optional
            _description_, by default ""
        sector : str, optional
            _description_, by default ""
        data : dict, optional
            _description_, by default {}
        number_of_workers : str, optional
            _description_, by default ""
        facility_type : str, optional
            _description_, by default ""
        processing_type : str, optional
            _description_, by default ""
        product_type : str, optional
            _description_, by default ""
        parent_company_name : str, optional
            _description_, by default ""
        native_language_name : str, optional
            _description_, by default ""
        create : bool, optional
            _description_, by default False
        public : bool, optional
            _description_, by default True
        textonlyfallback : bool, optional
            _description_, by default False

        Returns
        -------
        something
        """
        if len(data) == 0:
            payload = {}
            
            if len(name)>0:
                payload["name"] = name.strip()
            else:
                self.result = {"code":-100,"message":"Error: Empty facility name given, we need a name."}
                return pd.DataFrame([])
            
            if len(address)>0:
                payload["address"] = address.strip()
            else:
                self.result = {"code":-101,"message":"Error: Empty address given, we need an address."}
                return pd.DataFrame([])
            
            if len(country)>0:
                payload["country"] = country.strip()
            else:
                self.result = {"code":-102,"message":"Error: Empty country name given, we need a country."}
                return pd.DataFrame([])
            
            if len(sector)>0:
                payload["sector"] = sector.strip()
            else:
                payload["sector"] = "Unspecified"

            if len(number_of_workers)>0:
                payload["number_of_workers"] = number_of_workers.strip()
                
            if len(facility_type)>0:
                payload["facility_type"] = facility_type.strip()
                
            if len(processing_type)>0:
                payload["processing_type"] = processing_type.strip()
                
            if len(product_type)>0:
                payload["product_type"] = product_type.strip()
                
            if len(parent_company_name)>0:
                payload["parent_company_name"] = parent_company_name.strip()
                
            if len(native_language_name)>0:
                payload["native_language_name"] = native_language_name.strip()
                
        else:
            payload = data
        
        parameters = "?"
        if create:
            parameters += "create=true"
        else:
            parameters += "create=false"
            
        if public:
            parameters += "&public=true"
        else:
            parameters += "&public=false"
            
        if textonlyfallback:
            parameters += "&textonlyfallback=true"
        else:
            parameters += "&textonlyfallback=false"
                  
        self.last_api_call_epoch = time.time()
        r = requests.post(f"{self.url}/api/facilities/?{parameters}",headers=self.header,data=payload)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            data = json.loads(r.text)
            data = self._flatten_facilities_json(data)
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = pd.DataFrame({"status":"HTTP_ERROR"})
            self.result = {"code":-1,"message":f"{r.status_code}"}    
                
        return pd.DataFrame(data)
    
    
    
    
    def post_facilities_bulk(self, records : list = [], dataframe : pd.DataFrame = pd.DataFrame([])) -> pd.DataFrame:
        """Add multiple records
        """
        return
    
    
    def get_facilities_count(self):
        """/facilities/count/
        
        Returns
        -------
        active_count: int
           disctinct country codes used by active facilities
        """
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/facilities/count",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            data = int(json.loads(r.text)["count"])
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = -1
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.countries_active_count = data
        
        return data
    
    
    def get_facility(self,osh_id : str, return_extended_fields : bool = False ):
        """/facilities/{id}/
        
        Parameters
        ----------
        osh_id: str
           sixteen character OS ID
        
        Returns
        -------
        active_count: int
           disctinct country codes used by active facilities
        """
        
        self.last_api_call_epoch = time.time()
        print(f"{self.url}/api/facilities/{osh_id}/")
        r = requests.get(f"{self.url}/api/facilities/{osh_id}/",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            data = json.loads(r.text)
            self.raw_result = data.copy()
            self.result = {"code":0,"message":f"{r.status_code}"}
            
            entry = {
                "id": data["id"],
                "lon": data["geometry"]["coordinates"][0],
                "lat": data["geometry"]["coordinates"][1]
            }
            for k,v in data["properties"].items():
                if k.startswith("ppe_"):
                    continue
                elif isinstance(v,list):
                    if len(v) > 0 and isinstance(v[0],dict):
                        lines = []
                        for vv in v:
                            lines.append("|".join([f"{kkk}:{vvv}" for kkk,vvv in vv.items()]))
                        entry[k] = "\n".join(lines).replace("lng:","lon:")
                    else:
                        entry[k] = "\n".join(v)
                elif k == "extended_fields" and return_extended_fields:
                    for kk in v.keys():
                        lines = []
                        for vv in v[kk]:
                            lines.append("|".join([f"{kkk}:{vvv}" for kkk,vvv in vv.items()]))
                        entry[f"{kk}_extended"] = "\n".join(lines).replace("lng:","lon:")
                    #self.v = v.copy()
                elif k == "created_from":
                    self.v = v.copy()
                    entry[k] = "|".join([f"{kkk}:{vvv}" for kkk,vvv in v.items()]) 
                elif k == "extended_fields" and not return_extended_fields:
                    pass
                else:
                    if v is not None:
                        entry[k] = v
                    else:
                        entry[k] = ""
            #data = pd.DataFrame(entry,index=[0])
            data = entry.copy()
            
        else:
            #data = pd.DataFrame()
            data = {}
            self.result = {"code":-1,"message":f"{r.status_code}"}
        
        return data
    
    
    def get_facility_processing_types(self):
        """/facility-processing-types/
        
        Returns
        -------
        facility_processing_types: list
           something
        """
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/facility-processing-types/",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            facility_processing_types = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
            alldata = []
            for facility_processing_type in facility_processing_types:
                for processingType in facility_processing_type["processingTypes"]:
                    alldata.append({
                        "facility_type":facility_processing_type["facilityType"],
                        "processing_type":processingType
                    })
            data = pd.DataFrame(alldata)
        else:
            data = pd.DataFrame(alldata)
            self.result = {"code":-1,"message":f"{r.status_code}"}
            
        self.facility_processing_types = data
        return data    
    
       
    def get_parent_companies(self):
        """/api/product-types/"""
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/parent-companies/",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            data = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.parent_companies = data

        return pd.DataFrame(self.parent_companies,columns=["key_or_something","parent_company"])
    
       
    def get_product_types(self):
        """/api/product-types/"""
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/product-types/",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            data = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.product_types = data

        return pd.DataFrame(self.product_types,columns=["product_type"])
        
    
       
    def get_sectors(self):
        """/api/sectors/"""
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/sectors/",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            data = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.sectors = data

        return pd.DataFrame(self.sectors,columns=["sectors"])
    

    def get_workers_ranges(self):
        """/api/workers-range/"""
        
        self.last_api_call_epoch = time.time()
        r = requests.get(f"{self.url}/api/workers-ranges/",headers=self.header)
        self.last_api_call_duration = time.time()-self.last_api_call_epoch
        if r.ok:
            workers_ranges = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
            alldata = []
            for workers_range in workers_ranges:
                if "-" in workers_range:
                    lower,upper = workers_range.split("-")
                elif "Less" in workers_range:
                    upper = workers_range.split(" ")[-1]
                    lower = 1
                elif "More" in workers_range:
                    lower = workers_range.split(" ")[-1]
                    upper = 999999
                else:
                    lower = -1
                    upper = -1
                alldata.append({
                    "workers_range":workers_range,
                    "lower":lower,
                    "upper":upper,
                })
            data = pd.DataFrame(alldata)
        else:
            data = pd.DataFrame({
                    "workers_range":[],
                    "lower":[],
                    "upper":[],
            })
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.workers_ranges = data

        return data
