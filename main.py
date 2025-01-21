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
            Commit again.
01-12-2025  Debug drag function. Add function to nudge the shape 1 pixel.
            Read line color and line thickness. Move creation of shape object
            into its own funciton.
01-16-2025  Create ShapeCanvas as a child class of Sketchpad. drag_shape() now
            updates center location of the object. Selecting a shape now
            highlights only that shape.
01-17-2025  Rename Sketchpad class to DrawCanvas.
01-18-2025  Define a base class MyCanvas, of which DrawCanvas and ShapeCanvas
            are children. Streamline __init__ functions and variables, but
            keep old and superfluous code, commented-out, to document what
            was done.
01-21-2025  Remove commented-out code. Add ShapeCanvas attribute shape_centers
            for correctly dragging and resizing any selected shape.
"""
# TODO: 2) in drag_shape(), use modifier key to constrain horizontal / vertical

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader

cnv = SourceFileLoader("cnv", "../image_display_RF/canvas_ui.py").load_module()


class MyCanvas(tk.Canvas):
    def __init__(self, parent,
                 mode='',
                 linewidth=1,
                 width=320,
                 height=320,
                 background='#ffa',
                 ):
        self.mode = mode
        self.linewidth = linewidth
        self.width = width
        self.height = height
        self.background = background

        super().__init__(parent, width=self.width, height=self.height, background=self.background)

        self.firstx = 0
        self.firsty = 0
        self.startx = 0
        self.starty = 0
        self.previousx = 0
        self.previousy = 0
        self.points = []

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


    def set_start(self, event) -> None:
        """Handler for L-mouse click. Depending on the mode this function may:
        - save initial cursor position (firstx,y) and/or:
        - save next position clicked after closing a figure (startx,y)
        - reset the start posn.
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


class DrawCanvas(MyCanvas):
    """
    DrawCanvas : Defines a Canvas for interactive drawing.

    Extends: tk.Canvas

    Attributes
    ----------

    Methods
    -------
    method_1:
        text
    """

    def __init__(self, parent,
                 mode='lines',
                 linewidth=1,
                 **kwargs
                 ):
        # self.__dict__.update(kwargs)
        """
        Initializess a DrawCanvas object.

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

        self.mode = mode
        self.linewidth = linewidth
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        self.background = kwargs.get('background')

        super().__init__(parent, mode='lines', width=self.width, height=self.height, background=self.background)
        # super().__init__(parent)

        # print(f'in DrawCanvas, mode is {self.mode}')
        # print(f'in DrawCanvas, linewidth is {self.linewidth}')
        self.linecolor = 'black'
        self.line_count = 0
        self.linetags = []

        match self.mode:
            case 'freehand':
                self.bind('<Button-1>', self.set_start)
            case 'lines':
                print('    binding...')
                self.bind('<Button-1>', self.draw_line)
                self.bind('<Double-1>', self.double_click)
                self.bind('<Button-3>', self.undo_line)
            # case 'shapes':
            #     self.bind('<Button-1>', self.set_shape)
            #     self.bind('<Shift-Motion>', self.drag_shape)
            #     self.bind('<Control-Motion>', self.expand_shape)
            #     self.bind('<Alt-Motion>', self.contract_shape)

                # use scrollwheel if available (also works for middle mouse button
                # plus trackbutton on ThinkPad):
                # self.bind('<Button-4>', self.expand_shape)
                # self.bind('<Button-5>', self.contract_shape)

                # self.master.bind('<Shift-Up>', lambda ev, h=0, v=-1: self.nudge_shape(ev, h, v))
                # self.master.bind('<Shift-Down>', lambda ev, h=0, v=1: self.nudge_shape(ev, h, v))
                # self.master.bind('<Shift-Left>', lambda ev, h=-1, v=0: self.nudge_shape(ev, h, v))
                # self.master.bind('<Shift-Right>', lambda ev, h=1, v=0: self.nudge_shape(ev, h, v))


    def draw_line(self, event) -> None:
        """Handler for L-mouse click when drawing lines. If past the starting

        position, draw a line from last posn to current posn.
        """
        # print('in draw_line...')
        if self.firstx == 0 and self.firsty == 0:
            self.set_start(event)
            return

        self.line_count += 1
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

    # def create_shape(self,
    #                  start,
    #                  end,
    #                  shape='oval',
    #                  linecolor='black',
    #                  width=1,
    #                  tag='oval'):
    #     id1 = None
    #
    #     match shape:
    #         case 'oval':
    #             taglist = ['oval', tag]
    #             id1 = self.create_oval(start,
    #                                    end,
    #                                    outline=linecolor,
    #                                    width=width,
    #                                    tags=taglist)
    #             # w = self.itemcget('width')
    #             # print(f'')
    #         case _:
    #             pass
    #
    #     return id1


    # def set_shape(self, event):
    #     set_center(event)
    #
    #     xwidth, ywidth = 20.0, 20.0
    #     self.set_start(event)
    #
    #     start_posn = self.startx - xwidth, self.starty - ywidth
    #     end_posn = self.startx + xwidth, self.starty + ywidth
    #     this_tag = self.next_shape + str(len(self.shapetags) + 1)
    #     id1 = self.create_shape(start_posn,
    #                             end_posn,
    #                             shape=self.next_shape,
    #                             linecolor=self.linecolor,
    #                             width=self.linewidth,
    #                             tag=this_tag)
    #     if id1 is not None:
    #         self.shapetags.append(this_tag)
    #         self.selected = id1

        # get attributes
        # --------------
        # outline = self.itemcget(id1, 'outline')
        # print(f'outline is: {outline}')

        # c = self.find('withtag', 'oval')
        # OR:
        # self.find_withtag('oval')


    # def drag_shape(self, event):
    #     dx = 0
    #     dy = 0
    #     shift = 1
    #     # theshape = self.shapetags[-1]
    #     theshape = self.selected
    #     print('in DrawCanvas drag_shape')
    #     if event.x > self.previousx: dx = shift
    #     if event.x < self.previousx: dx = -shift
    #     if event.y > self.previousy: dy = shift
    #     if event.y < self.previousy: dy = -shift
    #
    #     self.previousx = event.x
    #     self.previousy = event.y
    #
    #     center_posn['x'] += dx
    #     center_posn['y'] += dy
    #
    #     self.move(theshape, dx, dy)
    #
    #
    # def nudge_shape(self, event, dx, dy):
    #     # print(f'in nudge_shape, ev: {event}')
    #     canvas1.focus_set()
    #     theshape = self.shapetags[-1]
    #     self.move(theshape, dx, dy)
    #
    #
    # def expand_shape(self, event):
    #     # global center_posn
    #     # theshape = self.shapetags[-1]
    #     theshape = self.selected
    #     self.scale(theshape, center_posn['x'], center_posn['y'], 1.01, 1.01)
    #
    #
    # def contract_shape(self, event):
    #     # theshape = self.shapetags[-1]
    #     theshape = self.selected
    #     # print(f'contractint {theshape}')
    #
    #     self.scale(theshape, center_posn['x'], center_posn['y'], 0.99, 0.99)

# END Class DrawCanvas ==========

class ShapeCanvas(MyCanvas):
    def __init__(self, parent,
                 linewidth=1,
                 **kwargs
                 ):
        self.__dict__.update(kwargs)

        """
        Initializes a ShapeCanvas object.

        Parameters
        ----------
        width : Int
            Canvas width.
        height : Int
            Canvas height.

        Methods
        -------
        """

        self.linewidth = linewidth
        # self.width = kwargs.get('width')
        # self.height = kwargs.get('height')
        # self.background = kwargs.get('background')

        # if an expected argument is not passed:
        # self.test = kwargs.get('test')
        # print(f'test: {self.test}')      # = None

        super().__init__(parent, width=self.width, height=self.height, background=self.background)

        # print(f'in ShapeCanvas, mode is {self.mode}')

        self.linecolor = 'black'
        self.shapetags = []
        self.shape_centers = []
        self.next_shape = 'oval'
        self.selected = None

        self.bind('<Button-1>', self.set_shape)
        self.bind('<Shift-Motion>', self.drag_shape)
        self.bind('<Control-Motion>', self.expand_shape)
        self.bind('<Alt-Motion>', self.contract_shape)

        self.master.bind('<Shift-Up>', lambda ev, h=0, v=-1: self.nudge_shape(ev, h, v))
        self.master.bind('<Shift-Down>', lambda ev, h=0, v=1: self.nudge_shape(ev, h, v))
        self.master.bind('<Shift-Left>', lambda ev, h=-1, v=0: self.nudge_shape(ev, h, v))
        self.master.bind('<Shift-Right>', lambda ev, h=1, v=0: self.nudge_shape(ev, h, v))
        self.master.bind('<Button-3>', lambda ev: self.select_shape(ev))

    def create_shape(self,
                     start,
                     end,
                     shape='oval',
                     linecolor='black',
                     width=1,
                     tag='oval'):
        id1 = None

        match shape:
            case 'oval':
                taglist = ['oval', tag]
                id1 = self.create_oval(start,
                                       end,
                                       outline=linecolor,
                                       width=width,
                                       tags=taglist)
            case _:
                pass

        return id1


    def set_shape(self, event):
        set_center(event)

        xwidth, ywidth = 20.0, 20.0
        self.set_start(event)

        start_posn = self.startx - xwidth, self.starty - ywidth
        end_posn = self.startx + xwidth, self.starty + ywidth
        this_tag = self.next_shape + str(len(self.shapetags) + 1)
        id1 = self.create_shape(start_posn,
                                end_posn,
                                shape=self.next_shape,
                                linecolor=self.linecolor,
                                width=self.linewidth,
                                tag=this_tag)
        if id1 is not None:
            self.shapetags.append(this_tag)
            this_center = {'x':self.startx, 'y':self.starty}
            self.shape_centers.append(this_center)
            self.selected = id1

        # example of getting attributes
        # ------------------
        # outline = self.itemcget(id1, 'outline')
        # print(f'outline is: {outline}')

        # c = self.find('withtag', 'oval')
        # OR:
        # self.find_withtag('oval')


    def drag_shape(self, event):
        dx = 0
        dy = 0
        shift = 1
        # theshape = self.shapetags[-1]
        theshape = self.selected
        this_tag = self.gettags(theshape)[1]
        this_index = self.shapetags.index(this_tag)
        center_posn = self.shape_centers[this_index]

        if event.x > self.previousx: dx = shift
        if event.x < self.previousx: dx = -shift
        if event.y > self.previousy: dy = shift
        if event.y < self.previousy: dy = -shift

        self.previousx = event.x
        self.previousy = event.y

        center_posn['x'] += dx
        center_posn['y'] += dy
        # print(f"ending center: {center_posn['x']}, {center_posn['y']}")

        self.move(theshape, dx, dy)


    def nudge_shape(self, event, dx, dy):
        # print(f'in nudge_shape, ev: {event}')
        mydrawcanvas.focus_set()
        # theshape = self.shapetags[-1]
        theshape = self.selected
        self.move(theshape, dx, dy)


    def expand_shape(self, event):
        # global center_posn
        # theshape = self.shapetags[-1]
        theshape = self.selected
        this_tag = self.gettags(theshape)[1]
        this_index = self.shapetags.index(this_tag)
        center_posn = self.shape_centers[this_index]

        self.scale(theshape, center_posn['x'], center_posn['y'], 1.01, 1.01)


    def contract_shape(self, event):
        # theshape = self.shapetags[-1]
        theshape = self.selected
        this_tag = self.gettags(theshape)[1]
        this_index = self.shapetags.index(this_tag)
        center_posn = self.shape_centers[this_index]

        self.scale(theshape, center_posn['x'], center_posn['y'], 0.99, 0.99)


    def select_shape(self, event):
        """Make the shape near the cursor the 'selected' shape, and highlight it."""
        found = self.find_closest(event.x, event.y, halo=25)
        if len(found) > 0:
            self.selected = found[0]

            # remove highlight from all shapes
            # print(f'shapetags: {self.shapetags}')
            for n, item in enumerate(self.shapetags):
                self.itemconfigure(item, fill='orange')
            self.itemconfigure(self.selected, fill='#ffa')
        else:
            print('object not found')

# END Class ShapeCanvas ==========

file_path = ''

def set_color(event):
    """Set drawing color for canvas."""
    color_choice = colorbar.gettags('current')[0]
    mydrawcanvas.linecolor = color_choice
    myshapecanvas.linecolor = color_choice
    report_color(color_choice)


def report_color(textstr) -> None:
    """Display line color in lower left of canvas."""
    mydrawcanvas.delete('text2')
    mydrawcanvas.create_text(10,
                             mydrawcanvas.height - 10,
                             fill=textstr,
                             text=textstr,
                             anchor='w',
                             # justify='left',
                             tags='text2')


def set_linewidth(var):
    """Set line width for canvas.

    parameter: var = line width, from the IntVar in adj_linewidth.
    """
    mydrawcanvas.linewidth = var.get()


def open_picture():
    global file_path

    file_path = filedialog.askopenfilename(title="Select Image File",
                                           initialdir='../image_display_RF/images',
                                           filetypes=[("PNG files",'*.png'),
                                                      ("JPEG file",'*.jpeg')])

    add_image(mydrawcanvas, file_path)


def add_image(canv, fpath):
    global im_tk

    im = Image.open(fpath)
    imsize = cnv.init_image_size(im, viewport1)
    im_resize = im.resize((imsize['w'], imsize['h']))
    im_tk = ImageTk.PhotoImage(im_resize)

    placement = cnv.get_1_posn(viewport1, imsize['w'], imsize['h'],
                               ('center', 'center'))
    # print(placement)
    # print(f'placement x,y: {placement.x}, {placement.y}')

    imid = canv.create_image(placement.x, placement.y,
                             anchor=tk.NW,
                             image=im_tk,
                             tag = 'image1')

    # any reason to do this?
    # canv.update()


def set_center(ev):
    center_posn['x'], center_posn['y'] = ev.x, ev.y
    # print(f'in set_center: {center_posn["x"]}, {center_posn["y"]}')


root = tk.Tk()

# image to be loaded; the object needs to be global
im_tk = None

mydrawcanvas = DrawCanvas(root,
                          mode='lines',
                          linewidth=1,
                          width=640,
                          height=640,
                          background='#ccc'
                          )

myshapecanvas = ShapeCanvas(root,
                            # mode='shapes',
                            linewidth=1,
                            width=400,
                            height=500,
                            background='cyan'
                            )
# myshapecanvas.bind('<Button-3>', lambda event: self.select_shape(event))


num_colors = 8  # not used yet

colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'magenta', 'black']
xs = list(range(0, 320, 40))
y1 = 0
y2 = 42
colorbar = tk.Canvas(root, width=320, height=40)
for n, x in enumerate(xs):
    colorbar.create_rectangle(x, y1, x + 40, y2, fill=colors[n], tags=colors[n])  # + str(n))

colorbar.bind('<1>', set_color)

linewidths = [str(i) for i in list(range(1, 11))]

viewport1 = {'w': 640, 'h': 640, 'gutter': 10}

# controls for canvas interaction ----------
controls = ttk.Frame(root, padding=2, relief='groove')

status = ttk.Label(controls, text='mode:')
status.pack(side='left')

status_value = ttk.Label(controls, foreground='blue', text=mydrawcanvas.mode)
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
# ---------- END canvas interaction

# shape controls
# --------------
shape_value = 'default'
shape_var = tk.StringVar(value=shape_value)
center_posn = {'x': 0, 'y': 0}

open_button = tk.Button(root, text="Open Image", command=open_picture)

circle = ttk.Button(root, text='circle', name='circle', cursor='arrow')#, command=lambda w=circle: set_shape(w))
# ---------- END shape controls

quit_fr = ttk.Frame(root)
btnq = ttk.Button(quit_fr,
                  text="Quit",
                  command=root.quit,
                  style="MyButton1.TButton")

mydrawcanvas.grid(column=0, row=3)
myshapecanvas.grid(column=1, row=3)
controls.grid(column=0, row=4, sticky='ew')
colorbar.grid(column=0, row=5, pady=10)
open_button.grid(column=0, row=6, pady=10)
circle.grid(column=0, row=7)

btnq.pack()
quit_fr.grid(column=0, row=8, pady=10)

mydrawcanvas.update()
# print(f'size of mydrawcanvas: {mydrawcanvas.winfo_width()}, {mydrawcanvas.winfo_height()}')

myshapecanvas.update()
# print(f'size of myshapecanvas: {myshapecanvas.winfo_width()}, {myshapecanvas.winfo_height()}')

# colorbar.update()
# print(f'size of colorbar: {colorbar.winfo_width()}')

if __name__ == '__main__':
    root.mainloop()
