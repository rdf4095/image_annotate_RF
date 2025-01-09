"""
program: main.py

purpose: For project image_annotate, interactive image annotation.

comments: Places shapes, lines and text on an existing image in a canvas.

author: Russell Folks

history:
-------
01-02-2025  creation
01-05-2025  Begin adding shape controls.
01-06-2025  User can select a local image file.
01-08-2025  Add functions to enlarge or reduce size of a circle object.
01-09-2025  Add function to drag the current shape to a new location.
"""
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, filedialog

import canvas_ui as cnv


class Sketchpad(tk.Canvas):
    """
    Sketchpad : Defines a Canvas for interactive drawing.

    Extends: tk.Canvas

    Attributes
    ----------

    Methods
    -------
    method_1:
        text
    """

    def __init__(self, parent,
                 width=320,
                 height=320,
                 mode='lines',
                 background='#ffa',
                 linewidth=1
                 ):
        """
        Inits a Sketchpad object.

        Parameters
        ----------
        width : Int
            Canvas width.
        height : Int
            Canvas height.

        Methods
        -------
        point_init:
            Defines a Point object for x-y Canvas position.
        """

        self.width = width
        self.height = height
        self.mode = mode
        self.background = background
        self.linewidth = linewidth

        super().__init__(parent,
                         width=self.width,
                         height=self.height,
                         background=self.background)

        self.linecolor = 'black'
        self.firstx = 0
        self.firsty = 0

        self.startx = 0
        self.starty = 0
        self.previousx = 0
        self.previousy = 0
        self.line_count = 0
        self.points = []
        self.linetags = []

        match self.mode:
            case 'freehand':
                self.bind('<Button-1>', self.set_start)
                # self.bind('<B1-Motion>', self.draw_path)
            case 'lines':
                self.bind('<Button-1>', self.draw_line)
                self.bind('<Double-1>', self.double_click)
                self.bind('<Button-3>', self.undo_line)
            case 'shapes':
                self.bind('<Button-1>', self.set_shape)
                self.bind('<Shift-Motion>', self.drag_shape)
                self.bind('<Control-Motion>', self.expand_shape)
                self.bind('<Alt-Motion>', self.contract_shape)
                # use scrollwheel if available (also works for middle button
                # plus trackbutton on ThinkPad)
                # self.bind('<Button-4>', self.expand_shape)
                # self.bind('<Button-5>', self.contract_shape)
                self.bind('<Shift-Up>', self.nudge_shape)
                # self.bind('<Shift-Down>', self.nudge_shape)
                # self.bind('<Shift-Left>', self.nudge_shape)
                # self.bind('<Shift-Right>', self.nudge_shape)

        self.bind("<Motion>", self.report_posn)
        self.bind("<Leave>", self.clear_posn)

        def point_init(thispoint, xval: int, yval: int):
            thispoint.xval = xval
            thispoint.yval = yval

        self.Point = type('Point', (), {"__init__": point_init})

    def report_posn(self, event) -> None:
        """Display cursor position in lower right of canvas."""
        self.delete('text1')
        self.create_text(self.width - 24,
                         self.height - 10,
                         fill='blue',
                         text=str(event.x) + ',' + str(event.y),
                         tags='text1')

    def clear_posn(self, event) -> None:
        """Remove displayed cursor position from the canvas."""
        self.delete('text1')

    def report_color(self, textstr) -> None:
        """Display cursor position in lower right of canvas."""
        self.delete('text2')
        self.create_text(24,
                         self.height - 10,
                         fill=textstr,
                         text=textstr,
                         tags='text2')

    def set_start(self, event) -> None:
        """Handler for L-mouse click in freehand mode: save initial cursor
        position (firstx,y) and next position clicked after closing a figure in
        line mode (startx,y). Also used in line mode to reset the start posn.
        """
        if self.firstx == 0 and self.firsty == 0:
            self.firstx, self.firsty = event.x, event.y
            self.previousx, self.previousy = event.x, event.y
        else:
            self.previousx, self.previousy = self.startx, self.starty

        self.startx, self.starty = event.x, event.y

        if self.mode == 'lines':
            self.points.append(self.Point(event.x, event.y))
            # print(f'point added: {self.points[-1].xval},{self.points[-1].yval}')

    def draw_line(self, event) -> None:
        """Handler for L-mouse click in line mode. If past the starting position,
        draw a line from last posn to current posn.
        """
        if self.firstx == 0 and self.firsty == 0:
            self.set_start(event)
            return

        self.line_count += 1
        # line_number = self.line_count + 1#len(self.points)
        tagname = 'line' + str(self.line_count)
        self.create_line(self.startx, self.starty,
                         event.x, event.y,
                         fill=self.linecolor,
                         width=self.linewidth,
                         tags=tagname)

        self.linetags.append(tagname)
        self.set_start(event)

    def double_click(self, event) -> None:
        """Handler for L mouse double-click, in line mode. First, the single-click
        handler draws a line from the current position to the start posn. Then,
        this handler draws a line from the current to the previous position.
        """
        # print(f'    connecting from {event.x},{event.y} to {self.firstx},{self.firsty}')
        self.line_count += 1
        # line_number = self.line_count + 1#len(self.points)
        tagname = 'line' + str(self.line_count)
        self.create_line(event.x, event.y,
                         self.firstx, self.firsty,
                         fill=self.linecolor,
                         width=self.linewidth,
                         tags=tagname)
        self.linetags.append(tagname)
        print(f'linetags: {self.linetags}')

        # try (don't think this is necessary)
        # self.startx, self.starty = self.previousx, self.previousy

        self.firstx, self.firsty = 0, 0

        # the current shape is closed, forget its points and lines
        self.points = []
        self.linetags = []

    def undo_line(self, event) -> None:
        """Handler for R-mouse click. In line mode, remove last line and make
        previous cursor position the current position for connecting new lines.
        """
        if (self.firstx, self.firsty) == (0, 0):
            return

        if len(self.linetags) > 0:
            # print(f'linetags: {self.linetags}')
            self.delete(self.linetags[-1])
            self.linetags.pop()
        if len(self.points) > 0:
            # print(f'points: {self.points}')
            self.points.pop()
            if len(self.points) >= 1:
                self.startx, self.starty = self.points[-1].xval, self.points[-1].yval

    def draw_path(self, event) -> None:
        """Draw a path following the cursor.

        TODO: use modifier key to constrain horizontal / vertical
        """
        x_threshold = 10
        y_threshold = 10

        # both thresholds: simulate jagged lines in both directions
        # if (abs(event.x - self.startx) >= x_threshold and abs(event.y - self.starty) >= y_threshold):

        # y threshold: simulate jagged horizontal lines
        # if abs(event.y - self.starty) >= y_threshold:
        #     self.create_line(self.startx, self.starty, event.x, event.y, fill=self.linecolor, width=self.linewidth)
        #     self.set_start(event)

        # x threshold: simulate jagged vertical lines
        # if abs(event.x - self.startx) >= x_threshold:
        #     self.create_line(self.startx, self.starty, event.x, event.y, fill=self.linecolor, width=self.linewidth)
        #     self.set_start(event)

        # use y threshold value to force horizontal line if path is approximately horizontal
        # yvar = event.y - self.starty
        # if yvar <= y_threshold:
        #     self.create_line(self.startx, self.starty, event.x, event.y - yvar, fill=self.linecolor, width=self.linewidth)

        # use x threshold value to force vertical line if path is approximately vertical
        # xvar = event.x - self.startx
        # if xvar <= x_threshold:
        #     self.create_line(self.startx, self.starty, event.x - xvar, event.y, fill=self.linecolor, width=self.linewidth)

        # print(f'{event.x}, {event.y}')

        # no x or y change threshold
        self.create_line(self.startx, self.starty, event.x, event.y, fill=self.linecolor, width=self.linewidth)
        self.report_posn(event)
        self.set_start(event)

    def set_shape(self, event):
        # ? not needed for functionality, but better practice to include
        # global center_posn

        set_center(event)
        # print(f"center posn: {center_posn['x']}, {center_posn['y']}")
        xwidth, ywidth = 20.0, 20.0
        self.set_start(event)

        start_posn = self.startx - xwidth, self.starty - ywidth
        end_posn = self.startx + xwidth, self.starty + ywidth
        id1 = self.create_oval(*start_posn,
                               *end_posn,
                               outline='black',
                               width=2.0,
                               tags='circle1')

        print(f'start, previous: {self.startx}, {self.starty} -- {self.previousx}, {self.previousy}')
        # shape_var.set(value=shape_name.winfo_name())
        # print(f'shape selected: {shape_var.get()}')
        # print(f'shape selected: {shape_var.get()}')

        # get attributes
        # --------------
        # outline = self.itemcget(id1, 'outline')
        # print(f'outline is: {outline}')

        # c = self.find('withtag', 'circle1')
        # OR:
        # self.find_withtag('circle1')


    def drag_shape(self, event):
        dx = 0
        dy = 0

        if event.x > self.previousx: dx = 4
        if event.x < self.previousx: dx = -4
        if event.y > self.previousy: dy = 4
        if event.y < self.previousy: dy = -4

        self.previousx = event.x
        self.previousy = event.y

        self.move('current', dx, dy)


    def nudge_shape(self, event):
        print(f'in nudge_shape, ev: {event}')
        print(self.startx)
        # dx = 1
        # dy = 1

        # self.move('current', dx, dy)


    def expand_shape(self, event):
        # global center_posn
        self.scale('circle1', center_posn['x'], center_posn['y'], 1.01, 1.01)


    def contract_shape(self, event):
        self.scale('circle1', center_posn['x'], center_posn['y'], 0.99, 0.99)


# END Class Sketchpad ==========

file_path = ''

def set_color(event):
    """Set drawing color for both canvases."""
    color_choice = colorbar.gettags('current')
    print(f'color: {color_choice}')
    # sketch.linecolor = color_choice[0]
    sketch.linecolor = color_choice[0]

    # sketch.report_color(color_choice[0])
    sketch.report_color(color_choice[0])


def set_linewidth(var):
    """Set line width for canvas 2 (lines)."""
    sketch.linewidth = var.get()


def open_picture():
    global file_path

    file_path = filedialog.askopenfilename(title="Select Image File",
                                           initialdir='../image_display_RF/images',
                                           filetypes=[("PNG files",'*.png'),
                                                      ("JPEG file",'*.jpeg')])

    add_image(sketch, file_path)


def add_image(canv, fpath):
    global im_tk
    im = Image.open(fpath)
    imsize = cnv.init_image_size(im, viewport1)
    # heights.append(imsize['h'])
    # widths.append(imsize['w'])
    im_resize = im.resize((imsize['w'], imsize['h']))
    im_tk = ImageTk.PhotoImage(im_resize)
    # myPhotoImages.append(im_tk)
    # print(f'im w,h: {im.width}, {im.height}')
    # print(f'imsize w,h: {imsize["w"]}, {imsize["h"]}')
    # print()

    placement = cnv.get_1_posn(viewport1, imsize['w'], imsize['h'],
                               ('center', 'center'))
    # print(placement)
    # print(f'placement x,y: {placement.x}, {placement.y}')

    imid = canv.create_image(placement.x, placement.y,
                             anchor=tk.NW,
                             image=im_tk,
                             tag = 'image1')
    # canv.update()


def set_center(ev):
    center_posn['x'], center_posn['y'] = ev.x, ev.y
    print(f'in set_center: {center_posn["x"]}, {center_posn["y"]}')


root = tk.Tk()

sketch = Sketchpad(root, width=640, height=640, background='#ccc', mode='shapes')
# print(f'widgetName, _name: {sketch.widgetName}, {sketch._name}')

num_colors = 8  # not used yet
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'magenta', 'black']
xs = list(range(0, 320, 40))
y1 = 0
y2 = 42
colorbar = tk.Canvas(root, width=320, height=40)
for n, x in enumerate(xs):
    colorbar.create_rectangle(x, y1, x + 40, y2, fill=colors[n], tags=colors[n])  # + str(n))

colorbar.bind('<1>', set_color)

#   tk Frames:
#       - For a visible border, use 'relief' and 'border' attributes
#       - can use 'highlightthickness' and 'highlightbackground' attributes
#   ttk Frames:
#       - For a visible border, use 'relief' and 'padding' attributes
#       - 'padding' is internal to the Frame

linewidths = [str(i) for i in list(range(1, 11))]

viewport1 = {'w': 640, 'h': 640, 'gutter': 10}

# controls for canvas interaction ----------
controls = ttk.Frame(root, padding=2, relief='groove')

status = ttk.Label(controls, text='mode:')
status.pack(side='left')

status_value = ttk.Label(controls, foreground='blue', text=sketch.mode)
status_value.pack(side='left')

cursor_posn = tk.Text(background='#ff0')

lw = ttk.Label(controls, text='line width:')

line_w_var = tk.IntVar(value=1)
adj_linewidth = ttk.Spinbox(controls,
                            width=3,
                            from_=1,
                            to=10,
                            values=linewidths,
                            wrap=True,
                            foreground='blue',
                            textvariable=line_w_var,
                            command=lambda var=line_w_var: set_linewidth(var))

adj_linewidth.pack(side='right', pady=5)
lw.pack(side='right', padx=5)

# shape controls
# --------------
shape_value = 'default'
shape_var = tk.StringVar(value=shape_value)
center_posn = {'x': 0, 'y': 0}

open_button = tk.Button(root, text="Open Image", command=open_picture)

circle = ttk.Button(root, text='circle', name='circle', cursor='arrow')#, command=lambda w=circle: set_shape(w))
# circle.bind('<Button-1>', lambda ev, cp=center_posn: set_center(ev, cp))
# print(circle.winfo_name())

# ---------- END controls

quit_fr = ttk.Frame(root)
btnq = ttk.Button(quit_fr,
                  text="Quit",
                  command=root.quit,
                  style="MyButton1.TButton")

sketch.grid(column=0, row=3)
controls.grid(column=0, row=4, sticky='ew')
colorbar.grid(column=0, row=5, pady=10)
open_button.grid(column=0, row=6, pady=10)
circle.grid(column=0, row=7)

# btnq.grid(column=0,           row=6, ipady=10)
btnq.pack()
quit_fr.grid(column=0, row=8, pady=10)

# sketch.update()
# print(f'size of sketch: {sketch.winfo_width()}, {sketch.winfo_height()}')

# colorbar.update()
# print(f'size of colorbar: {colorbar.winfo_width()}')

if __name__ == '__main__':
    root.mainloop()
