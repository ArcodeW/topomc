import logging
import os

import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d

from topomc import app
from topomc.common.coordinates import Coordinates
from topomc.common.logger import Logger
from topomc.symbol import Symbol

MARGIN = 3

class MapRender:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        plt.figure(f"Map of {app.settings['World']}")

        self.get_settings()
        self.get_save_loc()

        self.max_len = max(np.floor(self.width / 16), np.floor(self.height / 16))

    def get_settings(self):
        self.smoothness = app.settings["Smoothness"]
        self.contour_index = app.settings["Index"]
        self.save_loc = app.settings["PDF save location"]
        self.line_width = app.settings["Line width"]

    def get_save_loc(self):
        if self.save_loc:
            save_loc = os.path.normpath(self.save_loc)
            if not save_loc.endswith(".pdf"):
                if save_loc.endswith(os.sep):
                    self.save_loc = save_loc + "map.pdf"
                else:
                    self.save_loc = save_loc + ".pdf" 

    @staticmethod
    def smoothen(iist, smoothness, is_closed=True):
        x, y = Coordinates.transpose_list(iist)

        if smoothness:
            if is_closed:
                x_start, x_end = x[0:MARGIN], x[-MARGIN:]
                y_start, y_end = y[0:MARGIN], y[-MARGIN:]
                x = x_end + x + x_start
                y = y_end + y + y_start

            x = gaussian_filter1d(x, smoothness)
            y = gaussian_filter1d(y, smoothness)

            if is_closed:
                x = x[MARGIN:-MARGIN + 1]
                y = y[MARGIN:-MARGIN + 1]
        return x, y

    def plot(self, symbol):

        if symbol.type == Symbol.type.LINEAR:
            Logger.log(logging.info, f"Building {symbol.__class__.__name__} symbol...", sub=1)
            renders = symbol.render()
            Logger.log(logging.info, f"Rendering {symbol.__class__.__name__} symbol...", sub=1)
            if renders:
                for x, y in renders:
                    plt.plot(x,y, symbol.color, linewidth=symbol.linewidth / 3) 
        if symbol.type == Symbol.type.AREA:
            raise NotImplementedError
        if symbol.type == Symbol.type.POINT:
            raise NotImplementedError

    def show(self):
        
        plt.axis("off")

        axes = plt.gca()
        graph = plt.gcf()

        axes.set_aspect(1)
        axes.set_xlim(0, self.width)
        axes.set_ylim(0, self.height)
        axes.invert_xaxis()

        scale_ratio = app.settings["Scale"]
        divisor, scale = scale_ratio.split(":")
        scale = int(scale) / int(divisor)

        if self.save_loc:
            # units * 100(metres) / scale * inch conversion
            graph.set_size_inches(self.width * 100 / scale * 0.393701, self.height * 100 / scale * 0.393701)
            graph.savefig(self.save_loc)

        for line in axes.lines:
            line.set_linewidth(
                line.get_linewidth() * 2**(4 - np.log2(self.max_len)))

        window_size = app.settings["Preview size"]
        graph.set_size_inches(8 * window_size, 8 * window_size)
        if graph.canvas.toolbar:
            graph.canvas.toolbar.pack_forget()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)


        Logger.log_done()
        Logger.log(logging.info, "Showing preview...", time_it=False)
        plt.show()
        Logger.log_done()


    def debug(self, symbol):
        plt.close() # close current figure
        plt.figure(f"Debugging chunk {'x'} {'z'}")
        
        axes = plt.gca()
        graph = plt.gcf()

        axes.set_xlim(0, 15)
        axes.set_ylim(0, 15)
        axes.invert_yaxis()
        axes.set_aspect(1)

        graph.set_size_inches(8, 8)
        plt.xticks(range(0, 15))
        plt.yticks(range(0, 15))
        plt.grid(color='#000', linestyle='-', linewidth=1, which="both")

        symbol.debug()

        Logger.log(logging.info, "Showing preview...", time_it=False)
        print()

        save_loc = app.settings["PDF save location"]
        if save_loc:
            save_loc = os.path.normpath(save_loc)
            if not save_loc.endswith(".pdf"):
                if save_loc.endswith(os.sep):
                    save_loc = save_loc + "map.pdf"
                else:
                    save_loc = save_loc + ".pdf"
        if save_loc:
            graph.savefig(save_loc)

        plt.show()
