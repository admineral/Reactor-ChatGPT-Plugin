import json
import quart
import quart_cors
from quart import request
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

@app.post("/render-code")
async def render_code():
    request_data = await request.get_json(force=True)
    react_code = request_data.get('code')

    # Send the React code to the React app and get a screenshot URL
    res = requests.post('http://0.0.0.0:5001/get-screenshot', json={"code": react_code})
    screenshot_url = res.text

    logging.debug(f"react_code={react_code}")
    logging.debug(f"screenshot_url={screenshot_url}")

    return {'code': react_code, 'screenshot_url': screenshot_url}

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()

