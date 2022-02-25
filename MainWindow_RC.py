# !/usr/bin/env python3
# coding: utf-8
__author__ = "Shushanth Prabhu"
__email__ = "shushanth@gmail.com"
__version__ = "1.0"

from tkinter import Frame, messagebox, Label, Menu, SUNKEN
from tkinter import E, W, X, Y, BOTH, LEFT, BOTTOM, TclError
from tkinter import Toplevel, Entry, Button

from tkinter.filedialog import askopenfilename, asksaveasfile
from PIL import ImageTk, Image

from NetworkParser import foster_solver as fs
from NetworkParser import cauer_solver as cs

# TODO need to put OPTIONS window in a new Class
# TODO Foster Options Window Esc closes the whole app instead of just the window
# TODO Sanity check in Foster Options Window

# LOWER BOUND
default_foster_lower_bound = 0.00000001
# UPPER BOUND
default_foster_upper_bound = 1000000
# Tolerance of Cost Function ftol
default_foster_ftol = 0.00000001
# Tolerance of Independent Functions xtol
default_foster_xtol = 0.00000001
# CREATE DIAGONOSTIC
default_foster_diagnostic = False
default_cauer_diagnostic = False


class MainWindow(Frame):

    def __init__(self):
        Frame.__init__(self)
        self.pack(expand=Y, fill=BOTH)

        # DEFAULT VALUES
        self.foster_lower_bound = default_foster_lower_bound
        self.foster_upper_bound = default_foster_upper_bound
        self.foster_ftol = default_foster_ftol
        self.foster_xtol = default_foster_xtol
        self.foster_diagnostic = default_foster_diagnostic
        self.cauer_diagnostic = default_cauer_diagnostic

        # INITIALIZE
        self.menu = None
        self.status = None
        self.option1_field = None
        self.option2_field = None
        self.option3_field = None
        self.option4_field = None

        self.r_list = []
        self.c_list = []
        # ICON and TTTLE BAR
        self.master.title('RC 1D Network')
        self.master.iconbitmap('images//RC.ico')

        self.create_widgets()

        # DISABLE RESIZING
        self.winfo_toplevel().resizable(0, 0)
        # ESC closes the widget.
        # self.winfo_toplevel().bind('<Escape>', self.esc_exit_app)
        # self.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.exit_app)
        self.winfo_toplevel().bind('<Escape>', lambda x: self.master.destroy())

    @property
    def foster_default_value(self):
        """
        Property containing all default foster network values
        """
        return (
            self.foster_lower_bound, self.foster_upper_bound, self.foster_ftol, self.foster_xtol,
            self.foster_diagnostic,
            self.cauer_diagnostic)

    def create_widgets(self):
        """
        Function which creates all widgets to the main window
        :return: None
        """
        self.create_menu_panels()
        self.create_buttons()
        # STATUS BAR
        self.status_bar = Label(self, text='Tool to create 1D RC Network', borderwidth=1, font='Helv 10', anchor=W)
        self.status_bar.pack(side="left", fill=X)

    def create_buttons(self):
        """
        Add Button to the MainWindow
        :return: None
        """
        buttons_frame = Frame(self, height=100, width=400)
        buttons_frame.grid_propagate(0)
        buttons_frame.pack()
        buttons_frame.grid_rowconfigure(1, weight=1)
        buttons_frame.grid_rowconfigure(4, weight=1)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(4, weight=1)

        foster_button = Button(buttons_frame, text='Create Foster Network', command=self.btn_foster)
        cauer_button = Button(buttons_frame, text='Create Cauer Network', command=self.btn_cauer)
        foster_button.focus()

        cauer_button.bind("<Enter>",
                          lambda a: self.status_bar.configure(text="Import Zth curves to create a Cauer Network"))
        cauer_button.bind("<Leave>", lambda a: self.status_bar.configure(text=" "))

        foster_button.bind("<Enter>",
                           lambda a: self.status_bar.configure(text="Import Zth Curves to create a Foster Network"))
        foster_button.bind("<Leave>", lambda a: self.status_bar.configure(text=" "))

        cauer_button.grid(in_=buttons_frame, row=2, column=1, sticky=E)
        foster_button.grid(in_=buttons_frame, row=1, column=1, sticky=E)

    def btn_foster(self):
        try:
            filepath = askopenfilename(filetypes=[("Text Files", "*.csv"), ("All Files", "*.*")])
            rc_network = fs.get_foster_network(filepath, self.foster_default_value)

            self.r_list, self.c_list = fs.sort_rc_list(rc_network)
            print(self.r_list, "\n", self.c_list)
            self.show_network(self.r_list, self.c_list)

        except fs.FC_Error_list.FosterCauer_Error as error:
            error = str(error)
            messagebox.showerror(title="Error", message=error)

    def btn_cauer(self):
        try:
            file_path = askopenfilename(filetypes=[("Text Files", "*.csv"), ("All Files", "*.*")])
            rc_network = cs.get_cauer_network(file_path)

            self.c_list, self.r_list = cs.sort_rc_list(rc_network)
            print(self.r_list, "\n", self.c_list)
            self.show_network(self.r_list, self.c_list)

        except cs.FC_Error_list.FosterCauer_Error as error:
            error = str(error)
            messagebox.showerror(title="Error", messagebox=error)

    def create_status_bar(self):
        """
        Create Status bar
        :return: None
        """
        status_bar = Frame()
        self.status = Label(self.master, text='Tool to create 1D RC Network', borderwidth=1,
                            font='Helv 10', anchor=W, relief=SUNKEN, name='status')
        self.status.pack(side=LEFT, padx=2, expand=Y, fill=BOTH)
        status_bar.pack(side=BOTTOM, fill=X, pady=2)

    def update_status(self, evt):
        """
        Function to update the Status
        :param evt: Mouse Enter event
        :return: None
        """
        try:
            # triggered on mouse entry if a menu item has focus
            # (focus occurs when user clicks on a top level menu item)

            item = self.tk.eval('%s entrycget active -label' % evt.widget)
            self.status_bar.configure(foreground='black',
                                      text=item)
        except TclError:
            # no label available, ignore
            pass

    def create_menu_panels(self):
        """
        Function creating menu panels
        :return: None
        """
        # create the main menu (only displays if child of the 'root' window)
        self.master.option_add('*tearOff', False)  # disable all tearoff's
        self.menu = Menu(self.master, name='menu')
        self.build_submenus()
        self.master.config(menu=self.menu)
        # set up standard bindings for the Menu class
        # (essentially to capture mouse enter/leave events)
        self.menu.bind_class('Menu', '<<MenuSelect>>', self.update_status)

    def build_submenus(self):
        """
        Function to add sub menus
        :return: None
        """
        self.add_options_menu()
        self.add_help_menu()
        # DELETE

    # ================================================================================
    # Submenu routines
    # ================================================================================
    # OPTIONS MENU
    def add_options_menu(self):
        """
        Adding Options Menu
        :return: None
        """
        options_menu = Menu(self.menu, name='options_menu')

        self.menu.add_cascade(label='Options', menu=options_menu, underline=0)

        options_menu.add_command(label='Foster Network Options',
                                 command=self.show_foster_options)

        self.add_diagnostic_menu(options_menu)  # check buttons
        options_menu.add_separator()
        options_menu.add_command(label='Exit',
                                 command=self.exit_app)

    def esc_exit_app(self, event):
        if event:
            self.exit_app()

    def exit_app(self):
        response = messagebox.askyesno(title="Exit", message="Are you sure you wish to Quit?")
        if response:
            self.master.destroy()

    def show_foster_options(self):
        window_network_options = Toplevel(self)
        window_network_options.title("Network Options-")
        window_network_options.iconbitmap('images//RC_1D_Calc.ico')
        self.foster_options_form(window_network_options)

        # ESC closes the widget.
        window_network_options.winfo_toplevel().bind('<Escape>', lambda x: window_network_options.destroy())

    def add_diagnostic_menu(self, cascades):
        # build the Cascades->Check Buttons submenu
        check = Menu(cascades)
        cascades.add_cascade(label='Diagnostic', underline=0,
                             menu=check)
        check.add_checkbutton(label='Save Foster Diagnostic',
                              command=self.flip_foster_diagnostic)
        check.add_checkbutton(label='Save Cauer Diagnostic',
                              command=self.flip_cauer_diagnostic)

    def flip_foster_diagnostic(self):
        self.foster_diagnostic = not self.foster_diagnostic

    def flip_cauer_diagnostic(self):
        self.cauer_diagnostic = not self.cauer_diagnostic

    def foster_options_form(self, window):
        option1 = Label(window, text="Foster Network Lower Limit-")
        option2 = Label(window, text="Foster Network Upper Limit-")
        option3 = Label(window, text="Foster Cost Function Tolerance-")
        option4 = Label(window, text="Foster Cost Independent Function-")

        default_option1_field = str(self.foster_lower_bound)
        default_option2_field = str(self.foster_upper_bound)
        default_option3_field = str(self.foster_ftol)
        default_option4_field = str(self.foster_xtol)

        # FIELD
        self.option1_field = Entry(window)
        self.option2_field = Entry(window)
        self.option3_field = Entry(window)
        self.option4_field = Entry(window)

        button_accept = Button(window, text="Accept", command=self.foster_options_accept)
        button_cancel = Button(window, text="Cancel", command=lambda: window.destroy())
        button_reset_default = Button(window, text="Reset Default", command=self.foster_options_reset_default)

        # PLACEMENT
        option1.grid(row=1, column=0)
        option2.grid(row=2, column=0)
        option3.grid(row=3, column=0)
        option4.grid(row=4, column=0)
        self.option1_field.grid(row=1, column=1, ipadx="50")
        self.option2_field.grid(row=2, column=1, ipadx="50")
        self.option3_field.grid(row=3, column=1, ipadx="50")
        self.option4_field.grid(row=4, column=1, ipadx="50")
        button_accept.grid(row=6, column=0)
        button_cancel.grid(row=6, column=1)
        button_reset_default.grid(row=6, column=2)

        self.option1_field.bind("<Return>", lambda a: self.option2_field.focus_set())
        self.option2_field.bind("<Return>", lambda a: self.option3_field.focus_set())
        self.option3_field.bind("<Return>", lambda a: self.option4_field.focus_set())
        self.option4_field.bind("<Return>", lambda a: button_accept.focus_set())

        # DEFAULT VALUES
        self.option1_field.insert(0, default_option1_field)
        self.option2_field.insert(0, default_option2_field)
        self.option3_field.insert(0, default_option3_field)
        self.option4_field.insert(0, default_option4_field)

    def foster_options_accept(self):
        self.foster_lower_bound = self.option1_field.get()
        self.foster_upper_bound = self.option2_field.get()
        self.foster_ftol = self.option3_field.get()
        self.foster_xtol = self.option4_field.get()

    def foster_options_reset_default(self):
        self.destroy()
        self.__init__()
        self.show_foster_options()

    # HELP MENU
    def add_help_menu(self):
        """
        Adding Options Menu
        :return: None
        """
        disclaimer_msg = "THE AUTHOR DOES NOT WARRANT THE CORRECTNESS OF ANY RESULTS OBTAINED WITH THIS TOOL." \
                         + "IN NO EVENT WILL OSRAM Continental OR ANY OF ITS EMPLOYEES BE LIABLE TO YOU FOR DAMAGES," \
                         + "INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE" \
                         + "USE OR INABILITY TO USE THE SOFTWARE(INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA" \
                         + "BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES)."

        help_menu = Menu(self.menu, name='help_menu')
        self.menu.add_cascade(label='Help', menu=help_menu, underline=0)

        help_menu.add_command(label='Info',
                              command=self.show_help_menu_info_msg)

        help_menu.add_command(label='Disclaimer',
                              command=lambda: messagebox.showwarning(title="Disclaimer", message=disclaimer_msg))
        help_menu.entryconfig(0, bitmap='questhead', compound=LEFT)

    def show_help_menu_info_msg(self):
        """
        Dispal Info Message
        :return: None
        """
        copyright_symbol = u"\u00A9"
        window = Toplevel(self)

        info_msg = "A simple tool to create a 1D RC Network" \
                   + "\n" + "Author - Shushanth Prabhu" + "\n" \
                   + "For any queries / suggestions send an email to-" \
                   + "\n shushanth@gmail.com" + "\n" \
                   + "All Rights Reserved" + "\n"
        # info_msg += "Code has the following dependencies-" + "\n"
        # info_msg += "\t" + "NumPy v1.17.4" + "\t" + "SciPy v1.3.3" + "\n"
        # info_msg += "\t" + "Sympy v1.5.1" + "\t" + "Python v3.7.5" + "\n"

        panel = Label(window, text=info_msg)
        panel.grid(row=1, column=2)



        ok_button = Button(window, text='Ok', command=window.destroy, width=10)
        ok_button.grid(row=2, column=1)
        ok_button.focus()

        # ESC closes the widget.
        window.winfo_toplevel().bind('<Escape>', lambda x: window.destroy())

    def rc_table(self, window, list1, list2):

        rc_frame = Frame(window)
        rc_frame.grid(row=1, column=2)

        cell = Entry(rc_frame, font=('Consolas 8 bold'), bg='light blue', justify='center')
        cell.grid(column=0, row=0)
        cell.insert(0, "Serial Number")

        cell = Entry(rc_frame, font=('Consolas 8 bold'), bg='light blue', justify='center')
        cell.grid(column=1, row=0)
        cell.insert(0, "Resistance")

        cell = Entry(rc_frame, font=('Consolas 8 bold'), bg='light blue', justify='center')
        cell.grid(column=2, row=0)
        cell.insert(0, "Capacitance")

        for i in range(len(list1)):
            cell = Entry(rc_frame)
            cell.grid(column=0, row=i + 1)
            cell.insert(0, i + 1)

            cell = Entry(rc_frame)
            cell.grid(column=1, row=i + 1)
            cell.insert(0, list1[i])

            cell = Entry(rc_frame)
            cell.grid(column=2, row=i + 1)
            cell.insert(0, list2[i])

        button_accept = Button(window, text="Accept", command=self.foster_options_accept)
        button_cancel = Button(window, text="Cancel", command=lambda: window.destroy())
        button_export = Button(window, text="Export as .txt", command=self.export_network)

        button_accept.grid(row=2, column=1)
        button_cancel.grid(row=2, column=2)
        button_export.grid(row=2, column=3)

    def show_network(self, list1, list2):
        table_output = Toplevel(self)
        table_output.title("RC Network Output-")
        table_output.iconbitmap('images//RC_1D_Calc.ico')
        self.rc_table(table_output, list1, list2)

        # ESC closes the widget.
        table_output.winfo_toplevel().bind('<Escape>', lambda x: table_output.destroy())

    def export_network(self):
        f = asksaveasfile(mode='w', defaultextension=".txt")
        if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        text2save = "Number"+"\t \t"+"Resistance"+"\t \t"+"Capacitance"+"\n"
        for i in range(0, len(self.r_list) - 1):
            text2save += str(i+1) + "\t \t" + str(self.r_list[i]) + "\t \t" + str(self.c_list[i]) + "\n"

        f.write(text2save)
        f.close()  # `()` was missing.


if __name__ == '__main__':
    MainWindow().mainloop()
