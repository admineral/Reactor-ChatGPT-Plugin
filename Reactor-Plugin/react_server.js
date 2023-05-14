const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const Babel = require('@babel/standalone');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use('/public', express.static(path.join(__dirname, 'public'))); // serving static files

app.post('/get-screenshot', async (req, res) => {
  console.log('Received POST request at /get-screenshot');
  const currentCode = req.body.code;
  console.log(`Received code: ${currentCode}`);  // Log the received code
  try {
    console.log('Launching Puppeteer');
    const browser = await puppeteer.launch({
    headless: "new",args: ['--remote-debugging-port=9222']});

    console.log('Creating new page');
    const page = await browser.newPage();

    console.log('Setting page content');
    const babelResult = Babel.transform(currentCode, { presets: ['react'] });
    const transpiledCode = babelResult.code;
    const componentName = currentCode.split(/function |class /).pop().split('(')[0].trim();
    
    const html = `
      <!DOCTYPE html>
      <html>
        <head>
          <script src="https://unpkg.com/react/umd/react.development.js"></script>
          <script src="https://unpkg.com/react-dom/umd/react-dom.development.js"></script>
        </head>
        <body>
          <div id="root"></div>
          <script>
            ${transpiledCode}
            ReactDOM.render(React.createElement(${componentName}), document.getElementById('root'));
          </script>
        </body>
      </html>
    `;

    await page.setContent(html);
    console.log('Waiting for rendering');
    await page.waitForTimeout(3000);  // Wait for 3 seconds
    console.log('Taking screenshot');
    const element = await page.$("#root");
    const boundingBox = await element.boundingBox();  // Get the bounding box of the element
    console.log(`Element bounding box: ${JSON.stringify(boundingBox)}`);  // Log the bounding box
    await page.screenshot({path: 'public/screenshot.png'}); // Save screenshot in the public directory
  
    console.log('Closing browser');
    await browser.close();
    
    // Get the current timestamp
    const timestamp = Date.now();
  
    const screenshotUrl = `http://localhost:5001/public/screenshot.png?${timestamp}`;
    console.log(`Screenshot saved at ${screenshotUrl}`);  // Log the screenshot URL
    res.send(screenshotUrl); // Serve screenshot from the public directory
  } catch (e) {
    console.error(`Error: ${e.message}`);  // Log the error message
    res.send({error: e.message});
  }
});

app.get('/screenshot.png', (req, res) => {
  console.log('Received GET request at /screenshot.png');
  res.sendFile(path.join(__dirname, 'public/screenshot.png')); // Serve the screenshot from the public directory
});

app.listen(5001, () => {
  console.log('React app listening on port 5001');
});