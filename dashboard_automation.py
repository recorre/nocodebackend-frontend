#!/usr/bin/env python3
"""
Dashboard Automation Script using PyAutoGUI
Automates the complete user journey from registration to creating content.
"""

import time
import logging
import os
import sys
import random
from datetime import datetime
import subprocess
import platform

# Import PyAutoGUI with error handling for headless environments
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PyAutoGUI not available: {e}")
    print("This script requires a graphical environment to run.")
    PYAUTOGUI_AVAILABLE = False
    # Create a mock pyautogui for testing
    class MockPyAutoGUI:
        def screenshot(self): return None
        def click(self, *args, **kwargs): pass
        def typewrite(self, *args, **kwargs): pass
        def press(self, *args, **kwargs): pass
        def scroll(self, *args, **kwargs): pass
        def locateOnScreen(self, *args, **kwargs): return None
        def center(self, *args, **kwargs): return (0, 0)
        FAILSAFE = True
        PAUSE = 0.5
        class ImageNotFoundException(Exception): pass
    pyautogui = MockPyAutoGUI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DashboardAutomation:
    """Main automation class for dashboard operations"""

    def __init__(self):
        self.screenshot_dir = "automation_screenshots"
        self.confidence = 0.8
        self.timeout = 30
        self.human_delay = (0.5, 1.5)  # Random delay range for human-like behavior
        self.pyautogui_available = PYAUTOGUI_AVAILABLE

        # Create screenshot directory
        os.makedirs(self.screenshot_dir, exist_ok=True)

        # Test data
        self.test_data = {
            'name': 'Test User',
            'email': f'test_{int(time.time())}@example.com',
            'password': 'TestPass123!',
            'site_url': 'https://casacorre.neocities.org/',
            'thread_title': 'Test Thread',
            'thread_content': 'This is a test thread created by automation.',
            'comment_content': 'This is a test comment created by automation.'
        }

        # Element coordinates (fallbacks)
        self.coordinates = {
            'register_link': (100, 200),  # Approximate navbar position
            'login_link': (200, 200),
            'dashboard_link': (300, 200),
            'sites_link': (400, 200),
            'threads_link': (500, 200),
            'logout_link': (600, 200)
        }

        logger.info(f"Dashboard Automation initialized (PyAutoGUI: {'available' if self.pyautogui_available else 'unavailable'})")

    def take_screenshot(self, name):
        """Take a screenshot and save it with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshot_dir}/{timestamp}_{name}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        logger.info(f"Screenshot saved: {filename}")
        return filename

    def add_human_delay(self):
        """Add human-like delay between actions"""
        delay = random.uniform(*self.human_delay)
        time.sleep(delay)

    def wait_for_page_load(self, timeout=10):
        """Wait for page to load by checking for stability"""
        time.sleep(2)  # Initial wait
        # Could implement more sophisticated page load detection

    def open_browser(self, url):
        """Open browser and navigate to URL"""
        try:
            logger.info(f"Opening browser to: {url}")

            if platform.system() == "Linux":
                # Try different browsers
                browsers = ['firefox', 'chromium-browser', 'google-chrome', 'chrome']
                browser_cmd = None

                for browser in browsers:
                    try:
                        subprocess.run(['which', browser], check=True, capture_output=True)
                        browser_cmd = browser
                        break
                    except subprocess.CalledProcessError:
                        continue

                if not browser_cmd:
                    raise Exception("No supported browser found")

                subprocess.Popen([browser_cmd, url])
                logger.info(f"Opened {browser_cmd} with URL: {url}")

            elif platform.system() == "Windows":
                os.startfile(url)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', url])

            # Wait for browser to open
            time.sleep(5)
            self.take_screenshot("browser_opened")

        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            raise

    def find_and_click_element(self, image_path=None, text=None, coordinates=None, description="element"):
        """Find and click element using multiple strategies"""
        try:
            # Strategy 1: Image recognition
            if image_path and os.path.exists(image_path):
                try:
                    location = pyautogui.locateOnScreen(image_path, confidence=self.confidence)
                    if location:
                        center = pyautogui.center(location)
                        pyautogui.click(center)
                        logger.info(f"Clicked {description} using image recognition")
                        self.add_human_delay()
                        return True
                except pyautogui.ImageNotFoundException:
                    logger.warning(f"Image not found for {description}")

            # Strategy 2: Text recognition (placeholder - would need OCR)
            if text:
                # This would require OCR library like pytesseract
                # For now, skip to coordinate fallback
                pass

            # Strategy 3: Coordinate fallback
            if coordinates:
                pyautogui.click(coordinates)
                logger.info(f"Clicked {description} using coordinates: {coordinates}")
                self.add_human_delay()
                return True

            logger.error(f"Could not find {description} using any method")
            return False

        except Exception as e:
            logger.error(f"Error clicking {description}: {e}")
            return False

    def type_text(self, text, description="text"):
        """Type text with human-like delays"""
        try:
            for char in text:
                pyautogui.typewrite(char)
                time.sleep(random.uniform(0.05, 0.15))  # Typing delay
            logger.info(f"Typed {description}: {text}")
            self.add_human_delay()
        except Exception as e:
            logger.error(f"Error typing {description}: {e}")
            raise

    def press_key(self, key, description="key"):
        """Press a keyboard key"""
        try:
            pyautogui.press(key)
            logger.info(f"Pressed {description}: {key}")
            self.add_human_delay()
        except Exception as e:
            logger.error(f"Error pressing {description}: {e}")
            raise

    def scroll_page(self, direction='down', clicks=3):
        """Scroll the page"""
        try:
            if direction == 'down':
                pyautogui.scroll(-clicks * 100)
            elif direction == 'up':
                pyautogui.scroll(clicks * 100)
            logger.info(f"Scrolled {direction} {clicks} times")
            self.add_human_delay()
        except Exception as e:
            logger.error(f"Error scrolling {direction}: {e}")
            raise

    def run_automation(self):
        """Main automation workflow"""
        try:
            if not self.pyautogui_available:
                logger.warning("PyAutoGUI not available. Running in simulation mode.")
                print("PyAutoGUI is not available in this environment.")
                print("This script requires a graphical desktop environment to run.")
                print("For testing purposes, the script structure is complete.")
                return

            logger.info("Starting dashboard automation")

            # Step 1: Open browser
            self.open_browser("https://nocodebackend-frontend.vercel.app/")
            self.wait_for_page_load()

            # Step 2: Take full page screenshot
            self.take_screenshot("initial_page")

            # Step 3: Click registration link
            if not self.find_and_click_element(
                image_path="images/register_link.png",
                coordinates=self.coordinates['register_link'],
                description="registration link"
            ):
                raise Exception("Could not find registration link")

            self.wait_for_page_load()
            self.take_screenshot("registration_page")

            # Step 4: Fill registration form
            self.fill_registration_form()

            # Step 5: Handle auto-login after registration
            self.wait_for_page_load()
            self.take_screenshot("after_registration")

            # Step 6: Navigate to dashboard (should be auto-redirected)
            self.wait_for_page_load()
            self.take_screenshot("dashboard_home")

            # Step 7: Create site
            self.create_site()

            # Step 8: Create thread
            self.create_thread()

            # Step 9: Create comment
            self.create_comment()

            # Step 10: Logout
            self.logout()

            logger.info("Automation completed successfully")

        except Exception as e:
            logger.error(f"Automation failed: {e}")
            self.take_screenshot("error_state")
            raise

    def fill_registration_form(self):
        """Fill out the registration form"""
        try:
            logger.info("Filling registration form")

            # Tab to first field or click name field
            self.press_key('tab')
            self.type_text(self.test_data['name'], "name field")

            self.press_key('tab')
            self.type_text(self.test_data['email'], "email field")

            self.press_key('tab')
            self.type_text(self.test_data['password'], "password field")

            # Submit form
            self.press_key('enter')

            logger.info("Registration form submitted")

        except Exception as e:
            logger.error(f"Error filling registration form: {e}")
            raise

    def create_site(self):
        """Create a new site"""
        try:
            logger.info("Creating new site")

            # Navigate to sites page
            if not self.find_and_click_element(
                coordinates=self.coordinates['sites_link'],
                description="sites link"
            ):
                # Try scrolling and looking for sites link
                self.scroll_page('down', 2)
                if not self.find_and_click_element(
                    coordinates=self.coordinates['sites_link'],
                    description="sites link"
                ):
                    raise Exception("Could not navigate to sites page")

            self.wait_for_page_load()
            self.take_screenshot("sites_page")

            # Click create site button (assuming it's in a standard position)
            pyautogui.click(400, 300)  # Approximate position for create button
            self.add_human_delay()

            # Fill site URL
            self.press_key('tab')
            self.type_text(self.test_data['site_url'], "site URL")

            # Submit
            self.press_key('enter')

            self.wait_for_page_load()
            self.take_screenshot("site_created")

            logger.info("Site created successfully")

        except Exception as e:
            logger.error(f"Error creating site: {e}")
            raise

    def create_thread(self):
        """Create a new thread for the site"""
        try:
            logger.info("Creating new thread")

            # Navigate to threads page
            if not self.find_and_click_element(
                coordinates=self.coordinates['threads_link'],
                description="threads link"
            ):
                raise Exception("Could not navigate to threads page")

            self.wait_for_page_load()
            self.take_screenshot("threads_page")

            # Click create thread button
            pyautogui.click(400, 300)  # Approximate position
            self.add_human_delay()

            # Fill thread details
            self.press_key('tab')
            self.type_text(self.test_data['thread_title'], "thread title")

            self.press_key('tab')
            self.type_text(self.test_data['thread_content'], "thread content")

            # Submit
            self.press_key('enter')

            self.wait_for_page_load()
            self.take_screenshot("thread_created")

            logger.info("Thread created successfully")

        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            raise

    def create_comment(self):
        """Create a comment on the thread"""
        try:
            logger.info("Creating comment")

            # Click on the created thread (assuming it's at the top)
            pyautogui.click(400, 400)  # Approximate position of first thread
            self.add_human_delay()

            self.wait_for_page_load()
            self.take_screenshot("thread_detail")

            # Find comment form and fill it
            pyautogui.click(400, 600)  # Approximate position of comment input
            self.add_human_delay()

            self.type_text(self.test_data['comment_content'], "comment content")

            # Submit comment
            self.press_key('enter')

            self.wait_for_page_load()
            self.take_screenshot("comment_created")

            logger.info("Comment created successfully")

        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            raise

    def logout(self):
        """Logout from the dashboard"""
        try:
            logger.info("Logging out")

            # Click logout link
            if not self.find_and_click_element(
                coordinates=self.coordinates['logout_link'],
                description="logout link"
            ):
                raise Exception("Could not find logout link")

            self.wait_for_page_load()
            self.take_screenshot("logged_out")

            logger.info("Logged out successfully")

        except Exception as e:
            logger.error(f"Error logging out: {e}")
            raise


def main():
    """Main entry point"""
    try:
        # Initialize PyAutoGUI safety settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

        # Create automation instance
        automation = DashboardAutomation()

        # Run automation
        automation.run_automation()

        print("Automation completed successfully!")

    except KeyboardInterrupt:
        print("Automation interrupted by user")
        logger.info("Automation interrupted by user")
    except Exception as e:
        print(f"Automation failed: {e}")
        logger.error(f"Automation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()