"""Contains the select addons view."""

# This file is part of OpenAndroidInstaller.
# OpenAndroidInstaller is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# OpenAndroidInstaller is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with OpenAndroidInstaller.
# If not, see <https://www.gnu.org/licenses/>."""
# Author: Tobias Sterbak

import webbrowser
from loguru import logger
from typing import Callable

from flet import (
    Column,
    Divider,
    ElevatedButton,
    OutlinedButton,
    FilledButton,
    Markdown,
    Row,
    Text,
    colors,
    icons,
    TextButton,
    AlertDialog,
    FilePicker,
    FilePickerResultEvent,
)
from flet.buttons import CountinuosRectangleBorder

from views import BaseView
from app_state import AppState
from widgets import get_title, confirm_button


class AddonsView(BaseView):
    def __init__(
        self,
        state: AppState,
        on_confirm: Callable,
    ):
        super().__init__(state=state)
        self.on_confirm = on_confirm

    def build(self):
        # dialog box to explain OS images and recovery
        self.dlg_explain_addons = AlertDialog(
            modal=True,
            title=Text("What is an OS image and recovery and why do I need it?"),
            content=Markdown(
                """## OS image or ROM
An operating system (OS) is system software that manages computer hardware,
software resources, and provides common services for computer programs. 
Popular, custom operating systems for mobile devices based on Android are 
- [LineageOS](https://lineageos.org/)
- [/e/OS](https://e.foundation/e-os/) or
- [LineageOS for microG](https://lineage.microg.org/)
- and many others.

Often, the related OS images are called 'ROM'. 'ROM' stands for *R*ead-*o*nly *m*emory,
which is a type of non-volatile memory used in computers for storing software that is
rarely changed during the life of the system, also known as firmware.

## Recovery Image
A custom recovery is used for installing custom software on your device.
This custom software can include smaller modifications like rooting your device or even
replacing the firmware of the device with a completely custom ROM.

OpenAndroidInstaller works with the [TWRP recovery project](https://twrp.me/about/).""",
                on_tap_link=lambda e: self.page.launch_url(e.data),
            ),
            actions=[
                TextButton("Close", on_click=self.close_close_explain_addons_dlg),
            ],
            actions_alignment="end",
            shape=CountinuosRectangleBorder(radius=0),
        )

        # initialize file pickers
        self.pick_addons_dialog = FilePicker(on_result=self.pick_addons_result)
        self.selected_addons = Text("Selected addons: ")

        # initialize and manage button state.
        self.confirm_button = confirm_button(self.on_confirm)
        # self.confirm_button.disabled = True
        # self.pick_addons_dialog.on_result = self.enable_button_if_ready

        # attach hidden dialogues
        self.right_view.controls.append(self.pick_addons_dialog)

        # create help/info button to show the help dialog
        info_button = OutlinedButton(
            "What is this?",
            on_click=self.open_explain_addons_dlg,
            expand=True,
            icon=icons.HELP_OUTLINE_OUTLINED,
            icon_color=colors.DEEP_ORANGE_500,
            tooltip="Get more details on custom operating system images and recoveries.",
        )

        # add title
        self.right_view_header.controls.append(
            get_title(
                "You can select additional addons to install. Otherwise you can safely continue",
                info_button=info_button,
                step_indicator_img="steps-header-select.png",
            )
        )

        # text row to show infos during the process
        self.info_field = Row()
        # if there is an available download, show the button to the page
        self.right_view.controls.append(Divider())
        self.right_view.controls.append(
            Column(
                [
                    Text("Here you can download the right GApps for your device."),
                    Row(
                        [
                            ElevatedButton(
                                "Download LineageOS image",
                                icon=icons.DOWNLOAD_OUTLINED,
                                on_click=lambda _: webbrowser.open(
                                    "https://wiki.lineageos.org/gapps"
                                ),
                                expand=True,
                            ),
                        ]
                    ),
                    Divider(),
                ]
            )
        )
        # attach the controls for uploading addons
        self.right_view.controls.extend(
            [
                Text("Select addons:", style="titleSmall"),
                Markdown(
                    f"""
The image file should look something like `lineage-19.1-20221101-nightly-{self.state.config.metadata.get('devicecode')}-signed.zip`."""
                ),
                Row(
                    [
                        FilledButton(
                            "Pick the addons you want to install",
                            icon=icons.UPLOAD_FILE,
                            on_click=lambda _: self.pick_addons_dialog.pick_files(
                                allow_multiple=True,
                                file_type="custom",
                                allowed_extensions=["zip"],
                            ),
                            expand=True,
                        ),
                    ]
                ),
                self.selected_addons,
                Divider(),
                self.info_field,
                Row([self.confirm_button]),
            ]
        )
        return self.view

    def open_explain_addons_dlg(self, e):
        """Open the dialog to explain addons."""
        self.page.dialog = self.dlg_explain_addons
        self.dlg_explain_addons.open = True
        self.page.update()

    def close_close_explain_addons_dlg(self, e):
        """Close the dialog to explain addons."""
        self.dlg_explain_addons.open = False
        self.page.update()

    def pick_addons_result(self, e: FilePickerResultEvent):
        path = ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
        # update the textfield with the name of the file
        self.selected_addons.value = (
            self.selected_addons.value.split(":")[0] + f": {path}"
        )
        if e.files:
            self.addon_paths = [file.path for file in e.files]
            self.state.addon_paths = self.addon_paths
            logger.info(f"Selected addons: {self.addon_paths}")
        else:
            logger.info("No addons selected.")
        # check if the addons works with the device and show the filename in different colors accordingly
        # update
        self.selected_addons.update()
