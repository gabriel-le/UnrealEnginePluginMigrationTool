from __future__ import annotations

import flet as ft
import asyncio
import subprocess
from pathlib import Path
import os
import sys
import platform

# Detect platform
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
UAT_SCRIPT_NAME = "RunUAT.bat" if IS_WINDOWS else "RunUAT.sh"


class UnrealPluginMigrationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Unreal Plugin Migration Tool"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20

        # Window sizing (Flet 0.80+ uses page.window)
        if hasattr(self.page, "window") and self.page.window is not None:
            self.page.window.width = 900
            self.page.window.height = 750
            self.page.window.resizable = True
        else:
            # Fallback for older Flet
            self.page.window_width = 900
            self.page.window_height = 750
            self.page.window_resizable = True

        # State variables
        self.uplugin_path = ""
        self.destination_path = ""
        self.ue_root_path = ""
        self.is_migrating = False

        # UI Components
        self.setup_components()
        self.build_ui()

    def setup_components(self):
        # File Pickers - Flet 0.80+ style (on_result is a property, not constructor arg)
        # FilePickers are invisible controls - don't add them to the page
        self.uplugin_picker = ft.FilePicker()
        self.uplugin_picker.on_result = self.on_uplugin_result

        self.destination_picker = ft.FilePicker()
        self.destination_picker.on_result = self.on_destination_result

        self.ue_root_picker = ft.FilePicker()
        self.ue_root_picker.on_result = self.on_ue_root_result

        # Text Fields for paths (Read-only)
        self.uplugin_field = ft.TextField(
            label="Source .uplugin File",
            read_only=True,
            hint_text="Select the plugin file to migrate...",
            border_color=ft.Colors.BLUE_200,
            text_size=12,
            dense=True,
            expand=True,
        )

        self.destination_field = ft.TextField(
            label="Destination Folder",
            read_only=True,
            hint_text="Select where the migrated plugin will be saved...",
            border_color=ft.Colors.BLUE_200,
            text_size=12,
            dense=True,
            expand=True,
        )

        # OS-specific hint text for UE root path
        if IS_WINDOWS:
            ue_hint = "e.g., C:\\Program Files\\Epic Games\\UE_5.3"
        elif IS_MACOS:
            ue_hint = "e.g., /Users/Shared/Epic Games/UE_5.3 or /Applications/UE_5.3"
        else:
            ue_hint = "e.g., /opt/UnrealEngine/UE_5.3"

        self.ue_root_field = ft.TextField(
            label="Unreal Engine Root Folder",
            read_only=True,
            hint_text=ue_hint,
            border_color=ft.Colors.BLUE_200,
            text_size=12,
            dense=True,
            expand=True,
        )

        # Console Output - Flexible height
        self.console_output = ft.TextField(
            label="Console Output",
            multiline=True,
            read_only=True,
            value="Ready to migrate plugin...\n",
            border_color=ft.Colors.GREY_700,
            text_size=11,
            expand=True,
        )

        # Progress and Status
        self.progress_bar = ft.ProgressBar(color=ft.Colors.BLUE, visible=False)
        self.status_text = ft.Text(
            "",
            italic=True,
            color=ft.Colors.BLUE_400,
            size=16,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # Action Button (Flet 0.80+ uses FilledButton instead of ElevatedButton)
        self.migrate_button = ft.FilledButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED),
                    ft.Text("Begin Migration"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            on_click=self.start_migration_wrapper,
            style=ft.ButtonStyle(
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            height=50,
        )

    def build_ui(self):
        # Header - Compact
        header = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.SETTINGS_SYSTEM_DAYDREAM_ROUNDED,
                                size=32,
                                color=ft.Colors.BLUE_400,
                            ),
                            ft.Text(
                                "Unreal Plugin Migration",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        "Automate your plugin packaging with UAT",
                        size=13,
                        color=ft.Colors.GREY_400,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                tight=True,
            ),
        )

        # Theme Toggle
        self.theme_icon = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE_ROUNDED,
            on_click=self.toggle_theme,
            tooltip="Toggle Theme",
        )

        # Main Content Card - Flexible
        content_card = ft.Container(
            content=ft.Column(
                [
                    # Section 1: Plugin Selection
                    self.create_section(
                        "1. Select Plugin",
                        ft.Row(
                            [
                                self.uplugin_field,
                                ft.IconButton(
                                    icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                                    on_click=self.pick_uplugin_file,
                                    tooltip="Browse for .uplugin file",
                                ),
                            ]
                        ),
                    ),
                    # Section 2: Destination Selection
                    self.create_section(
                        "2. Destination",
                        ft.Row(
                            [
                                self.destination_field,
                                ft.IconButton(
                                    icon=ft.Icons.CREATE_NEW_FOLDER_ROUNDED,
                                    on_click=self.pick_destination_folder,
                                    tooltip="Select destination folder",
                                ),
                            ]
                        ),
                    ),
                    # Section 3: UE Root Selection
                    self.create_section(
                        "3. Unreal Engine Path",
                        ft.Row(
                            [
                                self.ue_root_field,
                                ft.IconButton(
                                    icon=ft.Icons.COMPUTER_ROUNDED,
                                    on_click=self.pick_ue_root_folder,
                                    tooltip="Select UE root folder",
                                ),
                            ]
                        ),
                    ),
                    # Console Output Section - Flexible
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Console Output",
                                    size=15,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.BLUE_200,
                                ),
                                self.console_output,
                            ],
                            spacing=6,
                            tight=True,
                        ),
                        expand=True,
                    ),
                    # Status Message
                    ft.Container(
                        content=self.status_text,
                        padding=8,
                    ),
                    # Action Area - Fixed at bottom
                    ft.Column(
                        [
                            self.migrate_button,
                            ft.Container(height=4),
                            self.progress_bar,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        tight=True,
                    ),
                ],
                spacing=10,
                tight=True,
                expand=True,
            ),
            padding=20,
            expand=True,
        )

        # Main layout - Flexible column
        main_column = ft.Column(
            [
                ft.Row([self.theme_icon], alignment=ft.MainAxisAlignment.END),
                header,
                ft.Container(height=8),
                ft.Card(
                    content=content_card,
                    elevation=4,
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

        self.page.add(main_column)

    def create_section(self, title, content):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        title,
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.BLUE_200,
                    ),
                    content,
                ],
                spacing=6,
                tight=True,
            ),
        )

    def log_to_console(self, message):
        """Add message to console output"""
        self.console_output.value += f"{message}\n"
        self.page.update()
        # Also print to actual console
        print(message)

    # Async file picker handlers (Flet 0.80+ returns result directly)
    async def pick_uplugin_file(self, e):
        result = await self.uplugin_picker.pick_files(allowed_extensions=["uplugin"])
        # result is a list of files directly in Flet 0.80+
        if result and len(result) > 0:
            self.uplugin_path = result[0].path
            self.uplugin_field.value = self.uplugin_path
            self.uplugin_field.border_color = ft.Colors.GREEN
            self.log_to_console(f"✓ Plugin selected: {self.uplugin_path}")
            self.page.update()

    async def pick_destination_folder(self, e):
        result = await self.destination_picker.get_directory_path()
        # result is the path string directly in Flet 0.80+
        if result:
            self.destination_path = result
            self.destination_field.value = self.destination_path
            self.destination_field.border_color = ft.Colors.GREEN
            self.log_to_console(f"✓ Destination selected: {self.destination_path}")
            self.page.update()

    async def pick_ue_root_folder(self, e):
        result = await self.ue_root_picker.get_directory_path()
        # result is the path string directly in Flet 0.80+
        if result:
            self.ue_root_path = result
            self.ue_root_field.value = self.ue_root_path
            self.ue_root_field.border_color = ft.Colors.GREEN
            self.log_to_console(f"✓ UE Root selected: {self.ue_root_path}")
            self.page.update()

    # Legacy event handlers (kept for compatibility, but may not be called in 0.80+)
    def on_uplugin_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.uplugin_path = e.files[0].path
            self.uplugin_field.value = self.uplugin_path
            self.uplugin_field.border_color = ft.Colors.GREEN
            self.log_to_console(f"✓ Plugin selected: {self.uplugin_path}")
            self.page.update()

    def on_destination_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.destination_path = e.path
            self.destination_field.value = self.destination_path
            self.destination_field.border_color = ft.Colors.GREEN
            self.log_to_console(f"✓ Destination selected: {self.destination_path}")
            self.page.update()

    def on_ue_root_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.ue_root_path = e.path
            self.ue_root_field.value = self.ue_root_path
            self.ue_root_field.border_color = ft.Colors.GREEN
            self.log_to_console(f"✓ UE Root selected: {self.ue_root_path}")
            self.page.update()

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_icon.icon = ft.Icons.DARK_MODE_ROUNDED
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_icon.icon = ft.Icons.LIGHT_MODE_ROUNDED
        self.page.update()

    async def start_migration_wrapper(self, e):
        """Wrapper to handle async call from sync button click"""
        await self.start_migration(e)

    async def start_migration(self, e):
        # Validation with clear feedback
        missing_fields = []
        if not self.uplugin_path:
            missing_fields.append("Plugin file")
            self.uplugin_field.border_color = ft.Colors.RED
        if not self.destination_path:
            missing_fields.append("Destination folder")
            self.destination_field.border_color = ft.Colors.RED
        if not self.ue_root_path:
            missing_fields.append("UE root folder")
            self.ue_root_field.border_color = ft.Colors.RED

        if missing_fields:
            error_msg = f"⚠ Missing required fields: {', '.join(missing_fields)}"
            self.log_to_console(error_msg)
            self.show_snackbar(error_msg, ft.Colors.AMBER_700)
            self.status_text.value = "⚠ Please fill all required fields!"
            self.status_text.color = ft.Colors.AMBER
            self.page.update()
            return

        # Reset field colors
        self.uplugin_field.border_color = ft.Colors.BLUE_200
        self.destination_field.border_color = ft.Colors.BLUE_200
        self.ue_root_field.border_color = ft.Colors.BLUE_200

        uat_path = (
            Path(self.ue_root_path)
            / "Engine"
            / "Build"
            / "BatchFiles"
            / UAT_SCRIPT_NAME
        )
        if not uat_path.exists():
            error_msg = f"✗ {UAT_SCRIPT_NAME} not found at: {uat_path}"
            self.log_to_console(error_msg)
            self.show_snackbar(f"{UAT_SCRIPT_NAME} not found!", ft.Colors.RED_700)
            self.ue_root_field.border_color = ft.Colors.RED
            self.status_text.value = f"✗ {UAT_SCRIPT_NAME} not found!"
            self.status_text.color = ft.Colors.RED
            self.page.update()
            return

        # UI State Update
        self.log_to_console("\n" + "=" * 50)
        self.log_to_console("Starting migration process...")
        self.log_to_console("=" * 50)

        self.is_migrating = True
        self.migrate_button.disabled = True
        self.progress_bar.visible = True
        self.status_text.value = "⏳ MIGRATION IN PROGRESS - PLEASE WAIT..."
        self.status_text.color = ft.Colors.BLUE_400
        self.page.update()

        # Run Migration Asynchronously
        success, message = await self.run_uat_command(uat_path)

        # Reset UI State
        self.is_migrating = False
        self.migrate_button.disabled = False
        self.progress_bar.visible = False

        if success:
            self.log_to_console("\n" + "=" * 50)
            self.log_to_console("✓ SUCCESS: Plugin migrated successfully!")
            self.log_to_console("=" * 50)
            self.status_text.value = "✓ MIGRATION COMPLETED SUCCESSFULLY!"
            self.status_text.color = ft.Colors.GREEN
            self.page.update()

            # Show success dialog
            await asyncio.sleep(0.5)
            self.show_dialog(
                "✓ Migration Successful!",
                "Your plugin has been migrated successfully!\n\n"
                "The migrated plugin is located in the 'Migrated' subfolder "
                "of your selected destination.\n\n"
                "Check the console output above for detailed information.",
            )
        else:
            self.log_to_console("\n" + "=" * 50)
            self.log_to_console("✗ ERROR: Migration failed!")
            self.log_to_console(f"Error details: {message[:500]}")
            self.log_to_console("=" * 50)
            self.status_text.value = "✗ MIGRATION FAILED!"
            self.status_text.color = ft.Colors.RED
            self.page.update()

            # Show error dialog
            await asyncio.sleep(0.5)
            self.show_dialog(
                "✗ Migration Failed",
                f"The migration process encountered an error.\n\n"
                f"Error: {message[:300]}...\n\n"
                f"Check the console output above for full details.",
            )

        self.page.update()

    async def run_uat_command(self, uat_path):
        destination = Path(self.destination_path) / "Migrated"
        destination.mkdir(parents=True, exist_ok=True)

        # Build command as a list to avoid shell quoting issues on macOS/Linux
        uat_path_str = str(uat_path)
        plugin_arg = f"-plugin={self.uplugin_path}"
        package_arg = f"-package={destination}"

        # Log the command for user visibility
        self.log_to_console(f"\nExecuting command:")
        self.log_to_console(
            f'"{uat_path_str}" BuildPlugin {plugin_arg} {package_arg}\n'
        )

        try:
            # Use create_subprocess_exec with argument list for proper escaping
            # This avoids shell interpretation issues with spaces in paths
            process = await asyncio.create_subprocess_exec(
                uat_path_str,
                "BuildPlugin",
                plugin_arg,
                package_arg,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )

            # Read output line by line in real-time
            output_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                decoded_line = line.decode("utf-8", errors="ignore").strip()
                if decoded_line:
                    output_lines.append(decoded_line)
                    self.log_to_console(decoded_line)

            # Wait for process to complete
            await process.wait()

            full_output = "\n".join(output_lines)

            if process.returncode == 0:
                return True, full_output
            else:
                return (
                    False,
                    full_output or f"Process exited with code {process.returncode}",
                )

        except Exception as ex:
            error_msg = f"Exception occurred: {str(ex)}"
            self.log_to_console(error_msg)
            return False, error_msg

    def show_snackbar(self, message, color):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=14),
            bgcolor=color,
            duration=4000,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_dialog(self, title, content):
        """Show a modal dialog with the result"""
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=22, weight=ft.FontWeight.BOLD),
            content=ft.Text(content, size=14, selectable=True),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=self.close_dialog,
                    style=ft.ButtonStyle(
                        padding=15,
                    ),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def close_dialog(self, e=None):
        self.page.dialog.open = False
        self.page.update()


def main(page: ft.Page):
    UnrealPluginMigrationApp(page)


if __name__ == "__main__":
    # `app()` is deprecated in newer Flet (0.80+). Prefer `run()` when present.
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
