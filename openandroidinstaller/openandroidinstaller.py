"""Main file of the OpenAndroidInstaller."""

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

import os
import sys
import webbrowser
import click
import functools
from pathlib import Path

import flet as ft
from flet import (
    AppBar,
    Banner,
    Column,
    Container,
    ElevatedButton,
    Icon,
    Image,
    Page,
    Text,
    TextButton,
    UserControl,
    colors,
    icons,
)
from loguru import logger

from app_state import AppState
from views import (
    AddonsView,
    SelectFilesView,
    StepView,
    SuccessView,
    StartView,
    RequirementsView,
    WelcomeView,
)
from tooling import run_command

# where to write the logs
logger.add("openandroidinstaller.log")


# detect platform
PLATFORM = sys.platform
# Define asset paths
CONFIG_PATH = (
    Path(__file__).parent.joinpath(Path(os.sep.join(["assets", "configs"]))).resolve()
)
BIN_PATH = Path(__file__).parent.joinpath(Path("bin")).resolve()


class MainView(UserControl):
    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        # create the main columns
        self.view = Column(expand=True, width=1200)

        # create default starter views
        welcome_view = WelcomeView(
            on_confirm=self.confirm,
            state=self.state,
        )
        start_view = StartView(
            on_confirm=self.confirm,
            state=self.state,
        )
        requirements_view = RequirementsView(
            on_confirm=self.confirm,
            state=self.state,
        )
        select_files_view = SelectFilesView(
            on_confirm=self.confirm,
            state=self.state,
        )
        addons_view = AddonsView(
            on_confirm=self.confirm,
            state=self.state,
        )
        # ordered to allow for pop
        self.default_views = [
            addons_view,
            select_files_view,
            requirements_view,
            start_view,
            welcome_view,
        ]
        # create the final success view
        self.final_view = SuccessView(state=self.state)

        self.state.default_views = self.default_views
        self.state.final_view = self.final_view

    def build(self):
        self.view.controls.append(self.default_views.pop())
        return self.view

    def confirm(self, e):
        """Confirmation event handler to use in views."""
        # remove all elements from column view
        self.view.controls = []
        # if there are default views left, display them first
        if self.default_views:
            self.view.controls.append(self.default_views.pop())
        elif self.state.steps:
            self.view.controls.append(
                StepView(
                    step=self.state.steps.pop(0),
                    state=self.state,
                    on_confirm=self.confirm,
                )
            )
        else:
            # display the final view
            self.view.controls.append(self.final_view)
        logger.info("Confirmed.")
        self.view.update()


def configure(page: Page):
    """Configure the application."""
    # Configure the application base page
    page.title = "OpenAndroidInstaller"
    page.theme_mode = "light"
    page.window_height = 900
    page.window_width = int(1.5 * page.window_height)
    page.window_top = 100
    page.window_left = 120
    page.scroll = "adaptive"
    page.horizontal_alignment = "center"


def log_version_infos(bin_path):
    """Log the version infos of adb, fastboot and heimdall."""
    # adb
    adbversion = [line for line in run_command("adb", ["version"], bin_path)]
    adbversion = "\n".join(adbversion[:1])
    logger.info(f"{adbversion}")
    # fastboot
    fbversion = [line for line in run_command("fastboot", ["--version"], bin_path)]
    logger.info(f"{fbversion[0]}")
    # heimdall
    hdversion = [line for line in run_command("heimdall", ["info"], bin_path)]
    logger.info(f"Heimdall version: {hdversion[0]}")


def main(page: Page, test: bool = False, test_config: str = "sargo"):
    logger.info(f"Running OpenAndroidInstaller on {PLATFORM}")
    log_version_infos(bin_path=BIN_PATH)
    logger.info(100 * "-")

    # configure the page
    configure(page)

    # header
    page.appbar = AppBar(
        leading=Image(
            src="/assets/logo-192x192.png", height=40, width=40, border_radius=40
        ),
        leading_width=56,
        toolbar_height=72,
        elevation=0,
        title=Text("OpenAndroidInstaller alpha version", style="displaySmall"),
        center_title=False,
        bgcolor="#00d886",
        actions=[
            Container(
                content=ElevatedButton(
                    icon=icons.BUG_REPORT_OUTLINED,
                    text="Report a bug",
                    on_click=lambda _: webbrowser.open(
                        "https://github.com/openandroidinstaller-dev/openandroidinstaller/issues"
                    ),
                ),
                padding=15,
                tooltip="Report an issue on github",
            )
        ],
    )

    # display a warnings banner
    def close_banner(e):
        page.banner.open = False
        page.update()

    page.banner = Banner(
        bgcolor=colors.AMBER_100,
        leading=Icon(icons.WARNING_AMBER_ROUNDED, color=colors.AMBER, size=40),
        content=Text(
            "These instructions only work if you follow every section and step precisely. Do not continue after something fails!"
        ),
        actions=[
            TextButton("I understand", on_click=close_banner),
        ],
    )
    page.banner.open = True
    page.update()

    # create the State object
    state = AppState(
        platform=PLATFORM,
        config_path=CONFIG_PATH,
        bin_path=BIN_PATH,
        test=test,
        test_config=test_config,
    )
    # create application instance
    app = MainView(state=state)

    # add application's root control to the page
    page.add(app)


@click.command()
@click.option(
    "--test", is_flag=True, default=False, help="Start the application in testing mode."
)
@click.option(
    "--test_config", default="sargo", type=str, help="Config to use for testing"
)
def startup(test: bool, test_config: str):
    "Main entrypoint to the app."
    ft.app(
        target=functools.partial(main, test=test, test_config=test_config),
        assets_dir="assets",
    )


if __name__ == "__main__":
    startup()
