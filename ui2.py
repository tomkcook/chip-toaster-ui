import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from pathlib import Path
import oven, time

class Ui():
    def __init__(self, profile):
        self.profile = profile
        self.builder = Gtk.Builder()
        prog_path = Path(__file__).parent
        self.builder.add_from_file(str(prog_path / 'ui.glade'))
        self.builder.connect_signals(self)
        for obj in self.builder.get_objects():
            try:
                setattr(self, Gtk.Buildable.get_name(obj), obj)
            except:
                pass
        self.f = Figure()
        self.canvas = FigureCanvas(self.f)
        self.figure_holder.pack_start(self.canvas, True, True, 5)
        self.profile_data_x = [0]
        self.profile_data_y = [25]
        for (rate, target, time) in self.profile:
            t = (target - self.profile_data_y[-1]) / rate
            self.profile_data_x.append(self.profile_data_x[-1] + t)
            self.profile_data_y.append(target)
            self.profile_data_x.append(self.profile_data_x[-1] + time)
            self.profile_data_y.append(target)
        self.recorded_data_x = [0]
        self.recorded_data_y = [25]
        self.replot()
        self.stop_button.set_sensitive(False)
        self.start_button.set_sensitive(False)
        print(self.connect_button.get_label())
        self.main_window.show_all()
        self.oven = None
        self.running = False
        self.start_t = None
        GLib.idle_add(lambda: self.idle())

    def quit(self, *args):
        if self.oven:
            self.oven.stop()
        exit()

    def idle(self):
        if self.oven:
            t = self.oven.process()
            if isinstance(t, float):
                if self.running:
                    self.recorded_data_x.append(time.time() - self.start_t)
                    self.recorded_data_y.append(t)
                else:
                    self.recorded_data_x = [0]
                    self.recorded_data_y = [t]
                self.replot()
        return True

    def replot(self):
        self.f.clear()
        ax = self.f.add_subplot(1, 1, 1)
        ax.plot(self.profile_data_x, self.profile_data_y)
        ax.plot(self.recorded_data_x, self.recorded_data_y, 'x')
        self.canvas.draw()

    def connect_clicked(self, *args):
        if self.oven is None:
            try:
                self.oven = oven.Oven(self.tty_entry.get_text())
            except:
                d = Gtk.MessageDialog(self.main_window,
                    0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK, "Could not open tty {}".format(self.tty_entry.get_text()))
                d.run()
                d.destroy()
                import traceback
                traceback.print_exc()
                return
            self.connect_button.set_label('gtk-disconnect')
            self.start_button.set_sensitive(True)

        else:
            self.oven.stop()
            self.oven = None
            self.connect_button.set_label('gtk-connect')
            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(False)

    def start_clicked(self, *args):
        if self.oven.start(self.profile):
            self.start_t = time.time()
            self.running = True
            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(True)

    def stop_clicked(self, *args):
        self.oven.stop()
        self.running = False
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

if __name__ == '__main__':
    profile = [
        (1, 110, 120),
        (1, 210, 150),
        (-1, 30, 60)
    ]
    ui = Ui(profile)
    Gtk.main()
