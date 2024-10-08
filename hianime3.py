from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import time
import requests

# Set up headless Chrome options
chrome_options = Options()

# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-infobars")  # Disable infobar "Chrome is being controlled by automated test software"
chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-javascript")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Inject JavaScript to disable DevTools detection
# driver.execute_script("""
#     // Overwrite DevTools detection
#     const originalFunction = Function.prototype.toString;
#     Function.prototype.toString = function() {
#         if (this === window.console.log) {
#             return 'function log() { [native code] }';
#         }
#         return originalFunction.call(this);
#     };
# """)

# Open the URL
driver.get("https://hianime.to/")

# Inject JavaScript to disable MobileDetect and devtoolsDetector
driver.execute_script("""
     if (window.devtoolsDetector) {
        // Overwrite the launch method to include a breakpoint
        window.devtoolsDetector.launch = function() {
            debugger;  // Breakpoint
            console.log('Breakpoint inserted in devtoolsDetector.launch');
        };
    }

    // Disable the devtools detection loop
    if (window.devtoolsDetector) {
        window.devtoolsDetector._detectLoop = function() {};
        window.devtoolsDetector._broadcast = function() {};
        console.log('DevTools detection has been disabled.');
    };
                      
    // Mock the checkers to prevent them from detecting anything
    if (window.devtoolsDetector && window.devtoolsDetector._checkers) {
        for (let checker of window.devtoolsDetector._checkers) {
            checker.isEnable = function() { return false; };
            checker.isOpen = function() { return false; };
        }
        console.log('DevTools checkers have been disabled.');
    };

    // Mock devtoolsDetector to prevent triggering of redirection
    window.devtoolsDetector = {
        addListener: function() {},  // Do nothing when addListener is called
        launch: function() {}  // Do nothing when launch is called
    };

    // Use setInterval to monitor changes to location.href and block redirection
    setInterval(() => {
        if (window.location.href.includes('/home')) {
            console.log('Redirect attempt blocked to:', window.location.href);
            window.stop();  // Stop the loading of the new page
            window.location.href = '';  // Clear the URL to prevent redirection
        }
    }, 1000);  // Check every second
""")

# Execute JavaScript to hide Selenium WebDriver signature
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

def request_interceptor(request):
    # Modify or block requests based on URL or headers
    if 'redirect' in request.url:
        request.abort()  # Abort the redirect request

driver.request_interceptor = request_interceptor

# Capture network requests and save the m3u8 URL to a file
# m3u8_url_found = False
# for request in driver.requests:

#     if request.response and '.m3u8' in request.url:
#         m3u8_url_found = True
#         with open("m3u8_url.txt", "w") as f:
#             f.write(f"m3u8 URL: {request.url}\n")
#         break  # Exit the loop once the m3u8 URL is found

# if not m3u8_url_found:
#     print("m3u8 URL not found before redirection.")

# Modify the closing part:
try:
    # Your existing code for opening URL, waiting, and capturing requests
    # After loading the page, wait for 10 seconds
    time.sleep(60)

finally:
    # Ensure the browser is closed properly
    driver.close()
    driver.quit()