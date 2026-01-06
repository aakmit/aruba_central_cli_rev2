import os
from pycentral import NewCentralBase

# Validate token file exists
token_file = "cnx_data.yaml"
if not os.path.exists(token_file):
    raise FileNotFoundError(
        f"Token file '{token_file}' not found. Please provide a valid token file."
    )

# Initialize NewCentralBase class with the token credentials for New Central/GLP
new_central_conn = NewCentralBase(
    token_info=token_file
)

print()
# GLP API Call
glp_resp = new_central_conn.command(
    api_method="GET", api_path="devices/v1/devices", app_name="glp"
)

print(glp_resp)