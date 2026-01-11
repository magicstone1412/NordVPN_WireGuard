import os
import requests
import json
import datetime
from dotenv import load_dotenv


def get_nordvpn_wireguard_config ():
    """
    Fetches NordVPN WireGuard configuration details and generates a .conf file content.
    Uses ACCESS_TOKEN and optionally COUNTRY_CODE from environment variables.
    """
    # 1. Get ACCESS_TOKEN from environment variable
    access_token = os.getenv ( "ACCESS_TOKEN" )
    if not access_token:
        print ( "Error: ACCESS_TOKEN environment variable not set. Please set it before running." )
        return None

    # 2. Fetching the Private Key
    private_key_url = "https://api.nordvpn.com/v1/users/services/credentials"
    try:
        private_key_response = requests.get ( private_key_url, auth=("token", access_token) )
        private_key_response.raise_for_status ()  # Raise an exception for HTTP errors (4xx or 5xx)
        private_key_data = private_key_response.json ()
        private_key = private_key_data.get ( "nordlynx_private_key" )

        if not private_key:
            print ( "Error: Could not retrieve NordLynx private key from the API response." )
            print ( f"API Response: {private_key_data}" )
            return None
    except requests.exceptions.RequestException as e:
        print ( f"Error fetching private key: {e}" )
        return None
    except json.JSONDecodeError:
        print ( f"Error decoding JSON response for private key. Response text: {private_key_response.text}" )
        return None

    # 3. Fetching the Server Information
    country_code = os.getenv ( "COUNTRY_CODE" )
    server_info_url = "https://api.nordvpn.com/v1/servers/recommendations"

    params = {
        "filters[servers_technologies][identifier]": "wireguard_udp",
        "limit": 1
    }

    if country_code:
        try:
            countries_resp = requests.get("https://api.nordvpn.com/v1/servers/countries")
            countries_resp.raise_for_status()
            countries = countries_resp.json()
            country_id = next((c.get('id') for c in countries if c.get('code', '').lower() == country_code.lower()), None)

            if country_id:
                params["filters[country_id]"] = country_id
                print(f"Fetching server for country code: {country_code} (ID: {country_id})")
            else:
                print(f"Error: Country code '{country_code}' not found.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching countries: {e}")
            return None
    else:
        print ( "No COUNTRY_CODE provided. Fetching recommended server." )

    try:
        server_info_response = requests.get ( server_info_url, params=params )
        server_info_response.raise_for_status ()
        server_info_data = server_info_response.json ()

        if not server_info_data:
            print (
                f"Error: No server information found for country code '{country_code}'." if country_code else "Error: No recommended server information found." )
            return None

        server = server_info_data [ 0 ]
        hostname = server.get ( "hostname" )
        endpoint = server.get ( "station" )

        public_key = None
        for tech in server.get ( "technologies", [ ] ):
            if tech.get ( "identifier" ) == "wireguard_udp":
                for metadata in tech.get ( "metadata", [ ] ):
                    if metadata.get ( "name" ) == "public_key":
                        public_key = metadata.get ( "value" )
                        break
            if public_key:  # Break outer loop once public_key is found
                break

        if not all ( [ hostname, endpoint, public_key ] ):
            print ( "Error: Missing essential server details (hostname, endpoint, or public key) in the API response." )
            print ( f"Server data received: {server}" )
            return None

    except requests.exceptions.RequestException as e:
        print ( f"Error fetching server information: {e}" )
        return None
    except json.JSONDecodeError:
        print ( f"Error decoding JSON response for server information. Response text: {server_info_response.text}" )
        return None

    # 4. Create config file content
    config_content = f"""[Interface]
PrivateKey = {private_key}
Address = 10.5.0.2/32
DNS = 1.1.1.1

[Peer]
PublicKey = {public_key}
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = {endpoint}:51820
"""
    return config_content


if __name__ == "__main__":
    load_dotenv()
    wireguard_config = get_nordvpn_wireguard_config ()
    if wireguard_config:
        print ( "\n--- NordVPN WireGuard Configuration ---" )
        print ( wireguard_config )
        print ( "---------------------------------------" )

        # Save to a file
        country_code = os.getenv("COUNTRY_CODE")
        if not country_code:
            country_code = "recommended"
        date_str = datetime.datetime.now().strftime("%Y%m%d")

        # Determine output directory (defaults to current directory if not set)
        output_dir = os.getenv("OUTPUT_DIR", ".")
        if output_dir != "." and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = os.path.join(output_dir, f"{date_str}-nordvpn-{country_code}.conf")
        try:
            with open(filename, "w") as f:
                f.write(wireguard_config)
            print(f"\nConfiguration successfully saved to {filename}")
        except IOError as e:
            print(f"Error saving configuration to file: {e}")