# Unreal Engine Plugin Migration Tool

A Python application that provides a graphical interface for migrating Unreal Engine plugins between different engine versions. This tool is essentially a UI wrapper around Unreal Engine's built-in Automation Tool (UAT), making the plugin migration process much easier and more visual.

## What This Tool Does

This application helps you recompile Unreal Engine plugins for different engine versions. Instead of manually running complex command-line commands, you can use this simple interface to:

- Select your plugin file (.uplugin)
- Choose where to save the migrated plugin
- Pick your target Unreal Engine version
- Watch the migration process in real-time
- Get clear feedback on success or failure

## What's New in Version 3.0

Version 3.0 is a complete rewrite from the ground up. The original version (1.0/2.0) was a simple functional script with about 144 lines of code. Version 3.0 expands this to 437 lines with significantly more features and polish.

### Major Changes from Version 1.0/2.0

**Architecture**

- Old: Simple procedural code with functions
- New: Object-oriented class-based architecture (UnrealPluginMigrationApp class)
- Old: 144 lines of code
- New: 437 lines with better organization and maintainability for those who are forking

**User Interface**

- Old: Basic rows with text labels showing selected paths
- New: Professional card-based layout with labeled text fields
- Old: Simple theme toggle switch
- New: Icon button theme toggle with visual feedback
- Old: No visual feedback on selections
- New: Color-coded borders (green for valid, red for errors, blue for normal)
- Old: Fixed window size
- New: Responsive layout that adapts to window size without scrolling

**Console Output**

- Old: No console output visible in UI (only in terminal)
- New: Dedicated console output section with real-time streaming
- Old: No way to see what UAT is doing
- New: Watch every line of output as it happens

**Validation and Error Handling**

- Old: Basic try-catch with generic error dialogs
- New: Comprehensive validation before migration starts
- Old: No field validation
- New: Checks for missing fields and highlights them in red
- Old: No path verification
- New: Verifies RunUAT.bat exists before starting
- Old: Generic "something went wrong" messages
- New: Detailed error messages with specific information

**User Feedback**

- Old: Small text status (if any)
- New: Large, bold status messages that are impossible to miss
- Old: Basic alert dialogs
- New: Modal dialogs with detailed success/failure information
- Old: No progress indication
- New: Progress bar and status text during migration
- Old: No snackbar notifications
- New: Quick snackbar alerts for validation errors

**Processing**

- Old: Blocking subprocess.run() - UI freezes during migration
- New: Async/await with asyncio - UI stays responsive
- Old: No real-time output
- New: Streams output line-by-line as it happens
- Old: Simple subprocess execution
- New: Proper async subprocess management with error handling

**Code Quality**

- Old: String formatting with raw strings
- New: Pathlib for robust path handling
- Old: Minimal error handling
- New: Comprehensive try-catch blocks with specific error messages
- Old: No state management
- New: Proper state tracking (is_migrating, paths, etc.)
- Old: Direct UI updates
- New: Centralized update methods with logging

## Installation

### Option 1: Download Pre-built Executable (Recommended)

Download the latest `.exe` file from the [Releases page](https://github.com/mickexd/UnrealEnginePluginMigrationTool/releases). No installation required - just run it!
You might need to add an exception to your antivirus, don't worry it's safe (read the code)

### Option 2: Run from Source

You'll need Python 3.8 or higher installed on your system.

Install dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install flet pyinstaller
```

Run the application:

```bash
python UnrealPluginMigrationTool.py
```

### Option 3: Build Your Own Executable

If you want to build the executable yourself:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the build script:

```bash
build.bat
```

3. Find the executable in the `dist` folder

The build script uses PyInstaller to create a single-file executable that can be distributed without Python installed.

## How to Use

1. **Select Your Plugin**

   - Click the folder icon next to "Source .uplugin File"
   - Find and select the plugin you want to migrate
   - The field turns green when selected

2. **Choose Destination**

   - Click the folder icon next to "Destination Folder"
   - Pick where you want the migrated plugin saved
   - The tool creates a "Migrated" subfolder automatically

3. **Select Unreal Engine Version**

   - Click the folder icon next to "Unreal Engine Root Folder"
   - Navigate to your UE installation (example: C:\Program Files\Epic Games\UE_5.6)
   - The tool checks that the necessary files exist

4. **Start Migration**
   - Click "Begin Migration"
   - Watch the console output for real-time progress
   - Wait for the completion dialog

The console output shows you exactly what's happening, including any errors or warnings from Unreal Engine's build tools.

## Important Limitations

**This tool cannot fix all plugins.** Some plugins are deeply tied to specific engine versions and may not migrate successfully. Here's what you should know:

- **Engine-Dependent Plugins**: Plugins that rely heavily on engine-specific features or APIs may fail to migrate. These plugins often need manual code changes to work with different engine versions.

- **Complex Dependencies**: Plugins with complicated third-party dependencies might not compile correctly after migration.

- **Manual Intervention**: If a plugin fails to migrate, you'll likely need to:
  - Manually update the plugin's code to match the target engine version
  - Fix API changes and deprecated functions
  - Resolve dependency issues
  - Recompile using traditional methods (Visual Studio, etc.)

**Always keep backups of your original plugin files.** This tool uses Unreal Engine's official tools, but migration isn't always straightforward.

## What Happens During Migration

The tool runs Unreal Engine's BuildPlugin command through the Automation Tool (UAT). This is the same process you'd run manually from the command line, but with a much friendlier interface. The tool:

1. Validates your inputs
2. Constructs the proper UAT command
3. Executes the command
4. Streams the output to you in real-time
5. Reports success or failure

## Version Comparison

| Feature             | Version 1.0/2.0   | Version 3.0                        |
| ------------------- | ----------------- | ---------------------------------- |
| Code Lines          | 144               | 437                                |
| Architecture        | Procedural        | Object-Oriented Class              |
| User Interface      | Basic rows        | Modern card layout                 |
| Theme Options       | Dark only         | Dark and light                     |
| Console Output      | None              | Real-time streaming                |
| Input Fields        | Text labels       | Labeled text fields                |
| Validation          | None              | Comprehensive with visual feedback |
| Error Messages      | Generic           | Detailed and specific              |
| Path Verification   | None              | Checks RunUAT.bat exists           |
| Status Messages     | Small/none        | Large and prominent                |
| Progress Indication | None              | Progress bar + status text         |
| Responsiveness      | Fixed size        | Adapts to window size              |
| Processing          | Blocks UI         | Non-blocking async                 |
| Error Handling      | Basic try-catch   | Comprehensive with logging         |
| Path Handling       | String formatting | Pathlib                            |

## Contributing

This is an open project. Feel free to:

- Report bugs or issues
- Suggest improvements
- Submit pull requests
- Fork and modify for your own needs

## License

This project is released into the public domain. You can use it, modify it, distribute it, or do whatever you want with it. No attribution required, though it's always appreciated.

The tool itself is just a UI wrapper around Unreal Engine's official tools. All the actual migration work is done by Epic Games' Unreal Automation Tool (UAT).

## Disclaimer

This tool is provided as-is. While it uses Unreal Engine's official build tools, plugin migration can be complex and isn't always successful.

**Before using this tool:**

- Back up your plugin files
- Understand that some plugins may not migrate successfully
- Be prepared to manually fix code if needed
- Test migrated plugins thoroughly before using them in production

The author is not responsible for any issues, data loss, or problems that may occur during the migration process.

## Support

If you encounter issues or have questions:

- Check the console output for error messages
- Review Unreal Engine's documentation on plugin development
- Open an issue on GitHub with details about your problem

---

Made for the Unreal Engine community with love by me. Happy migrating!
