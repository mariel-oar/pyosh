import pytest
import pyosh 

@pytest.fixture(scope='module')
def vcr_config():
    return {
        "filter_headers": [('authorization', 'HIDETOKEN')],
    }
    
osh_api = pyosh.OSH_API()

@pytest.mark.vcr()
def test_post_facilities_match():
    global osh_api
    result = osh_api.post_facilities(
        name="Rudolf-Diesel Gymnasium",
        country="DE",
        address="Peterhofstraße 9, 86163 Augsburg"
    )

@pytest.mark.vcr()
def test_post_facilities_potential_match():
    global osh_api
    result = osh_api.post_facilities(
        name="Birkenau Grundschule",
        country="DE",
        address="Soldnerstraße 35, 86167 Augsburg"
    )

@pytest.mark.vcr()
def test_post_facilities_new():
    global osh_api
    result = osh_api.post_facilities(
        name="Deedeldee",
        country="DE",
        address="Linke Brandstr. 21, 86165 Augsburg"
    )
