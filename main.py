# main.py

import sys
from enum import Enum
from typing import Callable, List

from rich.panel import Panel
from rich.align import Align
from rich.align import AlignMethod

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.events import Click
from textual.views import GridView

from datetime import datetime

START = "START"
STOP = "STOP"

class Directions(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'

class MyButton(Widget):
    """Generic Button class."""

    in_focus = Reactive(False)

    def __init__(self,
                 name: str | None = None,
                 text: str | None = None,
                 callback: Callable | None = None,
                 args: List | None = None) -> None:
        super().__init__(name)
        self._text = text if text is not None else ""
        self._callback = callback
        self._args = args

    def render(self) -> Panel:
        pnl = Panel(
            self._text,
            style=("on red" if self.in_focus else ""))
        return Align(pnl, align="center")

    def on_enter(self) -> None:
        self.in_focus = True

    def on_leave(self) -> None:
        self.in_focus = False

    async def interact(self):
        if self._callback is not None:
            if self._args is None:
                self._callback()
            else:
                self._callback(*self._args)

class Status(Widget):

    value = Reactive("-")

    def render(self) -> Panel:
        return Panel(self.value)

class Clock(Widget):

    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self):
        time_str = datetime.now().strftime("%H:%M:%S")
        obj = Align(time_str, align="center", vertical="middle")

        return Panel(
            obj,
            title="Clock", title_align="left")

class Timer(Widget):

    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self):
        time_str = datetime.now().strftime("%H:%M:%S")
        obj = Align(time_str, align="center", vertical="top", height=3)
        return Panel(obj, title="Timer", title_align="left")

class ClockApp(App):
    """Demonstrates custom widgets"""
    status = Reactive("--")

    def watch_status(self, value):
        self._status.value = value

    async def on_mount(self) -> None:
        self._focus_index_x = 0
        self._focus_index_y = 0
        self._buttons: List[List[MyButton]]
        self._buttons = [ [None], [None] ]
        self._buttons[0][0] = MyButton(
            text=START,
            callback=self.watch_status,
            args=["top_button"])
        self._buttons[1][0] = MyButton(text=STOP)
        self._status = Status()
        self._clock = Clock()
        self._timer = Timer()

        self.grid = await self.view.dock_grid(edge='left', name="left")
        self.grid.set_gap(2, 1)
        self.grid.set_gutter(1)
        self.grid.set_align("left", "bottom")
        self.grid.add_column(name='col0', size=10)
        self.grid.add_column(name='col1', size=10)
        self.grid.add_row("row0", size=4)
        self.grid.add_row("row1", size=4)
        self.grid.add_row("row2", size=5)
        self.grid.add_row("row3", size=5)
        self.grid.add_areas(
            clock_area="col0-start|col1-end,row0",
            timer_area="col0-start|col1-end,row1",
            start_btn_area="col0,row2",
            stop_btn_area="col1,row2",
            status_area="col0-start|col1-end,row3")
        self.grid.place(
            clock_area=self._clock,
            timer_area=self._timer,
            start_btn_area=self._buttons[0][0],
            stop_btn_area=self._buttons[1][0],
            status_area=self._status)


    async def change_button_focus(self, direction: Directions):
        previous_index_x = self._focus_index_x
        previous_index_y = self._focus_index_y
        new_focus_index_x = self._focus_index_x
        new_focus_index_y = self._focus_index_y
        if direction == Directions.UP:
            if self._focus_index_y <= 0:
                new_focus_index_y = 0
            else:
                new_focus_index_y = self._focus_index_y - 1

        elif direction == Directions.DOWN:
            if self._focus_index_y >= len(self._buttons[self._focus_index_x]) - 1:
                new_focus_index_y = len(self._buttons[self._focus_index_x]) - 1
            else:
                new_focus_index_y = self._focus_index_y + 1

        elif direction == Directions.LEFT:
            if self._focus_index_x <= 0:
                new_focus_index_x = 0
            else:
                new_focus_index_x = self._focus_index_x - 1

        elif direction == Directions.RIGHT:
            if self._focus_index_x <= len(self._buttons) - 1:
                new_focus_index_x = len(self._buttons) - 1
            else:
                new_focus_index_x = self._focus_index_x + 1

        else:
            self.status = f"ERROR: Undefined {direction=}"
            new_focus_index_x = 0
            new_focus_index_y = 0

        self._buttons[previous_index_x][previous_index_y].in_focus = False
        self._buttons[new_focus_index_x][new_focus_index_y].in_focus = True
        self._focus_index_x = new_focus_index_x
        self._focus_index_y = new_focus_index_y

    async def action_up(self):
        self.status = "up-arrow"
        await self.change_button_focus(Directions.UP)

    async def action_down(self):
        self.status = "down-arrow"
        await self.change_button_focus(Directions.DOWN)

    async def action_left(self):
        self.status = "left-arrow"
        await self.change_button_focus(Directions.LEFT)

    async def action_right(self):
        self.status = "right-arrow"
        await self.change_button_focus(Directions.RIGHT)

    async def action_enter(self):
        self.status = "enter button"
        button = self._buttons[self._focus_index_x][self._focus_index_y]
        if button.in_focus:
            button.interact()


    async def on_load(self, event):
        await self.bind("q", "quit")
        await self.bind(Directions.UP.value, Directions.UP.value)
        await self.bind(Directions.DOWN.value, Directions.DOWN.value)
        await self.bind(Directions.LEFT.value, Directions.LEFT.value)
        await self.bind(Directions.RIGHT.value, Directions.RIGHT.value)
        await self.bind("enter", "enter")

if __name__ == "__main__":
    with open("error.log", "w") as fh:
        sys.stderr = fh
        app = ClockApp()
        app.run(log="textual.log")
