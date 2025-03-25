"""
program: main.py

purpose: For project image_annotate, interactive image annotation.

comments: Places shapes, lines and text on an existing image in a canvas.

author: Russell Folks

history:
-------
01-02-2025  creation
... [see history.txt]
02-02-2025  Refine shape selection process.
02-04-2025  Debug reporting the shape center coordinates when dragging.
02-08-2025  Add 'constrain' parameter to drag_shape() to drag vertically
            or horizontally. Replace expand and contract functions with a
            single fxn, resize_shape().
02-11-2025  Update class headers. Update some function headers.
            Make file_path a local var. Remove old commented-code. Add frame
            for shapecanvas controls. Deactivate set_center().
02-13-2025  Add buttons to create rectangle or arc on the shape canvas. Change
            'circle' parameters to 'oval', the tk name of the object.
02-14-2025  Add controls to set shape width and height.
02-19-2025  Extract shape controls into tool_classes.py.
02-20-2025  Use trace_add to detect changes in myshapecanvas Spinbox.
02-22-2025  Refine the 'constrain' argument for drag_shape(). Remove inactive
            commented-out code.
02-24-2025  Update displayed shape center upon unselect. Extract code into
            new fxn get_and_display_center().
02-26-2025  Create new folder "canvas" at the same level as this project, and
            move canvas class definitions there.
03-01-2025  Group code for each canvas' controls with it. Add colorbar object
            to myshapecanvas, pass colorbar to set_color().
03-11-2025  Add widgets for rect and arc size. Use classes from canvas module.
03-14-2025  Add styles for selection of oval, rectangle and arc buttons.
03-15-2025  Simplify set_next_shape() to use only an event parameter. Remove
            some test code. Move each shape's size-setting code adjacent to
            the shape-creating button.
03-21-2025  Refactor set_next_shape_size() and the lambda that calls it.
03-24-2025  Add button styles. Add separate height/width for other shapes.
"""

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader

tc = SourceFileLoader("tc", "../utilities/tool_classes.py").load_module()
cnv = SourceFileLoader("cnv", "../canvas/canvas_classes.py").load_module()
cnv_ui = SourceFileLoader("cnv_ui", "../image_display_RF/canvas_ui.py").load_module()

def set_color(event, cb, canv):
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


def set_linewidth(var):
    """Set line width for lines or shapes on a canvas.

    parameter:
        var : line width, from the IntVar in adj_linewidth.
    """
    mydrawcanvas.linewidth = var.get()


def set_next_shape_size(canv=None, param=None, wid=None):
    # print(f'in report_name: {wid}, yields: {wid.get()}')
    canv.set_shape_parameter(param, wid.get())


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


def set_next_shape(ev):
    """Designate the next shape to be drawn in the shape canvas.

    The corresponding button is highlighted.
    """
    widget = ev.widget
    widget_name = widget.winfo_name()
    myshapecanvas.next_shape = widget_name

    oval.configure(style='Oval.TButton')
    rectangle.configure(style='Rectangle.TButton')
    arc.configure(style='Arc.TButton')

    widget.configure(style='Selected.TButton')


# additional callback option
# not currently used
# def set_test(ev, wid, s, canv):
#     # pass
#     print(f'in set_test, canv is {canv}')


root = tk.Tk()

# test here; implement in canvas_classes.py
# class Shape():
#     def __init__(self, id, center=(0,0), lc='black'):
#         self.id: str = id
#         self.center: tuple(int,int) = center
#         self.lc: str = lc
#
# objlist = []
#
# objlist.append(Shape(id='oval1', center=(10,20), lc='red'))
# objlist.append(Shape('rect1', (15,20), 'blue'))
# objlist.append(Shape('oval2', (20,30), 'black'))
# objlist.append(Shape('arc1'))

# will fail if 'oval2' is not found
# myobject_1 = [n for n in objlist if n.id == 'oval2'][0]
# print(f'oval2 center: {myobject_1.center=}')

# will work with any value (returns None if not found),
# could also return a flag like -1 or some other value
# myobject_2 = next((n for n in objlist if n.id == 'oval2'), None)
# if myobject_2 is not None:
#     print(f'{myobject_2.center=}')
# else:
#     print('obj not found')
#
# arc1 = next((n for n in objlist if n.id == 'arc1'), None)
# if arc1 is not None: arc1.lc = 'magenta'
# print(f'{arc1.lc=}')
# print('------------------------')



# module variables
# ----------------
# image file to be loaded; the object needs to be global
im_tk = None
linewidths = [str(i) for i in list(range(1, 11))]
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'magenta', 'black']
xs = list(range(0, 320, 40))
y1 = 0
y2 = 42

style=ttk.Style()
style.theme_use('alt')
style.configure('Oval.TButton', width=12, height=30)
style.configure('Rectangle.TButton', width=12, height=30)
style.configure('Arc.TButton', width=12, height=30)
style.configure('Selected.TButton', width=12, height=30, background='#afa')

style.map('Selected.TButton', background=[('selected', '#afa')])

# draw canvas ----------

draw_frame = tk.Frame(root)
mydrawcanvas = cnv.DrawCanvas(draw_frame,
                          mode='lines',
                          width=400,
                          height=500,
                          background='#ffa'
                          )
# print(mydrawcanvas._name)
# objects['mycanvas'] = mydrawcanvas

controls_1 = ttk.Frame(draw_frame, padding=2, relief='groove')

colorbar1 = tk.Canvas(controls_1, width=320, height=40)
for n, x in enumerate(xs):
    colorbar1.create_rectangle(x, y1, x + 40, y2, fill=colors[n], tags=colors[n])  # + str(n))
colorbar1.bind('<1>', lambda ev, cb=colorbar1, canv=mydrawcanvas: set_color(ev, cb, canv))
# colorbar1.bind('<1>', lambda ev, objs=objects: set_color(ev, objs))
colorbar1.pack()

status = ttk.Label(controls_1, text='mode:')
status.pack(side='left', padx=5)

status_value = ttk.Label(controls_1, foreground='blue', text=mydrawcanvas.mode)
status_value.pack(side='left')

cursor_posn = tk.Text(background='#ff0')

line_w = ttk.Label(controls_1, text='line width:')

linewidth_value = tk.IntVar(value=1)
adj_linewidth = ttk.Spinbox(controls_1,
                            width=3,
                            from_=1,
                            to=10,
                            values=linewidths,
                            wrap=True,
                            foreground='blue',
                            textvariable=linewidth_value,
                            command=lambda var=linewidth_value: set_linewidth(var))

adj_linewidth.pack(side='right', pady=5)
line_w.pack(side='right', padx=5)

# ---------- END draw canvas

# shape canvas ----------

shape_frame = tk.Frame(root)
myshapecanvas = cnv.ShapeCanvas(shape_frame,
                            width=400,
                            height=500,
                            background='cyan'
                            )

viewport1 = {'w': 400, 'h': 500, 'gutter': 10}

center_posn = {'x': 0, 'y': 0}

controls_2 = ttk.Frame(shape_frame, padding=2, relief='groove')

colorbar2 = tk.Canvas(controls_2, width=320, height=40)
for n, x in enumerate(xs):
    colorbar2.create_rectangle(x, y1, x + 40, y2, fill=colors[n], tags=colors[n])  # + str(n))
colorbar2.bind('<1>', lambda ev, cb=colorbar2, canv=myshapecanvas: set_color(ev, cb, canv))

open_button = tk.Button(controls_2, text="Open Image", command=open_picture)

oval = ttk.Button(controls_2, text='oval', name='oval', cursor='arrow',
                  style='Selected.TButton')
# oval.bind('<Button-1>', lambda ev: set_next_shape(ev))
oval.bind('<Button-1>', set_next_shape)

#       oval settings ----------
oval_widths = (20, 40, 60)
oval_width = tk.IntVar(value=oval_widths[0], name='ovalwidth')
# oval_width.trace_add(mode='write', callback=set_test)

settings_oval_w = tc.SelectionFrame(controls_2,
                                    cb_values=oval_widths,
                                    display_name='W',
                                    var=oval_width,
                                    callb=lambda canv=myshapecanvas, param='oval_width', wid=oval_width: set_next_shape_size(canv, param, wid),
                                    posn=[0, 3],
                                    stick='')

oval_heights = (20, 50, 70)
oval_height = tk.IntVar(value=oval_heights[0], name='ovalheight')
# oval_height.trace_add(mode='write', callback=set_next_shape_size)
settings_oval_h = tc.SelectionFrame(controls_2,
                                    cb_values=oval_heights,
                                    display_name='H',
                                    var=oval_height,
                                    callb=lambda canv=myshapecanvas, param='oval_height', wid=oval_height: set_next_shape_size(canv, param, wid),
                                    posn=[0, 4],
                                    stick='')

#       ---------- END oval settings

rectangle = ttk.Button(controls_2, text='rectangle', name='rectangle', cursor='arrow',
                       style='Rectangle.TButton')
# rectangle.bind('<Button-1>', lambda ev: set_next_shape(ev))
rectangle.bind('<Button-1>', set_next_shape)

#       rectangle settings ----------

rect_widths = (20, 40, 60)
rect_width = tk.IntVar(value=rect_widths[0], name='rectwidth')
myshapecanvas.set_shape_parameter('rect_height', 35)
# rect_width.trace_add(mode='write', callback=set_test)
settings_rect_w = tc.SelectionFrame(controls_2,
                                    cb_values=rect_widths,
                                    display_name='W',
                                    var=rect_width,
                                    callb=lambda canv=myshapecanvas, param='rect_width', wid=rect_width: set_next_shape_size(canv, param, wid),
                                    posn=[1, 3],
                                    stick='')

rect_heights = (20, 50, 70)
rect_height = tk.IntVar(value=rect_heights[0], name='rectheight')
# rect_height.trace_add(mode='write', callback=set_test)
settings_rect_h = tc.SelectionFrame(controls_2,
                                    cb_values=rect_heights,
                                    display_name='H',
                                    var=rect_height,
                                    callb=lambda canv=myshapecanvas, param='rect_height', wid=rect_height: set_next_shape_size(canv, param, wid),
                                    posn=[1, 4],
                                    stick='')

#       ---------- END rectangle settings

arc = ttk.Button(controls_2, text='arc', name='arc', cursor='arrow',
                 style='Arc.TButton')
# arc.bind('<Button-1>', lambda ev: set_next_shape(ev))
arc.bind('<Button-1>', set_next_shape)

#       arc settings ----------

arc_widths = (20, 40, 60)
arc_width = tk.IntVar(value=arc_widths[0], name='arcwidth')
# arc_width.trace_add(mode='write', callback=set_test)
settings_arc_w = tc.SelectionFrame(controls_2,
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
settings_arc_h = tc.SelectionFrame(controls_2,
                                   cb_values=arc_heights,
                                   display_name='H',
                                   var=arc_height,
                                   callb=lambda canv=myshapecanvas, param='arc_height',
                                                wid=arc_height: set_next_shape_size(canv, param, wid),
                                   posn=[2, 4],
                                   stick='')

#       ---------- END arc settings

controls_2.columnconfigure(0, weight=1)
controls_2.columnconfigure(1, weight=1)
controls_2.columnconfigure(2, weight=1)

colorbar2.grid(column=0,   row=0, columnspan=3, pady=5)
open_button.grid(column=1, row=1, pady=5)
oval.grid(column=0,        row=2, padx=5, pady=5)
rectangle.grid(column=1,   row=2, padx=5, pady=5)#, sticky='ew')
arc.grid(column=2,         row=2, padx=5, pady=5)#, sticky='ew')

# ---------- END shape canvas


quit_fr = ttk.Frame(root)
btnq = ttk.Button(quit_fr,
                  text="Quit",
                  command=root.quit,
                  style="Oval1.TButton")

draw_frame.grid(column=0, row=0, padx=10)
mydrawcanvas.grid(column=0, row=1)
controls_1.grid(column=0, row=2, sticky='ew')

shape_frame.grid(column=1, row=0)
myshapecanvas.grid(column=0, row=1)
controls_2.grid(column=0, row=2, sticky='ew')

btnq.pack()
quit_fr.grid(column=0, row=1, pady=10)

if __name__ == '__main__':
    root.mainloop()
