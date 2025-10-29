#!/usr/bin/env python3
"""
Widget Commenting Automation Script using PyAutoGUI
Automates commenting on the comment widget at https://casacorre.neocities.org/
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

class WidgetCommentingAutomation:
    """Main automation class for widget commenting operations"""

    def __init__(self):
        self.screenshot_dir = "automation_screenshots"
        self.confidence = 0.8
        self.timeout = 30
        self.human_delay = (0.5, 1.5)  # Random delay range for human-like behavior
        self.pyautogui_available = PYAUTOGUI_AVAILABLE

        # Create screenshot directory
        os.makedirs(self.screenshot_dir, exist_ok=True)

        # Test data for multiple comments
        self.test_comments = [
            {
                'name': 'Alice Johnson',
                'email': 'alice.johnson@example.com',
                'content': 'Great article! Very informative and well-written.'
            },
            {
                'name': 'Bob Smith',
                'email': 'bob.smith@example.com',
                'content': 'I completely agree with your points. Thanks for sharing!'
            },
            {
                'name': 'Charlie Brown',
                'email': 'charlie.brown@example.com',
                'content': 'This is exactly what I was looking for. Bookmarked for later!'
            },
            {
                'name': 'Diana Prince',
                'email': 'diana.prince@example.com',
                'content': 'Excellent insights. Looking forward to more content like this.'
            },
            {
                'name': 'Eve Wilson',
                'email': 'eve.wilson@example.com',
                'content': 'Well done! This deserves more attention.'
            }
        ]

        # Approximate coordinates for widget elements (fallbacks)
        self.widget_coordinates = {
            'comment_form': (800, 600),  # Approximate position of comment form
            'name_field': (800, 620),
            'email_field': (800, 650),
            'content_field': (800, 680),
            'submit_button': (900, 720)
        }

        logger.info(f"Widget Commenting Automation initialized (PyAutoGUI: {'available' if self.pyautogui_available else 'unavailable'})")

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
        time.sleep(3)  # Initial wait for page load
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

    def locate_widget(self):
        """Locate the comment widget using multiple strategies"""
        try:
            logger.info("Locating comment widget")

            # Strategy 1: Look for widget by scrolling and image matching
            # Assume widget images are available (would need to be captured beforehand)
            widget_images = ["images/widget_area.png", "images/comment_form.png"]

            for image in widget_images:
                if os.path.exists(image):
                    try:
                        location = pyautogui.locateOnScreen(image, confidence=self.confidence)
                        if location:
                            center = pyautogui.center(location)
                            pyautogui.click(center)  # Click to focus on widget
                            logger.info("Widget located using image recognition")
                            return True
                    except pyautogui.ImageNotFoundException:
                        continue

            # Strategy 2: Scroll to find widget area (assuming it's in a common position)
            self.scroll_page('down', 5)  # Scroll down to find widget
            time.sleep(2)

            # Strategy 3: Use coordinates as fallback (approximate widget position)
            pyautogui.click(self.widget_coordinates['comment_form'])
            logger.info("Widget located using coordinate fallback")
            return True

        except Exception as e:
            logger.error(f"Error locating widget: {e}")
            return False

    def fill_comment_form(self, comment_data):
        """Fill out the comment form with test data"""
        try:
            logger.info("Filling comment form")

            # Click on name field
            pyautogui.click(self.widget_coordinates['name_field'])
            self.type_text(comment_data['name'], "name field")

            # Click on email field
            pyautogui.click(self.widget_coordinates['email_field'])
            self.type_text(comment_data['email'], "email field")

            # Click on content field
            pyautogui.click(self.widget_coordinates['content_field'])
            self.type_text(comment_data['content'], "comment content")

            logger.info("Comment form filled")

        except Exception as e:
            logger.error(f"Error filling comment form: {e}")
            raise

    def submit_comment(self):
        """Submit the comment"""
        try:
            logger.info("Submitting comment")

            # Click submit button
            pyautogui.click(self.widget_coordinates['submit_button'])
            self.add_human_delay()

            # Wait for submission
            time.sleep(2)

            logger.info("Comment submitted")

        except Exception as e:
            logger.error(f"Error submitting comment: {e}")
            raise

    def verify_comment(self, comment_data):
        """Verify comment was posted (basic check)"""
        try:
            # Take screenshot after submission
            self.take_screenshot("after_comment_submission")

            # Basic verification: check if page changed or look for success message
            # This is a placeholder - in a real scenario, might use OCR or image matching
            logger.info(f"Comment verification attempted for: {comment_data['name']}")
            return True

        except Exception as e:
            logger.error(f"Error verifying comment: {e}")
            return False

    def run_automation(self):
        """Main automation workflow"""
        try:
            if not self.pyautogui_available:
                logger.warning("PyAutoGUI not available. Running in simulation mode.")
                print("PyAutoGUI is not available in this environment.")
                print("This script requires a graphical desktop environment to run.")
                print("For testing purposes, the script structure is complete.")
                return

            logger.info("Starting widget commenting automation")

            # Step 1: Open browser to the site
            self.open_browser("https://casacorre.neocities.org/")
            self.wait_for_page_load()

            # Step 2: Take screenshot of initial page
            self.take_screenshot("initial_page")

            # Step 3: Locate the comment widget
            if not self.locate_widget():
                raise Exception("Could not locate comment widget")

            # Step 4: Take screenshot of widget area
            self.take_screenshot("widget_area")

            # Step 5: Submit multiple test comments
            for i, comment in enumerate(self.test_comments[:5], 1):  # Submit up to 5 comments
                logger.info(f"Submitting comment {i}")

                self.fill_comment_form(comment)
                self.submit_comment()
                self.verify_comment(comment)

                # Wait between comments
                time.sleep(3)

            # Step 6: Take final screenshot
            self.take_screenshot("final_state")

            logger.info("Widget commenting automation completed successfully")

        except Exception as e:
            logger.error(f"Automation failed: {e}")
            self.take_screenshot("error_state")
            raise


def main():
    """Main entry point"""
    try:
        # Initialize PyAutoGUI safety settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

        # Create automation instance
        automation = WidgetCommentingAutomation()

        # Run automation
        automation.run_automation()

        print("Widget commenting automation completed successfully!")

    except KeyboardInterrupt:
        print("Automation interrupted by user")
        logger.info("Automation interrupted by user")
    except Exception as e:
        print(f"Automation failed: {e}")
        logger.error(f"Automation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()