# TuK3

### Start local web server

* Create the file `static/api_key.json` with this content:
```
{
	"api_key": "YOUR_API_KEY"
}
```
* Replace `YOUR_API_KEY` with your Google Maps API key.
* Set `HANA_USER` and `HANA_PWD`environment variables
* Run `python server.py`
* Open http://localhost:9001 in a browser.
