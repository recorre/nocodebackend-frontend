#!/usr/bin/env python3
"""
Enhanced PyAutoGUI Script with Robust Error Handling
Updated widget_commenting_automation.py with comprehensive error handling and logging
"""

import time
import logging
import os
import sys
import random
import signal
import subprocess
import platform
import traceback
from datetime import datetime
from pathlib import Path

# Enhanced error handling for PyAutoGUI
PYAUTOGUI_AVAILABLE = False
pyautogui = None

# Try to import PyAutoGUI with enhanced error handling
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    print("✅ PyAutoGUI imported successfully")
except ImportError as e:
    print(f"⚠️ PyAutoGUI not available: {e}")
    print("🔧 Creating mock PyAutoGUI for graceful degradation...")
    
    # Enhanced mock for testing and development
    class MockPyAutoGUI:
        """Enhanced mock PyAutoGUI for environments without display"""
        
        def __init__(self):
            self.FAILSAFE = True
            self.PAUSE = 0.5
            self._screenshot_count = 0
            
        def screenshot(self, region=None):
            """Mock screenshot that creates a placeholder image"""
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a placeholder image
            img = Image.new('RGB', (1920, 1080), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            # Add placeholder text
            try:
                # Try to use a default font
                font = ImageFont.load_default()
            except:
                font = None
                
            text = f"Mock Screenshot #{self._screenshot_count + 1}"
            draw.text((50, 50), text, fill='black', font=font)
            
            if region:
                # Crop the image if region is specified
                img = img.crop((
                    region[0], region[1], 
                    region[0] + region[2], region[1] + region[3]
                ))
            
            self._screenshot_count += 1
            return img
            
        def click(self, x=None, y=None, clicks=1, interval=0.0, button='left', duration=0.0, tween=None):
            """Mock click operation"""
            print(f"🖱️ Mock click: ({x}, {y}) - {clicks}x - {button} button")
            
        def typewrite(self, message, interval=0.0):
            """Mock typing operation"""
            print(f"⌨️ Mock typing: '{message}'")
            
        def press(self, key, presses=1, interval=0.0):
            """Mock key press operation"""
            print(f"⌨️ Mock key press: {key} ({presses}x)")
            
        def scroll(self, clicks, x=None, y=None):
            """Mock scroll operation"""
            print(f"📜 Mock scroll: {clicks} clicks at ({x}, {y})")
            
        def locateOnScreen(self, image, confidence=0.8, grayscale=False, region=None):
            """Mock image location (always returns None)"""
            print(f"🔍 Mock image search: {image} (confidence: {confidence})")
            return None
            
        def locateCenterOnScreen(self, image, confidence=0.8, grayscale=False, region=None):
            """Mock image center location (always returns None)"""
            print(f"🎯 Mock center search: {image} (confidence: {confidence})")
            return None
            
        def center(self, location):
            """Mock center calculation"""
            if location:
                return (location[0] + location[2]//2, location[1] + location[3]//2)
            return (0, 0)
            
        def size(self):
            """Mock screen size"""
            return (1920, 1080)
            
        class ImageNotFoundException(Exception):
            """Mock image not found exception"""
            pass
            
        class FailSafeException(Exception):
            """Mock failsafe exception"""
            pass
    
    pyautogui = MockPyAutoGUI()
    print("✅ Mock PyAutoGUI created successfully")

# Configure enhanced logging
def setup_logging():
    """Setup comprehensive logging for the automation"""
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"automation_{timestamp}.log"
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler with colors (if colorama available)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Try to add color to console output
    try:
        from colorama import init, Fore, Back, Style
        init()
        class ColoredFormatter(logging.Formatter):
            COLORS = {
                'DEBUG': Style.DIM + Fore.BLUE,
                'INFO': Fore.GREEN,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.RED + Style.BRIGHT
            }
            
            def format(self, record):
                color = self.COLORS.get(record.levelname, '')
                if color:
                    record.levelname = color + record.levelname + Style.RESET_ALL
                return super().format(record)
        
        console_handler.setFormatter(ColoredFormatter())
    except ImportError:
        console_handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Create application logger
    app_logger = logging.getLogger('Automation')
    return app_logger, log_file

# Initialize logging
logger, log_file = setup_logging()

class AutomationError(Exception):
    """Custom exception for automation errors"""
    pass

class X11ConnectionError(AutomationError):
    """Exception for X11 connection issues"""
    pass

class DisplayNotAvailableError(AutomationError):
    """Exception when display is not available"""
    pass

class EnhancedWidgetCommentingAutomation:
    """Enhanced automation class with robust error handling"""
    
    def __init__(self, simulate_only=False):
        self.simulate_only = simulate_only
        self.screenshot_dir = Path("automation_screenshots")
        self.logs_dir = Path("logs")
        self.confidence = 0.8
        self.timeout = 30
        self.human_delay = (0.5, 1.5)
        self.pyautogui_available = PYAUTOGUI_AVAILABLE and not simulate_only
        
        # Create necessary directories
        self.screenshot_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Test data with enhanced validation
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
            }
        ]
        
        # Enhanced coordinate system with fallbacks
        self.widget_coordinates = {
            'comment_form': (800, 600),
            'name_field': (800, 620),
            'email_field': (800, 650),
            'content_field': (800, 680),
            'submit_button': (900, 720)
        }
        
        logger.info(f"Enhanced Automation initialized (PyAutoGUI: {'available' if self.pyautogui_available else 'mock/simulation'})")
        logger.info(f"Simulation mode: {simulate_only}")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        raise KeyboardInterrupt("Graceful shutdown initiated")
    
    def verify_display_connection(self):
        """Verify X11 display connection with detailed error reporting"""
        logger.info("Verifying display connection...")
        
        if not self.pyautogui_available:
            raise DisplayNotAvailableError("PyAutoGUI not available in this environment")
        
        try:
            # Test basic PyAutoGUI functionality
            screen_size = pyautogui.size()
            logger.info(f"✅ Display connection verified. Screen size: {screen_size}")
            return True
            
        except Exception as e:
            error_msg = f"Display connection failed: {e}"
            logger.error(error_msg)
            
            # Check for specific X11 errors
            if "Authorization required" in str(e):
                raise X11ConnectionError("X11 authorization failed - authentication protocol not specified")
            elif "Can't open display" in str(e):
                raise X11ConnectionError("Cannot open display - check DISPLAY environment variable")
            elif "No protocol specified" in str(e):
                raise X11ConnectionError("No X11 protocol specified - check X11 configuration")
            else:
                raise DisplayNotAvailableError(f"Unknown display error: {e}")
    
    def take_screenshot(self, name, include_timestamp=True):
        """Take a screenshot with enhanced error handling"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if include_timestamp:
                filename = f"{self.screenshot_dir}/{timestamp}_{name}.png"
            else:
                filename = f"{self.screenshot_dir}/{name}.png"
            
            # Take screenshot with error handling
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            logger.info(f"📸 Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to take screenshot '{name}': {e}")
            # Create a placeholder screenshot in case of error
            try:
                placeholder_path = f"{self.screenshot_dir}/error_{name}_{int(time.time())}.png"
                screenshot = pyautogui.screenshot()  # This should work with mock
                screenshot.save(placeholder_path)
                return placeholder_path
            except:
                logger.error("Failed to create placeholder screenshot")
                return None
    
    def safe_click(self, coordinates, description="element", timeout=10):
        """Perform a click operation with error recovery"""
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Attempting to click {description} at {coordinates} (attempt {attempt + 1})")
                
                # Verify coordinates are within screen bounds
                screen_width, screen_height = pyautogui.size()
                x, y = coordinates
                
                if 0 <= x <= screen_width and 0 <= y <= screen_height:
                    pyautogui.click(x, y)
                    self.add_human_delay()
                    logger.info(f"✅ Successfully clicked {description} at {coordinates}")
                    return True
                else:
                    raise ValueError(f"Coordinates {coordinates} are outside screen bounds ({screen_width}x{screen_height})")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Click attempt {attempt + 1} failed for {description}: {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retry with exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All click attempts failed for {description}")
        
        raise AutomationError(f"Failed to click {description} after {max_retries} attempts: {last_error}")
    
    def safe_type_text(self, text, description="text field", char_delay_range=(0.05, 0.15)):
        """Type text with enhanced error handling and human-like delays"""
        try:
            logger.info(f"Typing in {description}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            for char in text:
                pyautogui.typewrite(char)
                # Variable typing delay for human-like behavior
                delay = random.uniform(*char_delay_range)
                time.sleep(delay)
            
            self.add_human_delay()
            logger.info(f"✅ Successfully typed in {description}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to type in {description}: {e}")
            raise AutomationError(f"Text input failed for {description}: {e}")
    
    def wait_with_timeout(self, condition_func, timeout=30, description="condition"):
        """Wait for a condition with timeout and error handling"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    return True
            except Exception as e:
                logger.debug(f"Condition check failed: {e}")
            
            time.sleep(1)
        
        raise AutomationError(f"Timeout waiting for {description} after {timeout} seconds")
    
    def add_human_delay(self):
        """Add human-like delay between actions"""
        delay = random.uniform(*self.human_delay)
        time.sleep(delay)
    
    def open_browser_with_error_handling(self, url):
        """Open browser with comprehensive error handling"""
        try:
            logger.info(f"Opening browser to: {url}")
            
            if platform.system() == "Linux":
                browsers = ['firefox', 'chromium-browser', 'google-chrome', 'chrome']
                browser_cmd = None

                for browser in browsers:
                    try:
                        subprocess.run(['which', browser], check=True, capture_output=True)
                        browser_cmd = browser
                        logger.info(f"Found browser: {browser_cmd}")
                        break
                    except subprocess.CalledProcessError:
                        continue

                if not browser_cmd:
                    raise AutomationError("No supported browser found. Please install Firefox or Chrome.")

                # Open browser with error handling
                process = subprocess.Popen([browser_cmd, url])
                
                # Wait for browser to start
                time.sleep(5)
                
                # Check if browser process is still running
                if process.poll() is not None:
                    raise AutomationError(f"Browser {browser_cmd} failed to start")
                
                logger.info(f"✅ Browser {browser_cmd} opened successfully")

            elif platform.system() == "Windows":
                os.startfile(url)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', url])

        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            raise AutomationError(f"Browser automation failed: {e}")
    
    def run_enhanced_automation(self):
        """Run automation with comprehensive error handling and recovery"""
        try:
            logger.info("🚀 Starting enhanced widget commenting automation")
            
            # Step 1: Verify display connection
            try:
                self.verify_display_connection()
            except (X11ConnectionError, DisplayNotAvailableError) as e:
                logger.warning(f"Display issue detected: {e}")
                if self.simulate_only:
                    logger.info("Running in simulation mode due to display unavailability")
                else:
                    raise
            
            # Step 2: Open browser
            logger.info("Opening browser...")
            self.open_browser_with_error_handling("https://casacorre.neocities.org/")
            self.take_screenshot("browser_opened")
            
            # Step 3: Wait for page to load
            logger.info("Waiting for page to load...")
            time.sleep(3)
            self.take_screenshot("initial_page")
            
            # Step 4: Locate and interact with widget (simplified for demo)
            logger.info("Locating comment widget...")
            
            # For demo purposes, we'll use coordinate-based interaction
            # In a real scenario, you would use image recognition or DOM automation
            
            for i, comment_data in enumerate(self.test_comments, 1):
                try:
                    logger.info(f"Submitting comment {i} of {len(self.test_comments)}")
                    
                    # Fill comment form with error handling
                    self.safe_click(self.widget_coordinates['name_field'], "name field")
                    self.safe_type_text(comment_data['name'], "name field")
                    
                    self.safe_click(self.widget_coordinates['email_field'], "email field") 
                    self.safe_type_text(comment_data['email'], "email field")
                    
                    self.safe_click(self.widget_coordinates['content_field'], "content field")
                    self.safe_type_text(comment_data['content'], "comment content")
                    
                    # Submit comment
                    self.safe_click(self.widget_coordinates['submit_button'], "submit button")
                    
                    # Wait for submission
                    time.sleep(2)
                    self.take_screenshot(f"comment_submitted_{i}")
                    
                    logger.info(f"✅ Comment {i} submitted successfully")
                    
                except Exception as e:
                    logger.error(f"Failed to submit comment {i}: {e}")
                    self.take_screenshot(f"comment_error_{i}")
                    
                    # Continue with next comment instead of failing completely
                    continue
            
            # Final screenshot
            self.take_screenshot("automation_completed")
            logger.info("🎉 Enhanced automation completed successfully")
            
        except KeyboardInterrupt:
            logger.info("Automation interrupted by user")
            self.take_screenshot("automation_interrupted")
            raise
        except Exception as e:
            logger.error(f"Automation failed with unexpected error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.take_screenshot("automation_failed")
            raise AutomationError(f"Unexpected automation failure: {e}")

def main():
    """Enhanced main entry point with comprehensive error handling"""
    try:
        print("🔧 Enhanced PyAutoGUI Automation")
        print("="*50)
        
        # Check for command line arguments
        simulate_only = '--simulate' in sys.argv
        
        if simulate_only:
            print("🎭 Running in simulation mode (no actual GUI interactions)")
        
        # Initialize enhanced automation
        automation = EnhancedWidgetCommentingAutomation(simulate_only=simulate_only)
        
        # Run automation
        automation.run_enhanced_automation()
        
        print("✅ Enhanced automation completed successfully!")
        print(f"📋 Check logs in: {Path('logs')}")
        print(f"📸 Screenshots in: {Path('automation_screenshots')}")
        
    except KeyboardInterrupt:
        print("\n👋 Automation interrupted by user")
        logger.info("Automation interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except (X11ConnectionError, DisplayNotAvailableError) as e:
        print(f"\n❌ Display Error: {e}")
        print("\n💡 Suggested fixes:")
        print("1. Run the diagnostic tool: python x11_diagnostic_tool.py")
        print("2. Apply authentication fixes: python x11_auth_fix.py")
        print("3. Use headless solution: python headless_pyautogui.py your_script.py")
        print("4. Run in simulation mode: python enhanced_widget_automation.py --simulate")
        logger.error(f"Display error: {e}")
        sys.exit(1)
    except AutomationError as e:
        print(f"\n❌ Automation Error: {e}")
        logger.error(f"Automation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected Error: {e}")
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()