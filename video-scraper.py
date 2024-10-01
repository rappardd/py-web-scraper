from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the Chrome options to make Selenium harder to detect
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-browser-side-navigation")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-notifications")

# Enable logging for the DevTools protocol
capabilities = DesiredCapabilities.CHROME
capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

# Set up the Chrome driver
driver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

# Enable request interception (for blocking unwanted scripts)
driver.execute_cdp_cmd('Network.enable', {})
# driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["watch.min.js?v=3.4"]})

# Navigate to the webpage with the embedded video
driver.get('https://hianime.to/watch/berserk-1997-103?ep=3123?_debug=ok')

# Disable the devtoolsDetector function by overriding the addListener and launch methods
driver.execute_script("""
    if (window.devtoolsDetector) {
        devtoolsDetector.addListener = function() {};
        devtoolsDetector.launch = function() {};
    }
""")

# Run JavaScript to remove common redirect event listeners
driver.execute_script("""
    window.onbeforeunload = null;
    window.onunload = null;
    window.addEventListener('beforeunload', function(event) {
        event.preventDefault();
        event.stopImmediatePropagation();
    }, true);
    window.addEventListener('unload', function(event) {
        event.preventDefault();
        event.stopImmediatePropagation();
    }, true);
""")

# Override window.location.href to prevent the redirect
driver.execute_script("""
    Object.defineProperty(window, 'location', {
        configurable: true,
        enumerable: true,
        writable: true,
        value: { href: '' }
    });
""")

# Let the page load
time.sleep(60)

# Switch to the iframe by its ID
iframe = driver.find_element(By.ID, 'iframe-embed')
driver.switch_to.frame(iframe)

# Now inside the iframe, try to locate the video player or other elements
# Look for any video or media-related elements within the iframe
# Example: Sometimes the video src is in an <embed> or <source> tag
try:
    # This is just an example. Inspect the iframe for an actual video element.
    video_element = driver.find_element(By.TAG_NAME, 'video')
    video_url = video_element.get_attribute('src')
    print(f'Video URL: {video_url}')
except Exception as e:
    print("Could not find the video element:", e)

# If no direct video element is found, check if there's another nested iframe or redirect.


# Now you can use requests to download the video
import requests

r = requests.get(video_url, stream=True)
with open('video.mp4', 'wb') as f:
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)

# Optional: Analyze the performance logs for blocked/allowed scripts
logs = driver.get_log('performance')
for entry in logs:
    print(entry)

# Switch back to the default content (main page)
# driver.switch_to.default_content()

# Close the browser
# driver.quit()
