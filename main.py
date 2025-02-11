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
01-21-2025  Remove commented-out code. Add ShapeCanvas attribute: shape_centers
            for correctly dragging and resizing any selected shape.
01-22-2025  Update function docstrings.
01-25-2025  Switch to Google-style class docstrings.
            Update many method docstrings with more standardized text.
01-31-2025  Add function toggle_selection to manage the selected shape object.
            Remove attribute linewidth from base class MyCanvas.
02-02-2025  Refine shape selection process.
02-04-2025  Debug reporting the shape center coordinates when dragging.
02-08-2025  Add 'constrain' parameter to drag_shape() to drag vertically
            or horizontally. Replace expand and contract functions with a
            single fxn, resize_shape().
02-11-2025  Update class headers. Update some function headers.
            Make file_path a local var. Remove old commented-code. Add frame
            for shapecanvas controls. Deactivate set_center().
"""
# TODO: add Frame for each canvas and its controls, to manage spacing
# TODO: ? option to constrain drawing lines to horizontal / vertical

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader

cnv = SourceFileLoader("cnv", "../image_display_RF/canvas_ui.py").load_module()


class MyCanvas(tk.Canvas):
    """
    MyCanvas : Defines a tk Canvas with some default attributes.

    The canvas reports the current cursor location, and keeps track of L-mouse
    clicked locations.

    Extends: tk.Canvas

    Attributes:
        firstx (int): x location of initial L-click
        firsty (int): y location of initial L-click

        startx (int): x location of L-click
        starty (int): y location of L-click

        previousx (int): x location of prevoius L-click
        previousy (int): y location of prevoius L-click

        points (list of int): list of x,y locations

    Methods:
        report_cursor_posn: display x,y cursor location as text
        clear_cursor_posn: delete cursor location text
        set_start: upon L-mouse click, store x,y cursor location
    """
    def __init__(self, parent,
                 # mode='',
                 width=320,
                 height=320,
                 background='#ffa',
                 ):
        """
        Creates an instance of the MyCanvas object.

        Args:
            width (int): Width of the canvas in pixels
            height (int): Height of the canvas in pixels
            background (str): Canvas background color
        """
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

        self.bind("<Motion>", self.report_cursor_posn)
        self.bind("<Leave>", self.clear_cursor_posn)

        def point_init(thispoint, xval: int, yval: int):
            thispoint.xval = xval
            thispoint.yval = yval
        self.Point = type('Point', (), {"__init__": point_init})


    def report_cursor_posn(self, event) -> None:
        """Display x,y cursor position in lower right of canvas."""
        self.delete('text1')
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()

        # print(f'w,h: {self.width}, {self.height}, ---- {self.winfo_width()}, {self.winfo_height()}')
        self.create_text(width - 28,
                         height - 10,
                         fill='blue',
                         text=str(event.x) + ',' + str(event.y),
                         tags='text1')


    def clear_cursor_posn(self, event) -> None:
        """Remove displayed cursor position from the canvas."""
        self.delete('text1')


    def set_start(self, event) -> None:
        """Handler for L-mouse click.

        Sets the values of class atrributes for first, previous and start
        cursor locations,
        where:
        - first is used at the beginning of an interactive session.
        - start is the last-clicked location in a mouse action.
        - previous is the next-to-last location clicked.
        """
        if self.firstx == 0 and self.firsty == 0:
            self.firstx, self.firsty = event.x, event.y
            self.previousx, self.previousy = event.x, event.y
        else:
            self.previousx, self.previousy = self.startx, self.starty

        self.startx, self.starty = event.x, event.y

        # if self.mode == 'lines':
        #     # print(f'Point is a {type(self.Point)}')
        #     self.points.append(self.Point(event.x, event.y))
        self.points.append(self.Point(event.x, event.y))

# END Class MyCanvas ==========



class DrawCanvas(MyCanvas):
    """
    DrawCanvas : a tk Canvas for interactive drawing.

    The user can either draw freehand by L-dragging the mouse, or L-click
    successive points to create connected lines, and R-click to successively
    remove existing lines.

    Extends: MyCanvas

    Attributes:
        linecolor (str): color of line created on the canvas
        line_count (int): number of lines created
        linetags (list of str): list of tags for each line object

    Methods:
        draw_line:
        double_click:
        undo_line:
        draw_path:
    """
    def __init__(self, parent,
                 mode='lines',
                 # linewidth=1,
                 **kwargs
                 ):
        """
        Creates an instance of the DrawCanvas object.

        Args:
            mode (str): Type of interaction with canvas, e.g. drawing lines
            linewidth (int): Width of line for creating lines and shapes
            width (int): Width of the canvas in pixels
            height (int): Height of the canvas in pixels
            background (str): Canvas background color
        """
        self.mode = mode
        # self.linewidth = linewidth
        self.linewidth = kwargs.get('linewidth')
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        self.background = kwargs.get('background')

        super().__init__(parent, width=self.width, height=self.height, background=self.background)

        self.linecolor = 'black'
        self.line_count = 0
        self.linetags = []

        match self.mode:
            case 'freehand':
                print('    binding freehand...')
                self.bind('<Button-1>', self.set_start)
                self.bind('<Button1-Motion>', self.draw_line)
            case 'lines':
                print('    binding lines...')
                self.bind('<Button-1>', self.draw_line)
                self.bind('<Double-1>', self.double_click)
                self.bind('<Button-3>', self.undo_line)


    def draw_line(self, event) -> None:
        """Handler for L-mouse click when drawing lines.

        If past starting position, draw a line from previous to current posn.
        """
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
        """Handler for L mouse double-click, when drawing lines.

        First, the single-click handler draws a line from the current position
        to the start posn. Then, this handler draws a line from the current to
        the previous position.
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

        # try (don't think this is necessary)
        # self.startx, self.starty = self.previousx, self.previousy

        self.firstx, self.firsty = 0, 0

        # the current shape is closed, forget its points and lines
        self.points = []
        self.linetags = []


    def undo_line(self, event) -> None:
        """Handler for R-mouse click, when drawing lines.

        Remove last line and make previous cursor position the current position
        for connecting new lines.
        """
        if (self.firstx, self.firsty) == (0, 0):
            return

        if len(self.linetags) > 0:
            self.delete(self.linetags[-1])
            self.linetags.pop()
        if len(self.points) > 0:
            self.points.pop()
            if len(self.points) >= 1:
                self.startx, self.starty = self.points[-1].xval, self.points[-1].yval


    # NOT USED
    # --------
    def draw_path(self, event) -> None:
        """Draw a path following the cursor, when drawing lines."""
        print(f'canv width: {self.winfo_width()}')
        # x_threshold = 10
        # y_threshold = 10

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
        self.report_cursor_posn(event)
        self.set_start(event)

        # get attributes
        # --------------
        # outline = self.itemcget(id1, 'outline')
        # print(f'outline is: {outline}')

        # c = self.find('withtag', 'oval')
        # OR:
        # self.find_withtag('oval')

# END Class DrawCanvas ==========



class ShapeCanvas(MyCanvas):
    """
    ShapeCanvas : a tk Canvas for creating shapes.

    The user can select an image to display. Shapes (oval, rectangle, etc.) can
    be added to annotate the image, and these can be resized or moved.

    Extends: MyCanvas

    Attributes:
        linecolor (str): color of line created on the canvas
        shapetags (list of str): list of the tags for each shape object
        shape_centers (list of tuple): list of x,y locations for the center of each shape
        next_shape (str): name of the next shape to be added
        selected (int): id of the current shape object

    Methods:
        create_shape: define and create a new shape object
        set_shape: setup for create_shape, manage shape attributes
        drag_shape: interactively move shape with the mouse
        nudge_shape: move shape 1 pixel with arrow key
        resize_shape: interactively change shape size
        toggle_selection: call function to set the 'current' shape object
        select_shape: make the shape nearest the cursor the current
        unselect_shape: reset current to the last-created shape
        report_center: display current shape's center x,y
    """
    def __init__(self, parent,
                 # linewidth=1,
                 **kwargs
                 ):
        # self.__dict__.update(kwargs)
        """
        Creates an instance of the ShapeCanvas object.

        Args:
            linewidth (int): Width of line for creating lines and shapes
            width (int): Width of the canvas in pixels
            height (int): Height of the canvas in pixels
            background (str): Canvas background color
        """

        self.linewidth = kwargs.get('linewidth')
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        self.background = kwargs.get('background')
        self.motionx = 0
        self.motiony = 0

        # if an expected argument is not passed:
        # self.test = kwargs.get('test')
        # print(f'test: {self.test}')      # = None

        super().__init__(parent, width=self.width, height=self.height, background=self.background)

        self.linecolor = 'black'
        self.shapetags = []
        self.shape_centers = []
        self.shape_linecolors = []
        self.next_shape = 'oval'
        self.selected = None

        self.bind('<Button-1>', self.set_shape)
        self.bind('<Shift-Motion>', self.drag_shape)
        self.bind('<Alt-Motion>', lambda ev, c=True: self.drag_shape(ev, c))
        self.bind('<Control-Motion>', self.resize_shape)
        # self.bind('<Alt-Motion>', self.contract_shape)

        self.master.bind('<Shift-Up>', lambda ev, h=0, v=-1: self.nudge_shape(ev, h, v))
        self.master.bind('<Shift-Down>', lambda ev, h=0, v=1: self.nudge_shape(ev, h, v))
        self.master.bind('<Shift-Left>', lambda ev, h=-1, v=0: self.nudge_shape(ev, h, v))
        self.master.bind('<Shift-Right>', lambda ev, h=1, v=0: self.nudge_shape(ev, h, v))
        self.master.bind('<Button-3>', lambda ev: self.toggle_selection(ev))


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
        """Handler for L-mouse button when drawing shapes.

        Sets up parameters, calls create_shape(), and manages
        the list of existing shape objects, and some of their attributes.
        """
        # set_center(event)

        # TODO: these values should be user preferences, not hard-coded here.
        xwidth, ywidth = 20.0, 20.0

        self.set_start(event)

        start_posn = self.startx - xwidth, self.starty - ywidth
        end_posn = self.startx + xwidth, self.starty + ywidth
        this_tag = self.next_shape + str(len(self.shapetags) + 1)
        # print(f'tag created: {this_tag}')
        id1 = self.create_shape(start_posn,
                                end_posn,
                                shape=self.next_shape,
                                linecolor=self.linecolor,
                                width=self.linewidth,
                                tag=this_tag)
        if id1 is not None:
            self.shapetags.append(this_tag)
            this_center = {'x':self.startx, 'y':self.starty}
            # print(f'set center: {this_center}')
            self.shape_centers.append(this_center)
            self.shape_linecolors.append(self.linecolor)
            self.report_center(this_center, self.linecolor)
            self.selected = id1

            self.motionx, self.motiony = self.startx, self.starty


    def drag_shape(self, event, constrain=False):
        """Handler for L-mouse drag when drawing shapes.

        Interactively moves a shape object on the canvas."""
        dx = 0
        dy = 0
        shift = 1
        self.report_cursor_posn(event)

        theshape = self.selected

        this_tag = self.gettags(theshape)[1]
        this_index = self.shapetags.index(this_tag)
        center_posn = self.shape_centers[this_index]

        if constrain:
            x_difference = abs(event.x - self.previousx)
            y_difference = abs(event.y - self.previousy)

            if x_difference > y_difference:
                if event.x > self.previousx: dx = shift

                if event.x < self.previousx: dx = -shift
            else:
                if event.y > self.previousy: dy = shift
                if event.y < self.previousy: dy = -shift
        else:
            if event.x > self.previousx: dx = shift
            if event.x < self.previousx: dx = -shift
            if event.y > self.previousy: dy = shift
            if event.y < self.previousy: dy = -shift

        self.previousx = event.x
        self.previousy = event.y

        # print(f'dx, dy: {dx}, {dy}')
        self.move(theshape, dx, dy)

        coords_float = self.coords(theshape)
        coords = [int(n) for n in coords_float]
        center_posn['x'] = coords[0] + 20
        center_posn['y'] = coords[1] + 20

        t = self.gettags(self.selected)[1]

        outline = self.itemcget(self.selected, 'outline')
        self.report_center(center_posn, outline)


    def nudge_shape(self, event, dx, dy):
        """Move the selected shape object by one pixel.

        Shift key activates this operation, and the direction of movement is
        determined by which arrow key is pressed.
        """
        mydrawcanvas.focus_set()
        theshape = self.selected
        self.move(theshape, dx, dy)

        t = self.gettags(theshape)[1]
        whichone = self.shapetags.index(t)
        c = self.shape_centers[whichone]
        c['x'] += dx
        c['y'] += dy

        outline = self.itemcget(self.selected, 'outline')
        self.report_center(c, outline)


    # def expand_shape(self, event):
    #     """Handler for L-mouse button + CONTROL key to modify a shape object.
    #
    #     Interactively enlarges the selected shape.
    #     """
    #     if self.selected is None: return
    #     theshape = self.selected
    #     this_tag = self.gettags(theshape)[1]
    #     this_index = self.shapetags.index(this_tag)
    #     center_posn = self.shape_centers[this_index]
    #
    #     self.scale(theshape, center_posn['x'], center_posn['y'], 1.01, 1.01)


    def resize_shape(self, event):
        """Handler for L-mouse button + CONTROL key to modify a shape object.

        Interactively enlarges the selected shape.
        """
        # print(f'x,y: {event.x}, {event.y}')
        if self.selected is None: return
        theshape = self.selected
        this_tag = self.gettags(theshape)[1]
        this_index = self.shapetags.index(this_tag)
        center_posn = self.shape_centers[this_index]

        if event.y < self.motiony:
            self.scale(theshape, center_posn['x'], center_posn['y'], 1.01, 1.01)

        if event.y > self.motiony:
            self.scale(theshape, center_posn['x'], center_posn['y'], 0.99, 0.99)

        self.motionx, self.motiony = event.x, event.y


    # def contract_shape(self, event):
    #     """Handler for L-mouse button + ALT key to modify a shape object.
    #
    #     Interactively reduces the size of the selected shape.
    #     """
    #     if self.selected is None: return
    #     theshape = self.selected
    #     this_tag = self.gettags(theshape)[1]
    #     this_index = self.shapetags.index(this_tag)
    #     center_posn = self.shape_centers[this_index]
    #
    #     self.scale(theshape, center_posn['x'], center_posn['y'], 0.99, 0.99)


    def toggle_selection(self, event):
        """Assign one shape to be the currently selected shape."""
        # If Shift key, un-select everything and return
        if event.state == 1:
            self.unselect_shape(event)
        else:
            self.select_shape(event)


    def unselect_shape(self, event):
        """Handler for Shift + R-mouse click to unselect a shape.

        The selected shape reverts to the last shape created.
        """
        for n, item in enumerate(self.shapetags):
            self.itemconfigure(item, fill='')

        # set selected item to be the last created
        lastid = self.find_withtag(self.shapetags[-1])[0]
        self.itemconfigure(lastid, fill='#ffa')
        self.after(500, lambda: self.itemconfigure(lastid, fill=''))
        self.selected = lastid


    def select_shape(self, event):
        """Handler for R-mouse click to select the shape nearest the cursor.

        Makes the shape nearest the cursor, the 'selected' shape. A class
        attribute keeps track of the currently selected shape, by its id. The
        shape is highlighted with a color fill.
        """
        # remove lighlight from all shapes
        for n, item in enumerate(self.shapetags):
            self.itemconfigure(item, fill='')

        found = self.find_closest(event.x, event.y, halo=25)
        if len(found) > 0:
            self.selected = found[0]

            # highlight the seleced shape
            self.itemconfigure(self.selected, fill='#ffa')



            t = self.gettags(self.selected)[1]
            # print(f'tag selected: {t}')

            whichone = self.shapetags.index(t)
            # print(f'whichone: {whichone}')

            center = self.shape_centers[whichone]
            # print(f'center: {center}')

            outline = self.itemcget(self.selected, 'outline')
            # print(f'outline: {outline}')


            self.report_center(center, outline)
        else:
            print('no object found')


    def report_center(self, center, color) -> None:
        self.delete('center_text')
        textstr = f"center:  {center['x']}, {center['y']}"

        self.create_text(10,
                         12,
                         fill=color,
                         text=textstr,
                         anchor='w',
                         tags='center_text')



# END Class ShapeCanvas ==========

# file_path = ''

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


def open_picture():
    """Manage user selection of an image file, for display in a canvas."""
    # global file_path

    file_path = filedialog.askopenfilename(title="Select Image File",
                                           initialdir='../image_display_RF/images',
                                           filetypes=[("PNG files",'*.png'),
                                                      ("JPEG file",'*.jpeg')])

    # add_image(mydrawcanvas, file_path)
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

# not needed?
# def set_center(ev):
#     center_posn['x'], center_posn['y'] = ev.x, ev.y


root = tk.Tk()

# image to be loaded; the object needs to be global
im_tk = None

mydrawcanvas = DrawCanvas(root,
                          mode='freehand',
                          width=640,
                          height=640,
                          background='#ccc'
                          )

myshapecanvas = ShapeCanvas(root,
                            width=400,
                            height=500,
                            background='cyan'
                            )
# no londer needed?
# myshapecanvas.bind('<Button-3>', lambda event: self.select_shape(event))

num_colors = 8  # not used yet

colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'magenta', 'black']
xs = list(range(0, 320, 40))
y1 = 0
y2 = 42
colorbar = tk.Canvas(root, width=320, height=40)
for n, x in enumerate(xs):
    colorbar.create_rectangle(x, y1, x + 40, y2, fill=colors[n], tags=colors[n])  # + str(n))

# colorbar.bind('<1>', set_color)
colorbar.bind('<1>', lambda ev, canv=(mydrawcanvas, myshapecanvas): set_color(ev, canv))

linewidths = [str(i) for i in list(range(1, 11))]

# drawcanvas:
# viewport1 = {'w': 640, 'h': 640, 'gutter': 10}
# shapecanvas:
viewport1 = {'w': 400, 'h': 500, 'gutter': 10}


# draw canvas controls ----------
controls_1 = ttk.Frame(root, padding=2, relief='groove')

status = ttk.Label(controls_1, text='mode:')
status.pack(side='left')

status_value = ttk.Label(controls_1, foreground='blue', text=mydrawcanvas.mode)
status_value.pack(side='left')

cursor_posn = tk.Text(background='#ff0')

lw = ttk.Label(controls_1, text='line width:')

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
lw.pack(side='right', padx=5)
# ---------- END draw canvas controls


# shape canvas controls --------------
# needed?
# shape_value = 'default'
# shape_var = tk.StringVar(value=shape_value)

center_posn = {'x': 0, 'y': 0}

controls_2 = ttk.Frame(root, padding=2, relief='groove')

open_button = tk.Button(controls_2, text="Open Image", command=open_picture)

circle = ttk.Button(controls_2, text='circle', name='circle', cursor='arrow')#, command=lambda w=circle: set_shape(w))
# ---------- END shape canvas controls


quit_fr = ttk.Frame(root)
btnq = ttk.Button(quit_fr,
                  text="Quit",
                  command=root.quit,
                  style="MyButton1.TButton")

# mydrawcanvas.grid(column=0, row=3)
# controls_1.grid(column=0, row=4, sticky='ew')
# colorbar.grid(column=0, row=5, pady=10)
# open_button.grid(column=0, row=6, pady=10)
# circle.grid(column=0, row=7)
#
# myshapecanvas.grid(column=1, row=3)
# controls_2.grid(column=1, row=4)

mydrawcanvas.grid(column=0, row=1)
controls_1.grid(column=0, row=2, sticky='ew')
colorbar.grid(column=0, row=3, pady=10)

myshapecanvas.grid(column=1, row=1)
open_button.grid(column=0, row=1, pady=10)
circle.grid(column=0, row=2)
controls_2.grid(column=1, row=2, sticky='ew')

btnq.pack()
# quit_fr.grid(column=0, row=8, pady=10)
quit_fr.grid(column=0, row=4, pady=10)

# mydrawcanvas.update()
# print(f'size of mydrawcanvas: {mydrawcanvas.winfo_width()}, {mydrawcanvas.winfo_height()}')

# myshapecanvas.update()
# print(f'size of myshapecanvas: {myshapecanvas.winfo_width()}, {myshapecanvas.winfo_height()}')

# colorbar.update()
# print(f'size of colorbar: {colorbar.winfo_width()}')


# practice retrieving class info

# print('-------------------------------------------------------')
# print(f'{mydrawcanvas.__doc__}')
# print('-------------------------------------------------------')
# print()

# # alternative to print __doc__
# import inspect
# print(f'{inspect.getdoc(MyCanvas)}')
# print('-------------------------------------------------------------------')
# print()
# # exhaustive:
# print(help(MyCanvas))


if __name__ == '__main__':
    root.mainloop()
