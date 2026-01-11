# NordVPN_WireGuard
NordVPN WireGuard Configuration Generation

## Prerequisites

### Get Access Token
1.  Log in to your [NordAccount dashboard](https://my.nordaccount.com/dashboard/).
2.  Click on **NordVPN** in the services list.
3.  Scroll down to the **Manual setup** section and click **Set up NordVPN manually**.
4.  Verify your email address by entering the code sent to your email.
5.  Generate a new token in the **Access Token** tab.
6.  Copy and save this token. You will use it as the `ACCESS_TOKEN`.

### Country Code Format
If you specify a country, use the **2-letter ISO 3166-1 alpha-2 code** (e.g., `US`, `DE`, `GB`, `JP`).

You can use this command to check available country

```
curl --silent "https://api.nordvpn.com/v1/servers/countries" | jq --raw-output '.[].name, .[].code'
```

## Run with Docker (Recommended)

1.  **Build the Docker image:**
    ```bash
    docker build -t nordvpn-wireguard .
    ```

2.  **Run the container:**
    Replace `your_token` with your actual token. This command mounts the current directory to `/output` inside the container, so the configuration file is saved to your current folder.
    ```bash
    docker run --rm -v $(pwd):/output -e ACCESS_TOKEN="your_token" -e COUNTRY_CODE="us" nordvpn-wireguard
    ```

## Run from Source (Python)

1.  **Save the code:** Save the code as a Python file (e.g., `main.py`).
2.  **Install dependencies:** Open your terminal or command prompt and run:
    ```bash
    pip install requests python-dotenv
    ```
3.  **Create a `.env` file:**
    Create a file named `.env` in the same directory as the script and add your configuration:
    ```env
    ACCESS_TOKEN=your_token
    COUNTRY_CODE=us
    ```
    *   **`ACCESS_TOKEN`**: Use the token obtained in the **Prerequisites** section.
    *   **`COUNTRY_CODE` (optional)**: Use the 2-letter ISO code (e.g., "US"). If you don't set this, the program will fetch a general recommended server.

4.  **Run the program:** Execute the Python script:
    ```bash
    python main.py
    ```
    It will print the WireGuard configuration to your console and save it to a file (e.g., `yyyymmdd-nordvpn-us.conf`) in the current directory.

## Reference

  * https://gist.github.com/bluewalk/7b3db071c488c82c604baf76a42eaad3
