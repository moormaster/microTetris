#!/usr/bin/env python2

from tkinter import *

master = Tk()

canvas = Canvas(master, width=640, height=480)
canvas.pack()

canvas.create_rectangle(50, 50, 590, 430, fill="yellow", outline="yellow")
canvas.create_rectangle(55, 55, 585, 425, fill="black")

mainloop()

