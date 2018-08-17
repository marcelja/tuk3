# Trends and Concepts 3
## In-Memory Trajectory Data Analysis


#### Start local web server

* Create the file `static/api_key.json` with this content:
```
{
	"api_key": "YOUR_API_KEY"
}
```
* Replace `YOUR_API_KEY` with your Google Maps API key (see *Get API key* if you don't have one).
* Install required python packages via: `pip install -r requirements.txt`
* Set `HANA_USER` and `HANA_PWD`environment variables
* Run `python server.py`
* Open http://localhost:9001 in a browser.


#### Get API key

In order to obtain an API key, follow the instructions below:

1. visit [https://console.cloud.google.com/google/maps-apis](https://console.cloud.google.com/google/maps-apis) + login with your Google account
2. Select a project or create a new one
3. Click on APIs in the left column
4. Click on Maps JavaScript API -> activate
5. Click on credentials -> create credentials -> API key -> Restrict key -> Save
