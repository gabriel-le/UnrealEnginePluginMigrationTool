#!/bin/bash
echo "Building Unreal Plugin Migration Tool for macOS..."
echo ""

# Resolve Python (prefer active venv)
if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python"
else
    PYTHON="$(command -v python3)"
fi

# Build the application as a macOS app bundle
echo "Creating macOS application bundle..."
pyinstaller --name="UnrealPluginMigrationTool" \
    --onefile \
    --windowed \
    --osx-bundle-identifier="com.unrealpluginmigration.tool" \
    --collect-data flet \
    --collect-data flet_core \
    UnrealPluginMigrationTool.py

echo ""
if [ -d "dist/UnrealPluginMigrationTool.app" ]; then
    echo "Build successful!"
    echo "Application location: dist/UnrealPluginMigrationTool.app"
    echo ""
    echo "This is a macOS application bundle that can be distributed standalone."
    echo "You can drag the .app to your Applications folder or distribute it directly."
    echo ""
    echo "Note: Users may need to right-click and select 'Open' the first time"
    echo "to bypass Gatekeeper if the app is not signed."
elif [ -f "dist/UnrealPluginMigrationTool" ]; then
    echo "Build successful (single-file executable)!"
    echo "Executable location: dist/UnrealPluginMigrationTool"
    echo ""
    echo "You can run this directly from the terminal."
else
    echo "Build failed! Check the output above for errors."
fi
