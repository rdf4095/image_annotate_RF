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
"""
"""
TODO: 1. Change logic for shape size by having create_shape read the h,w 
      spinboxes for each shape, and calculate the start_posn and end_posn.
      Then you don't need posn arguments in the fxn call.
"""

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader

import tool_classes as tc
cnv = SourceFileLoader("cnv", "../image_display_RF/canvas_ui.py").load_module()
cnv_classes = SourceFileLoader("cnv_classes", "../canvas/canvas_classes.py").load_module()
# tc = SourceFileLoader("tc", "./tool_classes.py").load_module()

def set_color(event, canvaslist):
    """Set color for lines drawn on canvases."""
    color_choice = colorbar.gettags('current')[0]

    for canv in canvaslist:
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

    parameter: var = line width, from the IntVar in adj_linewidth.
    """
    mydrawcanvas.linewidth = var.get()


def set_oval_size(var, index, mode):
    match var:
        case 'ovalwidth':
            myshapecanvas.oval_width = oval_width.get()
        case 'ovalheight':
            myshapecanvas.oval_height = oval_height.get()


def report_name(n):
    print(f'reported: {n}')


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
    imsize = cnv.init_image_size(im, viewport1)
    im_resize = im.resize((imsize['w'], imsize['h']))
    im_tk = ImageTk.PhotoImage(im_resize)

    placement = cnv.get_1_posn(viewport1, imsize['w'], imsize['h'],
                               ('center', 'center'))
    # print(f'placement x,y: {placement.x}, {placement.y}')

    imid = canv.create_image(placement.x, placement.y,
                             anchor=tk.NW,
                             image=im_tk,
                             tag = 'image1')


def set_next_shape(s):
    """Designate the next shape to be drawn in the shape canvas."""
    myshapecanvas.next_shape = s


root = tk.Tk()

# image file to be loaded; the object needs to be global
im_tk = None

draw_frame = tk.Frame(root)
mydrawcanvas = cnv_classes.DrawCanvas(draw_frame,
                          mode='lines',
                          width=400,
                          height=500,
                          background='#ffa'
                          )

shape_frame = tk.Frame(root)
myshapecanvas = cnv_classes.ShapeCanvas(shape_frame,
                            width=400,
                            height=500,
                            background='cyan'
                            )

# no londer needed?
# ...can we ad hoc bind some other action like this?
# myshapecanvas.bind('<Button-3>', lambda event: self.select_shape(event))

linewidths = [str(i) for i in list(range(1, 11))]

viewport1 = {'w': 400, 'h': 500, 'gutter': 10}


# draw canvas controls ----------
controls_1 = ttk.Frame(draw_frame, padding=2, relief='groove')

colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'magenta', 'black']
xs = list(range(0, 320, 40))
y1 = 0
y2 = 42
colorbar = tk.Canvas(controls_1, width=320, height=40)
for n, x in enumerate(xs):
    colorbar.create_rectangle(x, y1, x + 40, y2, fill=colors[n], tags=colors[n])  # + str(n))
colorbar.bind('<1>', lambda ev, canv=(mydrawcanvas, myshapecanvas): set_color(ev, canv))
colorbar.pack()

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
# ---------- END draw canvas controls


# shape canvas controls --------------
# needed?
# shape_var = tk.StringVar(value=shape_value)

center_posn = {'x': 0, 'y': 0}

controls_2 = ttk.Frame(shape_frame, padding=2, relief='groove')

open_button = tk.Button(controls_2, text="Open Image", command=open_picture)
open_button.grid(column=1, row=0, pady=5)

oval = ttk.Button(controls_2, text='oval', name='oval', cursor='arrow', command=lambda w='oval': set_next_shape(w))
oval.grid(column=0, row=1, padx=5, pady=5)

# oval settings ===============

oval_widths = (10, 40, 70)
oval_width = tk.IntVar(value=oval_widths[0], name='ovalwidth')
oval_width.trace_add(mode='write', callback=set_oval_size)
settings_w = tc.ToolFrame(controls_2,
                        cb_values=oval_widths,
                        display_name='W',
                        var=oval_width,
                        callb=report_name,
                        posn=[2, 0],
                        stick='')

oval_heights = (15, 45, 75)
oval_height = tk.IntVar(value=oval_heights[0], name='ovalheight')
oval_height.trace_add(mode='write', callback=set_oval_size)
settings_h = tc.ToolFrame(controls_2,
                        cb_values=oval_heights,
                        display_name='H',
                        var=oval_height,
                        callb=report_name,
                        posn=[3, 0],
                        stick='')

# =============== END oval settings

rectangle = ttk.Button(controls_2, text='rectangle', name='rectangle', cursor='arrow', command=lambda w='rectangle': set_next_shape(w))
rectangle.grid(column=1, row=1, padx=5, pady=5)#, sticky='ew')

arc = ttk.Button(controls_2, text='arc', name='arc', cursor='arrow', command=lambda w='arc': set_next_shape(w))
arc.grid(column=2, row=1, padx=5, pady=5)#, sticky='ew')

controls_2.columnconfigure(0, weight=1)
controls_2.columnconfigure(1, weight=1)
controls_2.columnconfigure(2, weight=1)

# ---------- END shape canvas controls


quit_fr = ttk.Frame(root)
btnq = ttk.Button(quit_fr,
                  text="Quit",
                  command=root.quit,
                  style="MyButton1.TButton")

# draw_frame.grid(column=0, row=1)
draw_frame.grid(column=0, row=0)
mydrawcanvas.grid(column=0, row=1)
controls_1.grid(column=0, row=3, sticky='ew')

# shape_frame.grid(column=1, row=1)
shape_frame.grid(column=1, row=0)
myshapecanvas.grid(column=0, row=1)
controls_2.grid(column=0, row=2, sticky='ew')

btnq.pack()
# quit_fr.grid(column=0, row=4, pady=10)
quit_fr.grid(column=0, row=1, pady=10)

if __name__ == '__main__':
    root.mainloop()
