
#ADD YOUR KEY HERE
#LINE 55
#openai.api_key = 'YOUR-OPEN-AI-API-KEY-HERE'
############################################
import json
import quart
import quart_cors
from quart import request
import openai
import requests
import re

import logging
logging.basicConfig(level=logging.DEBUG)

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Store the current state of the code.
_CURRENT_CODE = {}

@app.post("/generate-code")
async def generate_code():
    request_data = await request.get_json(force=True)
    user_input = request_data.get('prompt')
    username = request_data.get('username')  # Add this line
    current_code = _CURRENT_CODE.get(username, "")


    logging.debug(f"username={username}")


    prompt = f"""
    I'm building a React web application and I need some help. My current code is:

    ```jsx
    const App = () => {{
        return (
            <div>
                <h1>Welcome to My Site</h1>
            </div>
        );
    }};.

    I'm trying to add a new feature or change it. Here's what I want to do:

    User: {user_input}

    ChatGPT, could you provide me with the complete React component code to achieve this? For example, if I wanted to create a component that displays a welcome message, I would expect something like this:
    Please include the entire component definition, including the 'const App = () => {{ ... }};' part, not just the JSX expression.
    """

    #ADD YOUR KEY HERE

    openai.api_key = 'YOUR-OPEN-AI-API-KEY-HERE'
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt= prompt,
        max_tokens=3000,
        temperature=0.2,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )


    new_code = response.choices[0].text.strip()
    if 'const App = () => {' not in new_code or '};' not in new_code:
        return {'error': 'The generated code is not a complete React component'}

    _CURRENT_CODE[username] = new_code  # Update the current code

    

    # Send the new code to the React app and get a screenshot URL
    res = requests.post('http://0.0.0.0:5001/get-screenshot', json={"code": new_code})
    screenshot_url = res.text

    logging.debug(f"new_code={new_code}")
    logging.debug(f"screenshot_url={screenshot_url}")

    return {'code': new_code, 'screenshot_url': screenshot_url}

@app.get("/Reactor/<string:username>")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)

@app.route("/current-code/<string:username>", methods=["GET"])
async def get_current_code(username):
    return quart.Response(response=json.dumps(_CURRENT_CODE.get(username, "")), status=200)
    
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
