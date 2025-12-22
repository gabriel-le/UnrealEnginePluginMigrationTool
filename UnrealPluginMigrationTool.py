import flet as ft
import asyncio
import subprocess
from pathlib import Path
import os
import sys

class UnrealPluginMigrationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Unreal Plugin Migration Tool"
        self.page.theme_mode = "dark"
        self.page.window_width = 900
        self.page.window_height = 750
        self.page.window_resizable = True
        self.page.padding = 20
        
        # State variables
        self.uplugin_path = ""
        self.destination_path = ""
        self.ue_root_path = ""
        self.is_migrating = False

        # UI Components
        self.setup_components()
        self.build_ui()

    def setup_components(self):
        # File Pickers
        self.uplugin_picker = ft.FilePicker(on_result=self.on_uplugin_result)
        self.destination_picker = ft.FilePicker(on_result=self.on_destination_result)
        self.ue_root_picker = ft.FilePicker(on_result=self.on_ue_root_result)
        
        self.page.overlay.extend([
            self.uplugin_picker, 
            self.destination_picker, 
            self.ue_root_picker
        ])

        # Text Fields for paths (Read-only)
        self.uplugin_field = ft.TextField(
            label="Source .uplugin File",
            read_only=True,
            hint_text="Select the plugin file to migrate...",
            border_color="blue200",
            text_size=12,
            dense=True,
        )
        
        self.destination_field = ft.TextField(
            label="Destination Folder",
            read_only=True,
            hint_text="Select where the migrated plugin will be saved...",
            border_color="blue200",
            text_size=12,
            dense=True,
        )
        
        self.ue_root_field = ft.TextField(
            label="Unreal Engine Root Folder",
            read_only=True,
            hint_text="e.g., C:\\Program Files\\Epic Games\\UE_5.3",
            border_color="blue200",
            text_size=12,
            dense=True,
        )

        # Console Output - Flexible height
        self.console_output = ft.TextField(
            label="Console Output",
            multiline=True,
            read_only=True,
            value="Ready to migrate plugin...\n",
            border_color="grey700",
            text_size=11,
            expand=True,  # Takes available space
        )

        # Progress and Status
        self.progress_bar = ft.ProgressBar(color="blue", visible=False)
        self.status_text = ft.Text(
            "", 
            italic=True, 
            color="blue400", 
            size=16,
            weight="bold",
            text_align="center",
        )
        
        # Action Button
        self.migrate_button = ft.ElevatedButton(
            "Begin Migration",
            icon="play_arrow_rounded",
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
            content=ft.Column([
                ft.Row([
                    ft.Icon("settings_system_daydream_rounded", size=32, color="blue400"),
                    ft.Text("Unreal Plugin Migration", size=24, weight="bold"),
                ], alignment="center"),
                ft.Text("Automate your plugin packaging with UAT", size=13, color="grey400"),
            ], horizontal_alignment="center", spacing=4, tight=True),
        )

        # Theme Toggle
        self.theme_icon = ft.IconButton(
            icon="light_mode_rounded",
            on_click=self.toggle_theme,
            tooltip="Toggle Theme"
        )

        # Main Content Card - Flexible
        content_card = ft.Container(
            content=ft.Column([
                # Section 1: Plugin Selection
                self.create_section(
                    "1. Select Plugin",
                    ft.Row([
                        self.uplugin_field,
                        ft.IconButton(
                            icon="folder_open_rounded",
                            on_click=lambda _: self.uplugin_picker.pick_files(
                                allowed_extensions=["uplugin"]
                            ),
                            tooltip="Browse for .uplugin file"
                        ),
                    ])
                ),
                
                # Section 2: Destination Selection
                self.create_section(
                    "2. Destination",
                    ft.Row([
                        self.destination_field,
                        ft.IconButton(
                            icon="create_new_folder_rounded",
                            on_click=lambda _: self.destination_picker.get_directory_path(),
                            tooltip="Select destination folder"
                        ),
                    ])
                ),
                
                # Section 3: UE Root Selection
                self.create_section(
                    "3. Unreal Engine Path",
                    ft.Row([
                        self.ue_root_field,
                        ft.IconButton(
                            icon="computer_rounded",
                            on_click=lambda _: self.ue_root_picker.get_directory_path(),
                            tooltip="Select UE root folder"
                        ),
                    ])
                ),
                
                # Console Output Section - Flexible
                ft.Container(
                    content=ft.Column([
                        ft.Text("Console Output", size=15, weight="w600", color="blue200"),
                        self.console_output,
                    ], spacing=6, tight=True),
                    expand=True,  # Takes remaining space
                ),
                
                # Status Message
                ft.Container(
                    content=self.status_text,
                    padding=8,
                ),
                
                # Action Area - Fixed at bottom
                ft.Column([
                    self.migrate_button,
                    ft.Container(height=4),
                    self.progress_bar,
                ], horizontal_alignment="center", tight=True)
                
            ], spacing=10, tight=True, expand=True),
            padding=20,
            expand=True,
        )

        # Main layout - Flexible column
        main_column = ft.Column([
            ft.Row([self.theme_icon], alignment="end"),
            header,
            ft.Container(height=8),
            ft.Card(
                content=content_card,
                elevation=4,
                expand=True,  # Card takes remaining space
            ),
        ], spacing=0, expand=True)

        self.page.add(main_column)

    def create_section(self, title, content):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=15, weight="w600", color="blue200"),
                content
            ], spacing=6, tight=True),
        )

    def log_to_console(self, message):
        """Add message to console output"""
        self.console_output.value += f"{message}\n"
        self.page.update()
        # Also print to actual console
        print(message)

    # Event Handlers
    def on_uplugin_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.uplugin_path = e.files[0].path
            self.uplugin_field.value = self.uplugin_path
            self.uplugin_field.border_color = "green"
            self.log_to_console(f"✓ Plugin selected: {self.uplugin_path}")
            self.page.update()

    def on_destination_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.destination_path = e.path
            self.destination_field.value = self.destination_path
            self.destination_field.border_color = "green"
            self.log_to_console(f"✓ Destination selected: {self.destination_path}")
            self.page.update()

    def on_ue_root_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.ue_root_path = e.path
            self.ue_root_field.value = self.ue_root_path
            self.ue_root_field.border_color = "green"
            self.log_to_console(f"✓ UE Root selected: {self.ue_root_path}")
            self.page.update()

    def toggle_theme(self, e):
        if self.page.theme_mode == "dark":
            self.page.theme_mode = "light"
            self.theme_icon.icon = "dark_mode_rounded"
        else:
            self.page.theme_mode = "dark"
            self.theme_icon.icon = "light_mode_rounded"
        self.page.update()

    async def start_migration_wrapper(self, e):
        """Wrapper to handle async call from sync button click"""
        await self.start_migration(e)

    async def start_migration(self, e):
        # Validation with clear feedback
        missing_fields = []
        if not self.uplugin_path:
            missing_fields.append("Plugin file")
            self.uplugin_field.border_color = "red"
        if not self.destination_path:
            missing_fields.append("Destination folder")
            self.destination_field.border_color = "red"
        if not self.ue_root_path:
            missing_fields.append("UE root folder")
            self.ue_root_field.border_color = "red"
        
        if missing_fields:
            error_msg = f"⚠ Missing required fields: {', '.join(missing_fields)}"
            self.log_to_console(error_msg)
            self.show_snackbar(error_msg, "amber700")
            self.status_text.value = "⚠ Please fill all required fields!"
            self.status_text.color = "amber"
            self.page.update()
            return

        # Reset field colors
        self.uplugin_field.border_color = "blue200"
        self.destination_field.border_color = "blue200"
        self.ue_root_field.border_color = "blue200"

        uat_path = Path(self.ue_root_path) / "Engine" / "Build" / "BatchFiles" / "RunUAT.bat"
        if not uat_path.exists():
            error_msg = f"✗ RunUAT.bat not found at: {uat_path}"
            self.log_to_console(error_msg)
            self.show_snackbar("RunUAT.bat not found!", "red700")
            self.ue_root_field.border_color = "red"
            self.status_text.value = "✗ RunUAT.bat not found!"
            self.status_text.color = "red"
            self.page.update()
            return

        # UI State Update
        self.log_to_console("\n" + "="*50)
        self.log_to_console("Starting migration process...")
        self.log_to_console("="*50)
        
        self.is_migrating = True
        self.migrate_button.disabled = True
        self.progress_bar.visible = True
        self.status_text.value = "⏳ MIGRATION IN PROGRESS - PLEASE WAIT..."
        self.status_text.color = "blue400"
        self.page.update()

        # Run Migration Asynchronously
        success, message = await self.run_uat_command(uat_path)

        # Reset UI State
        self.is_migrating = False
        self.migrate_button.disabled = False
        self.progress_bar.visible = False
        
        if success:
            self.log_to_console("\n" + "="*50)
            self.log_to_console("✓ SUCCESS: Plugin migrated successfully!")
            self.log_to_console("="*50)
            self.status_text.value = "✓ MIGRATION COMPLETED SUCCESSFULLY!"
            self.status_text.color = "green"
            self.page.update()
            
            # Show success dialog
            await asyncio.sleep(0.5)
            self.show_dialog(
                "✓ Migration Successful!", 
                "Your plugin has been migrated successfully!\n\n"
                "The migrated plugin is located in the 'Migrated' subfolder "
                "of your selected destination.\n\n"
                "Check the console output above for detailed information."
            )
        else:
            self.log_to_console("\n" + "="*50)
            self.log_to_console("✗ ERROR: Migration failed!")
            self.log_to_console(f"Error details: {message[:500]}")
            self.log_to_console("="*50)
            self.status_text.value = "✗ MIGRATION FAILED!"
            self.status_text.color = "red"
            self.page.update()
            
            # Show error dialog
            await asyncio.sleep(0.5)
            self.show_dialog(
                "✗ Migration Failed", 
                f"The migration process encountered an error.\n\n"
                f"Error: {message[:300]}...\n\n"
                f"Check the console output above for full details."
            )
        
        self.page.update()

    async def run_uat_command(self, uat_path):
        destination = Path(self.destination_path) / "Migrated"
        destination.mkdir(parents=True, exist_ok=True)
        
        # Quote paths to handle spaces
        command = f'"{uat_path}" BuildPlugin -plugin="{self.uplugin_path}" -package="{destination}"'
        
        self.log_to_console(f"\nExecuting command:")
        self.log_to_console(f"{command}\n")
        
        try:
            # Create process with real-time output
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                shell=True
            )
            
            # Read output line by line in real-time
            output_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                decoded_line = line.decode('utf-8', errors='ignore').strip()
                if decoded_line:
                    output_lines.append(decoded_line)
                    self.log_to_console(decoded_line)
            
            # Wait for process to complete
            await process.wait()
            
            full_output = '\n'.join(output_lines)
            
            if process.returncode == 0:
                return True, full_output
            else:
                return False, full_output or f"Process exited with code {process.returncode}"
                
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
            title=ft.Text(title, size=22, weight="bold"),
            content=ft.Text(content, size=14, selectable=True),
            actions=[
                ft.TextButton(
                    "OK", 
                    on_click=lambda _: self.close_dialog(),
                    style=ft.ButtonStyle(
                        padding=15,
                    )
                )
            ],
            actions_alignment="end",
        )
        self.page.dialog.open = True
        self.page.update()

    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

def main(page: ft.Page):
    UnrealPluginMigrationApp(page)

if __name__ == "__main__":
    ft.app(target=main)
