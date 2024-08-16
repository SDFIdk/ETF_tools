import urllib.parse
import netrc
import os
import sys

#STRAIGHT OUTTA CHATGPT!

def get_api_key(machine):
    """Retrieve API key from .netrc file."""
    secrets = netrc.netrc()
    info = secrets.authenticators(machine)
    if info:
        return info[2]
    else:
        raise ValueError(f"No API key found for {machine} in .netrc file")

def build_dmi_url(cell_id, start_datetime, end_datetime, parameter_id, time_resolution, bbox_crs="https://www.opengis.net/def/crs/OGC/1.3/CRS84"):
    """Build the DMI API URL from user inputs."""
    base_url = "https://dmigw.govcloud.dk/v2/climateData/bulk/10kmGridValue/items"
    
    query_params = {
        "cellId": cell_id,
        "datetime": f"{start_datetime}Z/{end_datetime}Z",
        "parameterId": parameter_id,
        "timeResolution": time_resolution,
        "bbox-crs": bbox_crs
    }
    
    api_key = get_api_key("dmigw.govcloud.dk")
    query_params["api-key"] = api_key
    
    url_parts = list(urllib.parse.urlparse(base_url))
    url_parts[4] = urllib.parse.urlencode(query_params)
    
    return urllib.parse.urlunparse(url_parts)

# Example usage:
cell_id = "10km_615_66"
start_datetime = "2023-01-01T00:00:00"
end_datetime = "2024-01-01T00:00:00"
parameter_id = "pot_evaporation_makkink"
time_resolution = "day"

url = build_dmi_url(cell_id, start_datetime, end_datetime, parameter_id, time_resolution)
print(url)

print('AAAA')
