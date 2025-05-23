"""
module: tool_classes.py

purpose: provide custom tkinter (ttk) widget classes for a Frame with one or
         more child widgets.

comments:

author: Russell Folks

history:
-------
02-17-2025  creation
03-07-2025  Change docstring format.
"""
# TODO: fix instance attributes

from tkinter import ttk

class ToolFrame(ttk.Frame):
    """
    ToolFrame : Defines a Frame containing a row of widgets.

    Extends: ttk.Frame

    Attributes:
        sep (str): character to separate text
        label_name (str): text of the Label

    Methods:
        create_widgets: add widget children to the Frame
    """
    def __init__(self, parent,
                 cb_values=(20, 30, 40),
                 display_name='',
                 name='',
                 var=None,
                 callb=None,
                 posn=None,
                 stick='w'
                 ):
        """
        Inits a ToolFrame object.

        Arguments:
            cb_values (tuple): values passed through to a Combobox.
            var (tkinter.IntVar): variable for widget value
            callb (function): callback for the widget event
            posn (list): row and column for gridding child objects
            display_name (str): used to construct the Label text
            name (str): name attribute of the Combobox

        Methods:
            create_widgets: Creates and displays the widgets.
            props: Returns the parameter list for an instance of the class.
        """
        super().__init__(parent)

        self.cb_values = cb_values
        self.var = var
        # print(f'in class, var is {type(var)}')
        self.callb = callb
        self.posn = posn
        self.display_name = display_name
        self.name = name
        self.stick = stick

        self.sep = ': '
        self.label_name = self.display_name + self.sep

        self.create_widgets()

    def create_widgets(self):
        lab = ttk.Label(self,
                        text=self.label_name)

        # could add a postcommand attribute, which executes before the callb.
        cb = ttk.Spinbox(self,
                         width=3,
                         from_=1,
                         to=10,
                         values=self.cb_values,
                         wrap=True,
                         textvariable=self.var,
                         command=lambda n=self.display_name: self.callb(n)
        )
        cb.bind('<<ComboboxSelected>>', self.callb)

        lab.pack(side='left')
        cb.pack(side='left')

        self.grid(column=self.posn[0], row=self.posn[1], padx=5, pady=10, sticky=self.stick)
