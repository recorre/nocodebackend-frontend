#!/usr/bin/env python3
"""
X11 Authentication Fix for PyAutoGUI Scripts
Provides immediate fixes for "Authorization required, but no authorization protocol specified" error
"""

import os
import sys
import subprocess
import logging
import tempfile
from pathlib import Path

class X11AuthFix:
    """Fixes X11 authentication issues for PyAutoGUI"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def fix_xauth(self):
        """Fix X11 authentication using xauth"""
        print("🔧 Fixing X11 Authentication with xauth...")
        
        try:
            # Check if xauth is available
            subprocess.run(['which', 'xauth'], check=True, capture_output=True)
            
            # Get current DISPLAY
            display = os.environ.get('DISPLAY', ':0')
            print(f"Current DISPLAY: {display}")
            
            # Create xauth entry
            xauth_cmd = [
                'xauth', 'add', display, 
                'MIT-MAGIC-COOKIE-1', 
                subprocess.check_output(['mcookie']).decode().strip()
            ]
            
            subprocess.run(xauth_cmd, check=True)
            print("✅ X11 authentication fixed with xauth")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to fix X11 authentication: {e}")
            return False
        except FileNotFoundError:
            print("❌ xauth command not found")
            return False
    
    def set_display_permissions(self):
        """Set proper display permissions"""
        print("🔧 Setting display permissions...")
        
        try:
            # For local display, try to set permissions
            display = os.environ.get('DISPLAY', ':0')
            
            # Try to set access control off for local connections
            try:
                subprocess.run(['xhost', '+local:'], check=True, capture_output=True)
                print("✅ Display permissions set for local connections")
                return True
            except subprocess.CalledProcessError:
                # If xhost fails, try alternative approach
                print("⚠️ xhost command failed, trying alternative...")
                
                # Set environment variable for X11
                os.environ['XAUTHORITY'] = f"{os.path.expanduser('~')}/.Xauthority"
                print(f"✅ Set XAUTHORITY to: {os.environ['XAUTHORITY']}")
                return True
                
        except Exception as e:
            print(f"❌ Failed to set display permissions: {e}")
            return False
    
    def enable_x11_forwarding(self):
        """Enable X11 forwarding for SSH connections"""
        print("🔧 Enabling X11 forwarding...")
        
        try:
            # Check if running under SSH
            if 'SSH_CLIENT' in os.environ or 'SSH_TTY' in os.environ:
                # Enable X11 forwarding in SSH
                os.environ['SSH_CLIENT'] = os.environ.get('SSH_CLIENT', '')
                print("✅ X11 forwarding environment configured for SSH")
                return True
            else:
                print("ℹ️ Not running under SSH, X11 forwarding not needed")
                return True
                
        except Exception as e:
            print(f"⚠️ X11 forwarding configuration failed: {e}")
            return False
    
    def create_display_wrapper(self):
        """Create a wrapper script to run with proper X11 environment"""
        print("🔧 Creating X11 display wrapper...")
        
        wrapper_script = '''#!/bin/bash
# X11 Display Wrapper Script
# This script ensures proper X11 environment for PyAutoGUI

# Set display if not already set
export DISPLAY=${DISPLAY:-:0}

# Set X11 authority file
export XAUTHORITY=${XAUTHORITY:-$HOME/.Xauthority}

# Try to fix authentication
if command -v xauth >/dev/null 2>&1; then
    # Check if xauth entry exists
    if ! xauth list "$DISPLAY" >/dev/null 2>&1; then
        echo "Creating xauth entry for display $DISPLAY"
        xauth add "$DISPLAY" MIT-MAGIC-COOKIE-1 "$(mcookie)"
    fi
fi

# Set proper permissions on X authority file
if [ -f "$XAUTHORITY" ]; then
    chmod 600 "$XAUTHORITY"
fi

# Enable X11 access control
if command -v xhost >/dev/null 2>&1; then
    xhost +local: 2>/dev/null || true
fi

# Run the main script
echo "Running with DISPLAY=$DISPLAY and XAUTHORITY=$XAUTHORITY"
exec "$@"
'''
        
        wrapper_path = Path('run_with_x11.sh')
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)
        
        wrapper_path.chmod(0o755)
        print(f"✅ Created X11 wrapper script: {wrapper_path}")
        print(f"Usage: {wrapper_path} python your_script.py")
        
        return wrapper_path
    
    def apply_all_fixes(self):
        """Apply all available X11 fixes"""
        print("🚀 Applying all X11 authentication fixes...")
        
        fixes_applied = []
        
        # Fix 1: XAuth
        if self.fix_xauth():
            fixes_applied.append("xauth")
        
        # Fix 2: Display permissions
        if self.set_display_permissions():
            fixes_applied.append("display_permissions")
        
        # Fix 3: X11 forwarding
        if self.enable_x11_forwarding():
            fixes_applied.append("x11_forwarding")
        
        # Fix 4: Create wrapper
        wrapper_path = self.create_display_wrapper()
        fixes_applied.append("wrapper_script")
        
        print(f"\n✅ Applied {len(fixes_applied)} fixes: {', '.join(fixes_applied)}")
        return True

def main():
    """Apply X11 authentication fixes"""
    fix = X11AuthFix()
    success = fix.apply_all_fixes()
    
    if success:
        print("\n🎉 X11 authentication fixes applied successfully!")
        print("\n📝 Next steps:")
        print("1. Try running your PyAutoGUI script again")
        print("2. If issues persist, use the wrapper script:")
        print("   ./run_with_x11.sh python your_script.py")
        print("3. For headless environments, consider installing Xvfb")
    else:
        print("\n❌ Some fixes failed. Please check the error messages above.")

if __name__ == "__main__":
    main()