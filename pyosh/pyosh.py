"""pyosh Package for accessing the https://opensupplyhub.org API using python"""

__version__ = "0.1.0"

import os
import yaml
import requests
import json
import pandas as pd
import urllib

class OSH_API():
    """This is a class that wraps API access to https://opensupplyhub.org.

    Parameters
    ----------
    url: str, optional, default = "http://opensupplyhub.org"
       URL of endpoint to use, defaults to https://opensupplyhub.org
    token: str
       Access token to authenticate to the API
    """
    def __init__(self,url : str = "http://opensupplyhub.org",token : str = ""):
        result = {}
        self.header = {}
        
        if "OSH_URL" in os.environ.keys():
            self.url = os.environ["OSH_URL"]
        else:
            self.url = url
            
        if token > "":
            self.token = token
        elif "OSH_TOKEN" in os.environ.keys():
            self.token = os.environ["OSH_TOKEN"]
        elif os.path.exists("./env"):
            with open("./env","rt") as f:
                try:
                    self.token = yaml.load(f,yaml.Loader)["token"]
                except:
                    self.result = {"code":-1,"message":"could not find entry token in file .env"}
                    self.token = ""
                    return 
        elif os.path.exists("./env.yml"):
            with open("./env.yml","rt") as f:
                try:
                    self.token = yaml.load(f,yaml.Loader)["token"]
                except:
                    self.result = {"code":-1,"message":"could not find entry token in file .env.yml"}
                    self.token = ""
                    return
        else:
            self.result = {"code":-1,"message":"no valid token found"}
            self.token = ""
            return
        self.result = {"code":0,"message":"ok"}
        
        self.header = {
            "accept": "application/json",
            "Authorization": f"Token {self.token}"
        }
        
        self.countries = []
        self.countries_active_count = -1
        self.contributors = []
        
        return 
    
    
    def get_countries(self):
        """Get a list of country country codes and names
        
        Returns
        -------
        pandas.DataFrame   
           +-----------+---------------------------------+
           |column     | description                     |
           +===========+=================================+
           |iso_3166_2 | ISO 3166-2 Alpha-2 Country Code |
           +-----------+---------------------------------+
           |country    | ISO 3166 Country Name           |
           +-----------+---------------------------------+
        """
        
        r = requests.get(f"{self.url}/api/countries",headers=self.header)
        if r.ok:
            data = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.countries = data

        return pd.DataFrame(self.countries,columns=["iso_3166_2","country"])
            
        
    def get_countries_active_count(self):
        """Get a count of disctinct country codes used by active facilities.
        
        Returns
        -------
        active_count: int
           disctinct country codes used by active facilities
        """
        
        r = requests.get(f"{self.url}/api/countries/active_count",headers=self.header)
        if r.ok:
            data = int(json.loads(r.text)["count"])
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = -1
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.countries_active_count = data
        
        return data
    
    def get_contributors(self):
        """Get a list of contributors and their ID.
        
        Returns
        -------
        pandas.DataFrame with columns
        
        list_id: int
           the numeric ID of the list
        list_name: str
           the name of the list
        """
        
        r = requests.get(f"{self.url}/api/contributors",headers=self.header)
        if r.ok:
            data = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.contributors = data
        
        return pd.DataFrame(self.contributors,columns=["contributor_id","contributor_name"])
    
    
    def get_contributor_lists(self,contributor_id):
        """Get lists for specific contributor.
        
        Parameters
        ----------
        contributor_id: str, optional
           numeric contributor id
           
        Returns
        -------
        pandas.DataFrame with columns
        
        list_id: int
           the numeric ID of the list
        list_name: str
           the name of the list
        """
        
        r = requests.get(f"{self.url}/api/contributor-lists/?contributors={contributor_id}",headers=self.header)
        if r.ok:
            data = json.loads(r.text)
            self.result = {"code":0,"message":f"{r.status_code}"}
        else:
            data = []
            self.result = {"code":-1,"message":f"{r.status_code}"}
        self.contributors = data
        
        return pd.DataFrame(self.contributors,columns=["list_id","list_name"])
        
        pass
    
    
    def get_facilities(self,page=-1,pageSize=-1,q="",name="",contributors=-1,lists=-1,contributor_types="",combine_contributors=False,
                       countries="",boundary={},parent_company="",facility_type="",processing_type="",product_type="",number_of_workers="",
                       native_language_name="",detail=False,sectors=""):
        """Returns a list of facilities in GeoJSON format for a given query. (Maximum of 50 facilities per page if the detail parameter is fale or not specified, 10 if the detail parameter is true.)
        
        Parameters
        ----------
        page : integer, optional
           A page number within the paginated result set.
        pageSize : integer, optional
           Number of results to return per page.
        q : string, optional
           Facility Name or OS ID
        name : string, optional
           Facility Name (DEPRECATED; use `q` instead)
        contributors : integer, optional
           Contributor ID
        lists : integer, optional
           List ID
        contributor_types : string, optional
           Contributor Type
        countries : string, optional
           Country Code
        combine_contributors : string, optional
           Set this to "AND" if the results should contain facilities associated with ALL the specified contributors.
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
        pandas.DataFrame with columns
        
        os_id : string
           The OS ID
        lon : float
           Geo latitude
        lat : float
           Geo longitude
        name : string
           Facility name
        address : string
           Facility address
        country_code : string
           ISO 3166-2 Alpha country code
        country_name : string
           ISO 3166 Country name
        has_approved_claim : boolean
           Flag indicating if facility has been claimed by owner, manager, or other authorised person
        is_closed : boolean
           Flag indicating if facility has been closed (_True_), or is currently open (_False_)
        
        """
        
        parameters = []
         
        if page != -1:
            parameters.append(f"page={page}")
        if pageSize != -1:
            parameters.append(f"pageSize={pageSize}")
        if len(q) > 0:
            q = urllib.parse.quote_plus(q)
            parameters.append(f"q={q}")
        if len(name) > 0:
            name = urllib.parse.quote_plus(name)
            parameters.append(f"name={name}")
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
        if combine_contributors:
            parameters.append(f"combine_contributors={combine_contributors}")
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
            #print(request_url)
            r = requests.get(request_url,headers=self.header)
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
    
    
    def post_facilities(self,data={},name="",country_code="",sector="",number_of_workers="",facility_type="",
                        processing_type="",product_type="",parent_company_name="",native_language_name=""):
        """Add a single facility record
        """
        return
    
    def post_facilities_bulk(self,records=[]):
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
        
        r = requests.get(f"{self.url}/api/facilities/count",headers=self.header)
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
        
        r = requests.get(f"{self.url}/api/facilities/{osh_id}/",headers=self.header)
        if r.ok:
            data = json.loads(r.text)
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
                        for vv in v[kk]:
                            lines.append("|".join([f"{kkk}:{vvv}" for kkk,vvv in vv.items()]))
                        entry[f"{kk}_extended"] = "\n".join(lines).replace("lng:","lon:")
                elif return_extended_fields:
                    pass
                else:
                    entry[k] = v
            data = pd.DataFrame(entry,index=[0])
            
        else:
            data = pd.DataFrame()
            self.result = {"code":-1,"message":f"{r.status_code}"}
        
        return data
    
    
    def get_facility_processing_types(self):
        """/facility-processing-types/
        
        Returns
        -------
        facility_processing_types: list
           something
        """
        
        r = requests.get(f"{self.url}/api/facility-processing-types/",headers=self.header)
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
        
        r = requests.get(f"{self.url}/api/parent-companies/",headers=self.header)
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
        
        r = requests.get(f"{self.url}/api/product-types/",headers=self.header)
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
        
        r = requests.get(f"{self.url}/api/sectors/",headers=self.header)
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
        
        r = requests.get(f"{self.url}/api/workers-ranges/",headers=self.header)
        if r.ok:
            workers_range = json.loads(r.text)
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
