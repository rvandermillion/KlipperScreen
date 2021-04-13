import gi
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from panels.menu import MenuPanel

def create_panel(*args):
    return MainPanel(*args)

class MainPanel(MenuPanel):
    def __init__(self, screen, title, back=False):
        super().__init__(screen, title, False)

    def initialize(self, panel_name, items, extrudercount):
        print("### Making MainMenu")

        grid = self._gtk.HomogeneousGrid()
        grid.set_hexpand(True)
        grid.set_vexpand(True)

        # Create Extruders and bed icons
        eq_grid = Gtk.Grid()
        eq_grid.set_hexpand(True)
        eq_grid.set_vexpand(True)

        self.temperatures = []

        i = 0
        for x in self._printer.get_tools():
            self.labels[x] = self._gtk.ButtonImage("extruder-"+str(i), self._gtk.formatTemperatureString(0, 0))
            self.temperatures.append(x)
            i += 1

        add_temperatures = self._printer.get_heaters() + self._printer.get_temperature_sensors()
        for t in add_temperatures:
            if t == "heater_bed":
                self.labels[t] = self._gtk.ButtonImage("bed", self._gtk.formatTemperatureString(0, 0))
            else:
                name = " ".join(t.split(" ")[1:])
                self.labels[t] = self._gtk.ButtonImage("heat-up", name)
            self.sensors.append(t)

        i = 0
        cols = 3 if len(self.temperatures) > 4 else (1 if len(self.temperatures) <= 2 else 2)
        for t in self.temperatures:
            eq_grid.attach(self.labels[t], i%cols, int(i/cols), 1, 1)
            i += 1

        self.items = items
        self.create_menu_items()

        self.grid = Gtk.Grid()
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(True)

        grid.attach(eq_grid, 0, 0, 1, 1)
        grid.attach(self.arrangeMenuItems(items, 2, True), 1, 0, 1, 1)

        self.grid = grid

        self.target_temps = {
            "heater_bed": 0,
            "extruder": 0
        }

        self.content.add(self.grid)
        self.layout.show_all()

        self._screen.add_subscription(panel_name)

    def activate(self):
        return

    def process_update(self, action, data):
        if action != "notify_status_update":
            return

        for x in self._printer.get_tools():
            self.update_temp(x,
                self._printer.get_dev_stat(x,"temperature"),
                self._printer.get_dev_stat(x,"target")
            )
        for h in self._printer.get_heaters():
            self.update_temp(h,
                self._printer.get_dev_stat(h,"temperature"),
                self._printer.get_dev_stat(h,"target"),
                None if h == "heater_bed" else " ".join(h.split(" ")[1:])
            )
        for t in self._printer.get_temperature_sensors():
            self.update_temp(t,
                self._printer.get_dev_stat(t,"temperature"),
                0,
                " ".join(t.split(" ")[1:])
            )
        return
