#!/usr/bin/env python3
"""
Headless PyAutoGUI Wrapper
Automatically sets up Xvfb and handles PyAutoGUI execution in headless environments
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

class HeadlessPyAutoGUI:
    def __init__(self):
        self.xvfb_process = None
        self.script_args = sys.argv[1:]
        
    def setup_xvfb(self):
        """Setup Xvfb if needed"""
        # Only setup Xvfb if no display is available
        if 'DISPLAY' not in os.environ or not os.environ['DISPLAY']:
            print("🖥️ Setting up virtual display...")
            try:
                # Start Xvfb
                xvfb_cmd = ['Xvfb', ':99', '-screen', '0', '1920x1080x24']
                self.xvfb_process = subprocess.Popen(
                    xvfb_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                os.environ['DISPLAY'] = ':99'
                time.sleep(2)
                print("✅ Virtual display created")
            except Exception as e:
                print(f"❌ Failed to create virtual display: {e}")
                return False
        else:
            print(f"ℹ️ Using existing display: {os.environ['DISPLAY']}")
        return True
    
    def cleanup(self):
        """Cleanup resources"""
        if self.xvfb_process:
            print("🧹 Cleaning up virtual display...")
            try:
                self.xvfb_process.terminate()
                self.xvfb_process.wait(timeout=5)
            except:
                self.xvfb_process.kill()
    
    def run_script(self):
        """Run the PyAutoGUI script"""
        if not self.setup_xvfb():
            return False
        
        try:
            if self.script_args:
                # Run the script specified in arguments
                script_path = self.script_args[0]
                if Path(script_path).exists():
                    print(f"🚀 Running PyAutoGUI script: {script_path}")
                    # Import and run the script
                    sys.path.insert(0, str(Path(script_path).parent))
                    module_name = Path(script_path).stem
                    
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(module_name, script_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'main'):
                        module.main()
                    else:
                        print("⚠️ No main() function found in script")
                    
                    return True
                else:
                    print(f"❌ Script not found: {script_path}")
                    return False
            else:
                print("ℹ️ No script specified. Starting interactive mode...")
                print("This wrapper can be used as:")
                print("  headless_pyautogui.py script.py")
                return True
                
        except Exception as e:
            print(f"❌ Error running script: {e}")
            return False
        finally:
            self.cleanup()
    
    def run(self):
        """Main entry point"""
        try:
            return self.run_script()
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            return False
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            return False

if __name__ == "__main__":
    wrapper = HeadlessPyAutoGUI()
    success = wrapper.run()
    sys.exit(0 if success else 1)
