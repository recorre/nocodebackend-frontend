#!/bin/bash
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
