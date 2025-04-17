"""
program: main.py

purpose: For project image_annotate, interactive image annotation.

comments: Places shapes, lines and text on an existing image in a canvas.

author: Russell Folks

history:
-------
01-02-2025  creation
... [see history.txt]
03-01-2025  Group code for each canvas' controls with it. Add colorbar object
            to myshapecanvas, pass colorbar to set_color().
03-11-2025  Add widgets for rect and arc size. Use classes from canvas module.
03-14-2025  Add styles for selection of oval, rectangle and arc buttons.
03-15-2025  Simplify set_next_shape() to use only an event parameter. Remove
            some test code. Move each shape's size-setting code adjacent to
            the shape-creating button.
03-21-2025  Refactor set_next_shape_size() and the lambda that calls it.
03-24-2025  Add button styles. Add separate height/width for other shapes.
03-31-2025  Add canvas parameter to set_linewidth(). Remove drawcanvas: that
            code is used in sketch.py.
"""

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader

tc = SourceFileLoader("tc", "../utilities/tool_classes.py").load_module()
cnv = SourceFileLoader("cnv", "../canvas/canvas_classes.py").load_module()
cnv_ui = SourceFileLoader("cnv_ui", "../canvas/canvas_ui.py").load_module()

def set_color(event, canv, cb):
    """Set color for lines drawn on canvases.

    Parameters:
        event: widget event bound to this function
        cb : colorbar object
        canv : canvas object
    """
    # print(f'handling event {event}')
    # print(f' set_color on canv: {canv.name}')
    color_choice = cb.gettags('current')[0]

    canv.linecolor = color_choice
    report_color(canv, color_choice)


def report_color(canv, textstr) -> None:
    """Display line color in lower left of canvas."""
    canv.delete('color_text')
    canv.create_text(10,
                     canv.height - 10,
                     fill=textstr,
                     text=textstr,
                     anchor='w',
                     tags='color_text')


def set_linewidth(canv, var):
    """Set line width for lines or shapes on a canvas.

    parameter:
        var : line width, from the IntVar in adj_linewidth.
    """
    canv.linewidth = var.get()


def open_picture():
    """Manage user selection of an image file, for display in a canvas."""
    file_path = filedialog.askopenfilename(title="Select Image File",
                                           initialdir='../image_display_RF/images',
                                           filetypes=[("PNG files",'*.png'),
                                                      ("JPEG file",'*.jpeg')])

    add_image(myshapecanvas, file_path)


def add_image(canv, fpath):
    """Display an image in a canvas."""
    global im_tk

    im = Image.open(fpath)
    imsize = cnv_ui.init_image_size(im, viewport1)
    im_resize = im.resize((imsize['w'], imsize['h']))
    im_tk = ImageTk.PhotoImage(im_resize)

    placement = cnv_ui.get_1_posn(viewport1, imsize['w'], imsize['h'],
                               ('center', 'center'))
    # print(f'placement x,y: {placement.x}, {placement.y}')

    canv.create_image(placement.x, placement.y,
                             anchor=tk.NW,
                             image=im_tk,
                             tag = 'image1')


def set_next_shape_size(canv=None, param=None, wid=None):
    canv.set_shape_parameter(param, wid.get())


def set_next_shape(ev):
    """Designate the next type of shape to be drawn in the canvas.

    The corresponding button is highlighted.
    """
    widget = ev.widget
    widget_name = widget.winfo_name()
    myshapecanvas.next_shape = widget_name

    oval.configure(style='Oval.TButton')
    rectangle.configure(style='Rectangle.TButton')
    arc.configure(style='Arc.TButton')

    widget.configure(style='Selected.TButton')


# def set_to_black(ev):
#     myshapecanvas.selected.linecolor = 'black'


# NOT CURRENTLY USED
# additional callback option
# def set_test(ev, wid, s, canv):
#     # pass
#     print(f'in set_test, canv is {canv}')


root = tk.Tk()

# module variables
# ----------------
# image file to be loaded; the object needs to be global
im_tk = None

linewidths = [str(i) for i in list(range(1, 11))]
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'magenta', 'black']
xs = list(range(0, 320, 40))
y1 = 0
y2 = 42

active_color = "#afa"

style=ttk.Style()
style.theme_use('alt')
style.configure('Oval.TButton', width=12, height=30)
style.configure('Rectangle.TButton', width=12, height=30)
style.configure('Arc.TButton', width=12, height=30)
style.configure('Selected.TButton', width=12, height=30, background=active_color)

style.map('Selected.TButton', background=[('selected', active_color)])

shape_frame = tk.Frame(root)
myshapecanvas = cnv.ShapeCanvas(shape_frame,
                            width=400,
                            height=500,
                            background='cyan'
                            )

viewport1 = {'w': 400, 'h': 500, 'gutter': 10}

center_posn = {'x': 0, 'y': 0}

controls = ttk.Frame(shape_frame, padding=2, relief='groove')

basic_controls = ttk.Frame(controls)

colorbar = tk.Canvas(basic_controls, width=320, height=40)
for n, x in enumerate(xs):
    colorbar.create_rectangle(x, y1, x + 40, y2, fill=colors[n], tags=colors[n])  # + str(n))
colorbar.bind('<1>', lambda ev, canv=myshapecanvas, cb=colorbar: set_color(ev, canv, cb))



linewidths = [str(i) for i in list(range(1,11))]
lw1 = ttk.Label(basic_controls, text='line width:')

line_w1 = tk.IntVar(value=1)
adj_linewidth1 = ttk.Spinbox(basic_controls,
                            width=3,
                            from_=1,
                            to=10,
                            values=linewidths,
                            wrap=True,
                            foreground='blue',
                            textvariable=line_w1,
                            command=lambda canv=myshapecanvas, var=line_w1: set_linewidth(canv, var))
# adj_linewidth1.pack(side='right', pady=5)
# lw1.pack(side='right', padx=5)


shape_controls = ttk.Frame(controls, relief='raised')

open_button = tk.Button(shape_controls, text="Open Image", command=open_picture)

oval = ttk.Button(shape_controls, text='oval', name='oval', cursor='arrow',
                  style='Selected.TButton')
# oval.bind('<Button-1>', lambda ev: set_next_shape(ev))
oval.bind('<Button-1>', set_next_shape)

#       oval settings ----------
oval_widths = (20, 40, 60)
oval_width = tk.IntVar(value=oval_widths[0], name='ovalwidth')
# oval_width.trace_add(mode='write', callback=set_test)

settings_oval_w = tc.SelectionFrame(shape_controls,
                                    cb_values=oval_widths,
                                    display_name='W',
                                    var=oval_width,
                                    callb=lambda canv=myshapecanvas, param='oval_width', wid=oval_width: set_next_shape_size(canv, param, wid),
                                    posn=[0, 3],
                                    stick='')

oval_heights = (20, 50, 70)
oval_height = tk.IntVar(value=oval_heights[0], name='ovalheight')
# oval_height.trace_add(mode='write', callback=set_next_shape_size)
settings_oval_h = tc.SelectionFrame(shape_controls,
                                    cb_values=oval_heights,
                                    display_name='H',
                                    var=oval_height,
                                    callb=lambda canv=myshapecanvas, param='oval_height', wid=oval_height: set_next_shape_size(canv, param, wid),
                                    posn=[0, 4],
                                    stick='')

#       ---------- END oval settings

rectangle = ttk.Button(shape_controls, text='rectangle', name='rectangle', cursor='arrow',
                       style='Rectangle.TButton')
# rectangle.bind('<Button-1>', lambda ev: set_next_shape(ev))
rectangle.bind('<Button-1>', set_next_shape)

#       rectangle settings ----------

rect_widths = (20, 40, 60)
rect_width = tk.IntVar(value=rect_widths[0], name='rectwidth')
myshapecanvas.set_shape_parameter('rect_height', 35)
# rect_width.trace_add(mode='write', callback=set_test)
settings_rect_w = tc.SelectionFrame(shape_controls,
                                    cb_values=rect_widths,
                                    display_name='W',
                                    var=rect_width,
                                    callb=lambda canv=myshapecanvas, param='rect_width', wid=rect_width: set_next_shape_size(canv, param, wid),
                                    posn=[1, 3],
                                    stick='')

rect_heights = (20, 50, 70)
rect_height = tk.IntVar(value=rect_heights[0], name='rectheight')
# rect_height.trace_add(mode='write', callback=set_test)
settings_rect_h = tc.SelectionFrame(shape_controls,
                                    cb_values=rect_heights,
                                    display_name='H',
                                    var=rect_height,
                                    callb=lambda canv=myshapecanvas, param='rect_height', wid=rect_height: set_next_shape_size(canv, param, wid),
                                    posn=[1, 4],
                                    stick='')

#       ---------- END rectangle settings

arc = ttk.Button(shape_controls, text='arc', name='arc', cursor='arrow',
                 style='Arc.TButton')
# arc.bind('<Button-1>', lambda ev: set_next_shape(ev))
arc.bind('<Button-1>', set_next_shape)

#       arc settings ----------

arc_widths = (20, 40, 60)
arc_width = tk.IntVar(value=arc_widths[0], name='arcwidth')
# arc_width.trace_add(mode='write', callback=set_test)
settings_arc_w = tc.SelectionFrame(shape_controls,
                                   cb_values=arc_widths,
                                   display_name='W',
                                   var=arc_width,
                                   callb=lambda canv=myshapecanvas, param='arc_width',
                                                wid=arc_width: set_next_shape_size(canv, param, wid),
                                   posn=[2, 3],
                                   stick='')

arc_heights = (20, 50, 70)
arc_height = tk.IntVar(value=arc_heights[0], name='archeight')
# arc_height.trace_add(mode='write', callback=set_test)
settings_arc_h = tc.SelectionFrame(shape_controls,
                                   cb_values=arc_heights,
                                   display_name='H',
                                   var=arc_height,
                                   callb=lambda canv=myshapecanvas, param='arc_height',
                                                wid=arc_height: set_next_shape_size(canv, param, wid),
                                   posn=[2, 4],
                                   stick='')

#       ---------- END arc settings

quit_fr = ttk.Frame(root)
btnq = ttk.Button(quit_fr,
                  text="Quit",
                  command=root.quit,
                  style="Oval1.TButton")

# this grid works okay:
# controls.columnconfigure(0, weight=1)
# controls.columnconfigure(1, weight=1)
# controls.columnconfigure(2, weight=1)
#
# colorbar.grid(column=0,    row=0, pady=5, padx=5)
#
# lw1.grid(column=1,         row=0, pady=5, sticky='e')
# adj_linewidth1.grid(column=2, row=0, pady=5, padx=5, sticky='w')
#
# basic_controls.grid(column=0, row=0)
#
# open_button.grid(column=1, row=1, pady=5)
# oval.grid(column=0,        row=2, padx=20, pady=5)
# rectangle.grid(column=1,   row=2, padx=20, pady=5)#, sticky='ew')
# arc.grid(column=2,         row=2, padx=20, pady=5)#, sticky='ew')
#
# shape_controls.grid(column=0, row=1, columnspan=3)
#
# shape_frame.grid(column=0, row=0)
# myshapecanvas.grid(column=0, row=1)
# controls.grid(column=0, row=2, sticky='ew')


# try this grid ----------
controls.columnconfigure(0, weight=1)
controls.columnconfigure(1, weight=1)
controls.columnconfigure(2, weight=1)

# needed ?
# basic_controls.columnconfigure(0, weight=2)
# basic_controls.columnconfigure(1, weight=1)
# basic_controls.columnconfigure(2, weight=1)

colorbar.grid(column=0,    row=0, pady=5, padx=5)
lw1.grid(column=1,         row=0, pady=5, sticky='e')
adj_linewidth1.grid(column=2, row=0, pady=5, padx=5, sticky='w')

basic_controls.grid(column=0, row=0)

open_button.grid(column=1, row=1, pady=5)
oval.grid(column=0,        row=2, padx=20, pady=5)
rectangle.grid(column=1,   row=2, padx=20, pady=5)#, sticky='ew')
arc.grid(column=2,         row=2, padx=20, pady=5)#, sticky='ew')

shape_controls.grid(column=0, row=1, columnspan=3)

shape_frame.grid(column=0, row=0)
myshapecanvas.grid(column=0, row=1)
controls.grid(column=0, row=2, sticky='ew')
# ---------- END try this grid


btnq.pack()
quit_fr.grid(column=0, row=1, pady=10)

if __name__ == '__main__':
    root.mainloop()
