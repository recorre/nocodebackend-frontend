#!/usr/bin/env python3
"""
Headless X11 Solutions for PyAutoGUI
Provides long-term solutions for running PyAutoGUI in headless environments
"""

import os
import sys
import subprocess
import logging
import signal
from pathlib import Path
import time

class HeadlessX11Solution:
    """Provides solutions for headless X11 environments"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.xvfb_process = None
        
    def setup_xvfb(self, display=":99", resolution="1920x1080", color_depth="24"):
        """Setup Xvfb (X Virtual Framebuffer) for headless operation"""
        print(f"🖥️ Setting up Xvfb on display {display}...")
        
        try:
            # Check if Xvfb is available
            subprocess.run(['which', 'Xvfb'], check=True, capture_output=True)
            
            # Kill any existing Xvfb on the same display
            try:
                subprocess.run(['killall', 'Xvfb'], capture_output=True)
                time.sleep(1)
            except:
                pass
            
            # Start Xvfb
            xvfb_cmd = [
                'Xvfb', display, 
                '-screen', '0', f'{resolution}x{color_depth}'
            ]
            
            self.xvfb_process = subprocess.Popen(
                xvfb_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Set the DISPLAY environment variable
            os.environ['DISPLAY'] = display
            print(f"✅ Xvfb started on {display} with resolution {resolution}")
            
            # Wait for Xvfb to be ready
            time.sleep(2)
            
            return True
            
        except subprocess.CalledProcessError:
            print("❌ Xvfb not found. Install with: sudo apt-get install xvfb")
            return False
        except Exception as e:
            print(f"❌ Failed to start Xvfb: {e}")
            return False
    
    def setup_xvfb_with_x11_tools(self, display=":99"):
        """Setup Xvfb with additional X11 tools for better compatibility"""
        print(f"🔧 Setting up Xvfb with X11 tools on display {display}...")
        
        try:
            # Start Xvfb with extended options
            xvfb_cmd = [
                'Xvfb', display,
                '-screen', '0', '1920x1080x24',
                '+extension', 'RANDR',
                '+extension', 'GLX',
                '-render', 'std',
                '-reset', '-terminate'
            ]
            
            self.xvfb_process = subprocess.Popen(
                xvfb_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            os.environ['DISPLAY'] = display
            time.sleep(2)
            
            # Try to set up additional X11 tools
            tools_to_setup = ['xrandr', 'xset', 'xmodmap']
            for tool in tools_to_setup:
                try:
                    subprocess.run(['which', tool], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    print(f"⚠️ {tool} not available")
            
            # Set some default X11 settings
            try:
                subprocess.run(['xset', '-dpms'], capture_output=True)  # Disable power management
                subprocess.run(['xset', 's', 'off'], capture_output=True)  # Disable screen saver
                print("✅ X11 tools configured")
            except:
                print("⚠️ Some X11 tools configuration failed")
            
            print(f"✅ Xvfb setup completed on {display}")
            return True
            
        except Exception as e:
            print(f"❌ Xvfb setup failed: {e}")
            return False
    
    def cleanup_xvfb(self):
        """Cleanup Xvfb process"""
        if self.xvfb_process:
            print("🧹 Cleaning up Xvfb process...")
            try:
                self.xvfb_process.terminate()
                self.xvfb_process.wait(timeout=5)
                print("✅ Xvfb process terminated")
            except subprocess.TimeoutExpired:
                self.xvfb_process.kill()
                print("✅ Xvfb process killed")
            except Exception as e:
                print(f"⚠️ Error cleaning up Xvfb: {e}")
    
    def install_xvfb_if_needed(self):
        """Install Xvfb if not available"""
        print("📦 Checking Xvfb installation...")
        
        try:
            subprocess.run(['which', 'Xvfb'], check=True, capture_output=True)
            print("✅ Xvfb is already installed")
            return True
        except subprocess.CalledProcessError:
            print("⚠️ Xvfb not found. Attempting to install...")
            
            try:
                # Try to install Xvfb (requires sudo privileges)
                subprocess.run(['sudo', 'apt-get', 'update'], check=True, capture_output=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'xvfb'], check=True, capture_output=True)
                print("✅ Xvfb installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Xvfb: {e}")
                print("Please install manually: sudo apt-get install xvfb")
                return False
    
    def create_headless_wrapper(self):
        """Create a wrapper script for headless PyAutoGUI execution"""
        print("📝 Creating headless PyAutoGUI wrapper...")
        
        wrapper_script = '''#!/usr/bin/env python3
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
            print("\\n👋 Interrupted by user")
            return False
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            return False

if __name__ == "__main__":
    wrapper = HeadlessPyAutoGUI()
    success = wrapper.run()
    sys.exit(0 if success else 1)
'''
        
        wrapper_path = Path('headless_pyautogui.py')
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)
        
        wrapper_path.chmod(0o755)
        print(f"✅ Created headless wrapper: {wrapper_path}")
        print(f"Usage: {wrapper_path} widget_commenting_automation.py")
        
        return wrapper_path
    
    def create_docker_solution(self):
        """Create Docker-based solution"""
        print("🐳 Creating Docker-based solution...")
        
        dockerfile = '''# Use a Python base image with GUI support
FROM python:3.9-slim

# Install X11 and GUI dependencies
RUN apt-get update && apt-get install -y \\
    xvfb \\
    x11vnc \\
    xauth \\
    dbus-x11 \\
    x11-utils \\
    x11-xserver-utils \\
    libx11-6 \\
    libxext6 \\
    libxrender1 \\
    libxtst6 \\
    libxi6 \\
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install pyautogui Pillow

# Create app directory
WORKDIR /app

# Copy application files
COPY . .

# Create startup script
RUN echo '#!/bin/bash' > start.sh && \\
    echo 'Xvfb :99 -screen 0 1920x1080x24 &' >> start.sh && \\
    echo 'export DISPLAY=:99' >> start.sh && \\
    echo 'xhost +local:' >> start.sh && \\
    echo 'python "$@"' >> start.sh && \\
    chmod +x start.sh

# Set environment variables
ENV DISPLAY=:99
ENV QT_X11_NO_MITSHM=1

# Default command
CMD ["./start.sh"]
'''
        
        dockerfile_path = Path('Dockerfile.pyautogui')
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile)
        
        print(f"✅ Created Dockerfile: {dockerfile_path}")
        
        # Create docker-compose file
        compose_content = '''version: '3.8'
services:
  pyautogui:
    build:
      context: .
      dockerfile: Dockerfile.pyautogui
    environment:
      - DISPLAY=:99
      - QT_X11_NO_MITSHM=1
    volumes:
      - ./automation_screenshots:/app/screenshots
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
    network_mode: host
    command: python widget_commenting_automation.py
'''
        
        compose_path = Path('docker-compose.pyautogui.yml')
        with open(compose_path, 'w') as f:
            f.write(compose_content)
        
        print(f"✅ Created docker-compose file: {compose_path}")
        
        # Create run script
        run_script = '''#!/bin/bash
# Docker PyAutoGUI Runner

echo "🐳 Building PyAutoGUI Docker image..."
docker-compose -f docker-compose.pyautogui.yml build

echo "🚀 Running PyAutoGUI automation..."
docker-compose -f docker-compose.pyautogui.yml up --abort-on-container-exit

echo "🧹 Cleaning up..."
docker-compose -f docker-compose.pyautogui.yml down
'''
        
        run_path = Path('run_docker_automation.sh')
        with open(run_path, 'w') as f:
            f.write(run_script)
        run_path.chmod(0o755)
        
        print(f"✅ Created Docker runner: {run_path}")
        return True
    
    def setup_complete_headless_environment(self):
        """Setup a complete headless environment solution"""
        print("🚀 Setting up complete headless X11 environment...")
        
        solutions_created = []
        
        # Install Xvfb if needed
        if self.install_xvfb_if_needed():
            solutions_created.append("xvfb_installation")
        
        # Create headless wrapper
        wrapper_path = self.create_headless_wrapper()
        solutions_created.append("headless_wrapper")
        
        # Create Docker solution
        if self.create_docker_solution():
            solutions_created.append("docker_solution")
        
        # Create environment setup script
        self.create_env_setup_script()
        solutions_created.append("env_setup_script")
        
        print(f"\\n✅ Created {len(solutions_created)} headless solutions:")
        for solution in solutions_created:
            print(f"  • {solution}")
        
        return True
    
    def create_env_setup_script(self):
        """Create a script to setup the entire environment"""
        setup_script = '''#!/bin/bash
# Complete PyAutoGUI X11 Environment Setup

echo "🔧 Setting up PyAutoGUI X11 environment..."

# Install system packages
echo "📦 Installing system packages..."
sudo apt-get update
sudo apt-get install -y xvfb x11vnc xauth x11-utils

# Install Python packages
echo "🐍 Installing Python packages..."
pip install pyautogui Pillow python-xlib

# Setup X11 authentication
echo "🔐 Setting up X11 authentication..."
export DISPLAY=${DISPLAY:-:0}
xauth add "$DISPLAY" MIT-MAGIC-COOKIE-1 "$(mcookie)"
xhost +local:

# Create directories
mkdir -p automation_screenshots
mkdir -p logs

echo "✅ Environment setup completed!"
echo "🚀 Run your PyAutoGUI script with:"
echo "   ./headless_pyautogui.py your_script.py"
'''
        
        setup_path = Path('setup_pyautogui_env.sh')
        with open(setup_path, 'w') as f:
            f.write(setup_script)
        setup_path.chmod(0o755)
        
        print(f"✅ Created environment setup script: {setup_path}")

def main():
    """Main function"""
    solution = HeadlessX11Solution()
    solution.setup_complete_headless_environment()
    
    print("\\n🎉 Headless X11 solutions created!")
    print("\\n📋 Available solutions:")
    print("1. Virtual Display (Xvfb): Automatic setup with headless_pyautogui.py")
    print("2. Docker Solution: Containerized PyAutoGUI with docker-compose")
    print("3. Environment Setup: Complete setup with setup_pyautogui_env.sh")
    
    print("\\n📝 Usage examples:")
    print("• python headless_pyautogui.py widget_commenting_automation.py")
    print("• ./run_docker_automation.sh")
    print("• ./setup_pyautogui_env.sh")

if __name__ == "__main__":
    main()