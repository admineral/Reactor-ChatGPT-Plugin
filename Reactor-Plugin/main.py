#DOnt forget to add your OPENAI API KEY - LINE 89!!!

import json
import quart
import quart_cors
from quart import request
import openai
import requests
import re

import logging
logging.basicConfig(level=logging.DEBUG)

_INITIAL_CODE = """
function LandingPage() {
  const [buttonClicked, setButtonClicked] = React.useState(false);

  const handleButtonClick = () => {
    setButtonClicked(true);
  };

  const containerStyle = {
    backgroundImage: 'linear-gradient(to right, #6a11cb, #2575fc)',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    textAlign: 'center',
    padding: '2rem',
    color: 'white',
  };

  const buttonStyle = {
    background: 'white',
    color: 'blue',
    padding: '0.5rem 1rem',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 'bold',
    marginTop: '1rem',
  };

  return (
    <div style={containerStyle}>
      <h1>Welcome to Our Website</h1>
      <p>
        We provide top-notch services and solutions for our customers. Explore our offerings and find the best fit for your needs!
      </p>
      <button onClick={handleButtonClick} style={buttonStyle}>
        {buttonClicked ? 'Thanks for clicking!' : 'Learn More'}
      </button>
    </div>
  );
}
"""


app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Store the current state of the code.
_CURRENT_CODE = {}

@app.post("/generate-code")
async def generate_code():
    request_data = await request.get_json(force=True)
    user_input = request_data.get('prompt')
    username = request_data.get('username')  # Add this line
    current_code = _CURRENT_CODE.get(username, _INITIAL_CODE)



    logging.debug(f"username={username}")


    prompt = f"""
    I am using react-live to build a web application. My current code is:

    {current_code}.

    I'm trying to add a new feature or change it. Here's what I want to do:

    User: {user_input}

    ChatGPT, please provide me the code to achieve this, answer with full code:
    """

################################ ADD YOUR KEY HERE #################################
    openai.api_key = 'YOUR-OPENAI-API-KEY-HERE'
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
    

    if new_code:
        _CURRENT_CODE[username] = new_code  # Update the current code

    

    # Send the new code to the React app and get a screenshot URL
    res = requests.post('http://0.0.0.0:5001/get-screenshot', json={"code": new_code})
    screenshot_url = res.text

    logging.debug(f"new_code={new_code}")
    logging.debug(f"screenshot_url={screenshot_url}")

    return {'code': new_code, 'screenshot_url': screenshot_url}

@app.route("/Reactor/<string:username>", methods=["GET"])
async def get_initial_code(username):
    return quart.Response(response=json.dumps(_INITIAL_CODE), status=200)

@app.route("/current-code/<string:username>", methods=["GET"])
async def get_current_code(username):
    return quart.Response(response=json.dumps(_CURRENT_CODE.get(username, _INITIAL_CODE)), status=200)




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
