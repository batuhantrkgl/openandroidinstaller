"""Contains functions and classes to get different elements and widgets of the installer."""

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
from functools import partial
from typing import Callable

from flet import (
    Container,
    ElevatedButton,
    Row,
    Text,
    alignment,
    icons,
    IconButton,
    Image,
    Column,
)


def get_title(
    title: str, info_button: IconButton = None, step_indicator_img: str = None
) -> Container:
    if info_button:
        content = Row([Text(f"{title}", style="titleLarge"), info_button])
    else:
        content = Row([Text(f"{title}", style="titleLarge")])
    if step_indicator_img:
        content = Column(
            controls=[
                Image(
                    src=f"/assets/imgs/{step_indicator_img}",
                    fit="fitWidth",
                    tooltip=f"Current step: {title}",
                    width=600,
                ),
                content,
            ]
        )
    return Container(
        content=content,
        margin=0,
        padding=0,
        alignment=alignment.center,
        width=600,
        height=150,
        border_radius=1,
    )


def confirm_button(
    confirm_func: Callable, confirm_text: str = "Continue"
) -> ElevatedButton:
    """Get a button, that calls a given function when clicked."""
    return ElevatedButton(
        f"{confirm_text}",
        on_click=confirm_func,
        icon=icons.NEXT_PLAN_OUTLINED,
        expand=True,
    )


def call_button(
    call_func: Callable, command: str, confirm_text: str = "Confirm and run"
) -> ElevatedButton:
    """Get a button, that calls a given function with given command when clicked."""
    return ElevatedButton(
        f"{confirm_text}",
        on_click=partial(call_func, command=command),
        expand=True,
        icon=icons.DIRECTIONS_RUN_OUTLINED,
    )


def link_button(link: str, text: str) -> ElevatedButton:
    """Get a button that opens a link in a browser."""
    return ElevatedButton(
        f"{text}",
        on_click=lambda _: webbrowser.open(link),
        expand=True,
    )
