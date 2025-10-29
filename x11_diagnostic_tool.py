#!/usr/bin/env python3
"""
X11 Display Connection Diagnostic Tool
Diagnoses and provides solutions for PyAutoGUI X11 errors
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('x11_diagnostic_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class X11Diagnostic:
    """Diagnostic tool for X11 display connection issues"""
    
    def __init__(self):
        self.issues_found = []
        self.recommendations = []
        
    def check_display_environment(self):
        """Check DISPLAY environment variable and X11 availability"""
        print("\n🔍 Checking Display Environment...")
        
        # Check if DISPLAY is set
        display = os.environ.get('DISPLAY')
        if not display:
            self.issues_found.append("DISPLAY environment variable is not set")
            self.recommendations.append("Set DISPLAY environment variable (e.g., export DISPLAY=:0)")
            print("❌ DISPLAY environment variable is not set")
            return False
        else:
            print(f"✅ DISPLAY is set to: {display}")
            
        # Check if display is accessible
        try:
            result = subprocess.run(['xdpyinfo'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ X11 display is accessible")
                return True
            else:
                self.issues_found.append(f"X11 display {display} is not accessible")
                self.recommendations.append(f"Check if X11 server is running on display {display}")
                print(f"❌ X11 display {display} is not accessible")
                return False
        except FileNotFoundError:
            self.issues_found.append("xdpyinfo command not found")
            self.recommendations.append("Install X11 utilities (x11-utils package)")
            print("❌ xdpyinfo command not found - X11 utilities not installed")
            return False
        except subprocess.TimeoutExpired:
            self.issues_found.append("X11 display connection timeout")
            self.recommendations.append("Check X11 server status and network connectivity")
            print("❌ X11 display connection timeout")
            return False
        except Exception as e:
            self.issues_found.append(f"X11 connection error: {e}")
            self.recommendations.append("Verify X11 server is running and accessible")
            print(f"❌ X11 connection error: {e}")
            return False
    
    def check_x11_server(self):
        """Check if X11 server is running"""
        print("\n🖥️ Checking X11 Server Status...")
        
        # Check for common X11 servers
        x11_processes = []
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            x11_servers = ['Xorg', 'X', 'Xvfb', 'xinit']
            
            for server in x11_servers:
                if server in result.stdout:
                    x11_processes.append(server)
                    print(f"✅ Found {server} process")
            
            if not x11_processes:
                self.issues_found.append("No X11 server process found")
                self.recommendations.append("Start an X11 server (Xorg, Xvfb, or use --display flag)")
                print("❌ No X11 server process found")
                return False
                
        except Exception as e:
            self.issues_found.append(f"Error checking X11 processes: {e}")
            print(f"❌ Error checking X11 processes: {e}")
            return False
            
        return True
    
    def check_graphics_capabilities(self):
        """Check graphics and display capabilities"""
        print("\n🎮 Checking Graphics Capabilities...")
        
        # Check for graphics drivers
        try:
            result = subprocess.run(['lspci', '-v'], capture_output=True, text=True, timeout=5)
            if 'VGA' in result.stdout or 'Display' in result.stdout:
                print("✅ Graphics hardware detected")
            else:
                print("⚠️ No dedicated graphics hardware detected")
                self.recommendations.append("Consider using virtual display (Xvfb) for headless operation")
        except FileNotFoundError:
            print("⚠️ lspci not available - cannot check graphics hardware")
        except Exception as e:
            print(f"⚠️ Error checking graphics hardware: {e}")
        
        # Check for OpenGL
        try:
            result = subprocess.run(['glxinfo'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'OpenGL' in result.stdout:
                print("✅ OpenGL support detected")
            else:
                print("⚠️ OpenGL support not available")
                self.recommendations.append("Install graphics drivers and OpenGL support")
        except FileNotFoundError:
            print("⚠️ glxinfo not available - cannot check OpenGL support")
        except Exception as e:
            print(f"⚠️ Error checking OpenGL: {e}")
    
    def check_pyautogui_environment(self):
        """Check PyAutoGUI environment and dependencies"""
        print("\n🐍 Checking PyAutoGUI Environment...")
        
        # Check PyAutoGUI installation
        try:
            import pyautogui
            print("✅ PyAutoGUI is installed")
            
            # Check if Pillow is available (required for screenshots)
            try:
                from PIL import Image
                print("✅ Pillow (PIL) is available")
            except ImportError:
                self.issues_found.append("Pillow (PIL) not installed")
                self.recommendations.append("Install Pillow: pip install Pillow")
                print("❌ Pillow (PIL) not installed")
            
            # Test PyAutoGUI basic functionality
            try:
                # This will fail if no display is available
                pyautogui.size()
                print("✅ PyAutoGUI basic functionality works")
            except Exception as e:
                self.issues_found.append(f"PyAutoGUI basic test failed: {e}")
                self.recommendations.append("Fix X11 display connection or use headless alternatives")
                print(f"❌ PyAutoGUI basic test failed: {e}")
                
        except ImportError:
            self.issues_found.append("PyAutoGUI not installed")
            self.recommendations.append("Install PyAutoGUI: pip install pyautogui")
            print("❌ PyAutoGUI not installed")
        except Exception as e:
            self.issues_found.append(f"PyAutoGUI import error: {e}")
            print(f"❌ PyAutoGUI import error: {e}")
    
    def test_x11_connection(self):
        """Test direct X11 connection"""
        print("\n🔌 Testing X11 Connection...")
        
        try:
            import Xlib.display
            display = Xlib.display.Display()
            screen = display.screen()
            print("✅ Direct X11 connection successful")
            display.close()
            return True
        except ImportError:
            print("⚠️ python-xlib not available - cannot test direct X11 connection")
            self.recommendations.append("Install python-xlib for advanced X11 operations")
            return False
        except Exception as e:
            self.issues_found.append(f"Direct X11 connection failed: {e}")
            print(f"❌ Direct X11 connection failed: {e}")
            return False
    
    def check_headless_alternatives(self):
        """Check for headless alternatives"""
        print("\n🖥️ Checking Headless Alternatives...")
        
        # Check for Xvfb
        try:
            subprocess.run(['which', 'Xvfb'], check=True, capture_output=True)
            print("✅ Xvfb (X Virtual Framebuffer) is available")
            self.recommendations.append("Use Xvfb for headless operation: Xvfb :99 -screen 0 1920x1080x24")
        except subprocess.CalledProcessError:
            self.issues_found.append("Xvfb not available")
            self.recommendations.append("Install Xvfb for headless operation: apt-get install xvfb")
            print("❌ Xvfb not available")
        
        # Check for virtual display tools
        virtual_tools = ['vncserver', 'xrdp', 'x11vnc']
        for tool in virtual_tools:
            try:
                subprocess.run(['which', tool], check=True, capture_output=True)
                print(f"✅ {tool} is available")
            except subprocess.CalledProcessError:
                print(f"⚠️ {tool} not available")
    
    def run_diagnostics(self):
        """Run complete diagnostic suite"""
        print("🚀 Starting X11 Display Connection Diagnostics")
        print("="*50)
        
        # Run all diagnostic checks
        checks = [
            self.check_display_environment,
            self.check_x11_server,
            self.check_graphics_capabilities,
            self.check_pyautogui_environment,
            self.test_x11_connection,
            self.check_headless_alternatives
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                logger.error(f"Diagnostic check failed: {e}")
                print(f"❌ Diagnostic check failed: {e}")
        
        # Summary
        print("\n" + "="*50)
        print("📋 DIAGNOSTIC SUMMARY")
        print("="*50)
        
        if self.issues_found:
            print(f"\n❌ Issues Found ({len(self.issues_found)}):")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"  {i}. {issue}")
        else:
            print("\n✅ No major issues found")
        
        if self.recommendations:
            print(f"\n💡 Recommendations ({len(self.recommendations)}):")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
        
        return len(self.issues_found) == 0

def main():
    """Main diagnostic function"""
    try:
        diagnostic = X11Diagnostic()
        success = diagnostic.run_diagnostics()
        
        if success:
            print("\n🎉 All checks passed! PyAutoGUI should work correctly.")
        else:
            print("\n⚠️ Issues detected. Please review the recommendations above.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n👋 Diagnostic interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Diagnostic failed: {e}")
        logger.error(f"Diagnostic failed: {e}")
        return False

if __name__ == "__main__":
    main()