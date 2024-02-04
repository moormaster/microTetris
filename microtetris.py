#!/usr/bin/env python

#
# microTetris 0.1
#
# Copyright (C) 2006, Federico Pelloni <federico.pelloni@gmail.com>
#
# microTetris is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# microTetris is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with microTetris; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, 
# Boston, MA  02110-1301  USA
#
# ---
#
# microTetris web: http://microtetris.sourceforge.net/
#
# If you download the .py file, you can see the full license text at:
# http://www.opensource.org/licenses/gpl-license.php
#

import platform
import random
import sys
from tkinter import *

class Game(Frame):
    
    # Row number
    rows = 20
    # Column number
    columns = 11
    # Size of a square
    square_size = 3
    # Spacing between squares
    spacing = 1
    
    # Speed (interval between two ticks in milliseconds: larger for slower speed)
    timeout = 800
    
    keys = {
        "n":     "new_game",
        "p":     "toggle_pause",
        "Left":    "left",
        "Right":    "right",
        "Up":     "rotate",
        "Down":    "down",
        "space":    "drop"
    }
    
    
    # Red, Green, Blue triplets
    colors = ( 
            "yellow",   # 1 Yellow
            "green",   # 2 Green
            "light blue",   # 3 Blue
            "tan",   # 4 Purple
            "cyan",   # 5 Cyan
            "red",   # 6 Red
            "white",   # 7 White
        )
    
    
    # Shape matrix: 0 transparent, > 0 colour block
    blocks = (
            ((2, 2, 2), (2, 0, 0)),     # Green L
            ((6, 6, 6), (0, 0, 6)),     # Reversed Red L
            ((3, 3, 3), (0, 3, 0)),     # Blue T
            ((4, 4, 4, 4), ),           # Purple I
            ((7, 7, 0), (0, 7, 7)),     # White "Z"
            ((0, 1, 1), (1, 1, 0)),     # Yellow "S"
            ((5, 5), (5, 5))            # Cyan square
        )
        
    
    
    icon = [ "48 48 5 1",
            "  c red",
            ". c #FFFFFF",
            "X c #37C837",
            "# c #FFD42A",
            "= c #00ABD4",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############.                                   ",
            "############............           .............",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "#######################.           .============",
            "############........................============",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            "############.XXXXXXXXXX.========================",
            ".............XXXXXXXXXX.............============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============",
            "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.============"]
    
    
    paused = True
    tick_active = False
    falling_block = None
    row_matrix = None
    
    def __init__(self, master=None, screen_dimension=None, screen_position=None):
        Frame.__init__(self, master)
        self.pack()

        self.master.title("microTetris")

        if platform.system() == "Windows":
            self.master.overrideredirect(True)
        
        # TODO: set self.icon as application icon
        # if self.show_icon:
        #    w.set_icon(GdkPixbuf.Pixbuf.new_from_xpm_data(self.icon))

        self.width = self.columns * (self.square_size + self.spacing) - self.spacing + 4
        self.height = self.rows * (self.square_size + self.spacing) - self.spacing + 4
      
        self.master.bind("<Destroy>", self.quit)
        self.master.bind("<q>", self.quit)
        self.master.bind("<Escape>", self.quit)
        self.master.bind("<FocusIn>", lambda *a: self.toggle_pause(False))
        self.master.bind("<FocusOut>", lambda *a: self.toggle_pause(True))
        self.master.bind("<KeyPress>", self.catch_keypress)

        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()
        
        if screen_dimension is None or screen_position is None:
            sx = 0
            sy = 0
            sw = self.master.winfo_screenwidth()
            sh = self.master.winfo_screenheight()

        if not screen_dimension is None:
            sx = 0
            sy = 0
            sw = screen_dimension[0]
            sh = screen_dimension[1]

        if not screen_position is None:
            sx = screen_position[0]
            sy = screen_position[1]

        print("Recognized screen size of " + str(sw) + "x" + str(sh) + " at position " + str(sx) + ", " + str(sy))

        self.master.update()
        x = sx + sw - self.master.winfo_width()
        y = sy + sh - self.master.winfo_height() - 48
        print("Moving window of size " + str(self.master.winfo_width()) + "x" + str(self.master.winfo_height()) + " to position " + str(x) + ", " + str(y))

        self.master.geometry("+{}+{}".format(x, y))
 
        random.seed()

    def catch_keypress(self, event):
        k = event.keysym
        if k in self.keys:
            f = self.keys[k]
            assert hasattr(self, f), "Missing callback for '%s'" % f
            getattr(self, f)()
    
    def quit(self, event):
        self.master.destroy()
    
    def draw(self):
        cr = self.canvas
        area = [0, 0, self.width, self.height ]

        cr.delete("all")
        cr.create_rectangle(*area, fill="black")
        cr.create_rectangle(*area, outline="#808080")
        
        if self.falling_block is not None:
            
            basex = self.falling_block['x'] * (self.square_size + self.spacing) + 2
            basey = self.falling_block['y'] * (self.square_size + self.spacing) + 2
            i = 0
            for r in self.falling_block['block']:
                j = 0
                for c in r:
                    if c > 0:
                        x = basex + j * (self.square_size + self.spacing)
                        y = basey + i * (self.square_size + self.spacing)
                        cr.create_rectangle(x, y, x + self.square_size, y + self.square_size, fill=self.colors[c-1])
                    j += 1
                i += 1
         
        i = 0       
        for r in self.row_matrix:
            j = 0
            for c in r:
                if c > 0:
                    x = j * (self.square_size + self.spacing) + 2
                    y = i * (self.square_size + self.spacing) + 2
                    cr.create_rectangle(x, y, x + self.square_size, y + self.square_size, fill=self.colors[c-1])
                j += 1
            i += 1
        
    # Game routine
    def new_game(self):
        self.row_matrix = [[0 for i in range(1, self.columns + 1)] for j in range(1, self.rows + 1)]
        self.falling_block = None
        self.toggle_pause(False)
        self.tick(extra=self.tick_active)
        self.tick_active = True
    
    def new_block(self):
        
        block = random.choice(self.blocks)
        rotation = random.randint(0, 3)
        for i in range(rotation):
            block = self.rotate_block(block)
        self.falling_block = dict(block = block, x = (self.columns - len(block[0])) // 2, y = 0)
        
    def tick(self, extra=None):
        if not self.paused:
            if self.falling_block is None:
                self.new_block()
            else:
                fb = self.falling_block
            
                touched = False
            
                if len(fb['block']) + fb['y'] == self.rows:
                    touched = True
                else:
                    i = 0
                    for r in fb['block']:
                        j = 0
                        for c in r:
                            if c > 0:
                                y = fb['y'] + i
                                x = fb['x'] + j
                                if (self.row_matrix[y + 1][x] > 0):
                                    touched = True
                                    break
                            j += 1
                        i += 1
            
                if touched:
                    self.fix_block(fb)
                    self.new_block()
                else:
                    fb['y'] += 1
            
            self.draw()

        if not extra:
            self.after(self.timeout, self.tick)
         
        return not self.paused
    
    def fix_block(self, fb):
        if fb['y'] <= 1:
            self.new_game()
            return
        i = 0
        for r in fb['block']:
            j = 0
            for c in r:
                if c > 0:
                    self.row_matrix[fb['y'] + i][fb['x'] + j] = c
                j += 1
            i += 1
        for r in self.row_matrix:
            if 0 not in r:
                self.row_matrix.remove(r)
                self.row_matrix.insert(0, [0 for i in range(1, self.columns + 1)])
    
    def toggle_pause(self, paused = None):
        if paused is None:
            paused = not self.paused
            
        self.paused = paused
    
    def left(self):
        if not self.paused:
            x = max(self.falling_block['x'] - 1, 0)
            self.falling_block['x'] = x
            self.draw()
       
    def right(self):
        if not self.paused:
            x = min(self.falling_block['x'] + 1, self.columns - len(self.falling_block['block'][0]))
            self.falling_block['x'] = x
            self.draw()
        
    def rotate(self):
        if not self.paused:
            b = self.falling_block['block']
            b = self.rotate_block(b)
            self.falling_block['block'] = b
            self.draw()

    def down(self):
        if not self.paused:
            self.tick(extra=True)
    
    def drop(self):
        if not self.paused:
            fb = self.falling_block
            
            touched = True
            y = self.rows - len(fb['block'])
            while touched:
                touched = False
                i = 0
                for r in fb['block']:
                    cy = y + i
                    j = 0
                    for c in r:
                        if c > 0 and self.row_matrix[cy][fb['x']+j] > 0:
                            touched = True
                            break
                        j += 1
                    i += 1
                y -= 1
            fb['y'] = y + 1
            self.fix_block(fb)
            self.new_block()
            self.tick(extra=True)
        
    def rotate_block(self, matrix):

        rows = len(matrix[0])
        cols = len(matrix)
        new = []
        for i in range(rows):
            cur = []
            new.append(cur)
            for j in range(cols):
                cur.append(matrix[j][rows - i - 1])
        return new
        

if __name__ == "__main__":
    root = Tk()

    screen_dimension = None
    screen_position = None
    if len(sys.argv) >= 3:
        screen_dimension = [ int(sys.argv[1]), int(sys.argv[2]) ]
    if len(sys.argv) >= 5:
        screen_position = [ int(sys.argv[3]), int(sys.argv[4]) ]


    game = Game(root, screen_dimension, screen_position)
    game.new_game()
    root.mainloop()
