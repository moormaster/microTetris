#!/usr/bin/env python2

from tkinter import *

class Moep:
    def escape(self, event):
        print("Escape!!!")

    def keyPress(self, event):
        print("Key pressed: {}".format(event))

master = Tk()

frame = Frame(master)
frame.pack()

canvas = Canvas(frame, width=640, height=480)
canvas.pack()

canvas.create_rectangle(50, 50, 590, 430, fill="yellow", outline="yellow")
canvas.create_rectangle(55, 55, 585, 425, fill="black")

moep = Moep()

master.bind("<Escape>", moep.escape)
master.bind("<KeyPress>", moep.keyPress)

mainloop()

