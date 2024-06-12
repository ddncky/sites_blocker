import customtkinter
import tkinter
import tkinter.messagebox
from datetime import datetime, timedelta

import sites_handler as m
import stoic_api


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(
    "green"
)  # Themes: "blue" (standard), "green", "dark-blue"


class ScrollableCheckBoxFrame(customtkinter.CTkScrollableFrame):
    """Extends the functionality of the customtinkers's CTkScrollableFrame, adds some methods"""

    def __init__(self, master, item_list, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.checkbox_list = []
        for i, item in enumerate(item_list):
            self.add_item(item)

    def add_item(self, item):
        checkbox = customtkinter.CTkCheckBox(self, text=item)
        if self.command is not None:
            checkbox.configure(command=self.command)
        checkbox.grid(
            row=len(self.checkbox_list), column=0, pady=(0, 10), sticky="NSEW"
        )
        self.checkbox_list.append(checkbox)

    def remove_item(self, item):
        for checkbox in self.checkbox_list:
            if item == checkbox.cget("text"):
                checkbox.destroy()
                self.checkbox_list.remove(checkbox)
                return

    def add_or_del_common_filter_to_sites_to_block(self):
        for checkbox in self.checkbox_list:
            if checkbox.get() == 1:
                name = checkbox.cget("text")
                if name not in m.sites_to_block:
                    m.sites_to_block.append(name)
                    m.sites_to_block.append(name[4:])
            else:
                name = checkbox.cget("text")
                if name in m.sites_to_block:
                    m.sites_to_block.remove(name)
                    m.sites_to_block.remove(name[4:])
        print(m.sites_to_block)

    @property
    def get_checkbox_list(self):
        return self.checkbox_list


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("SitesBlocker")
        self.geometry(f"{800}x{600}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="Settings",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.block_button = customtkinter.CTkButton(
            self.sidebar_frame, command=self.start_session, text="Block"
        )
        self.block_button.grid(row=1, column=0, padx=20, pady=10)
        self.unblock_button = customtkinter.CTkButton(
            self.sidebar_frame, command=m.unblock_sites, text="Unblock"
        )
        self.unblock_button.grid(row=2, column=0, padx=20, pady=10)
        self.delete_input_button = customtkinter.CTkButton(
            self.sidebar_frame,
            text="Delete Website",
            command=self.open_input_dialog_event,
        )
        self.delete_input_button.grid(row=4, column=0, padx=20, pady=10)
        self.locked_mode_button = customtkinter.CTkSwitch(
            self.sidebar_frame, text="Locked Mode"
        )
        self.locked_mode_button.grid(row=3, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Theme:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Dark", "Light"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="UI Scaling:", anchor="w"
        )
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["80%", "90%", "100%"],
            command=self.change_scaling_event,
        )
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry = customtkinter.CTkEntry(
            self, placeholder_text="Enter Website", textvariable=None
        )
        self.entry.grid(
            row=3, column=1, columnspan=3, padx=(20, 15), pady=(10, 20), sticky="nsew"
        )

        self.entry_button = customtkinter.CTkButton(
            master=self,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=self.add_website_to_block,
            text="Enter",
        )
        self.entry_button.grid(
            row=3, column=4, padx=(0, 10), pady=(20, 30), sticky="nsew"
        )

        # create radiobutton frame
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.grid(
            row=0, column=4, padx=(20, 20), pady=(20, 0), sticky="nsew"
        )
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(
            master=self.radiobutton_frame,
            text="Templates:",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.label_radio_group.grid(
            row=0, column=2, columnspan=1, padx=10, pady=10, sticky=""
        )

        self.radio_button_1 = customtkinter.CTkRadioButton(
            master=self.radiobutton_frame,
            variable=self.radio_var,
            value=0,
            text="Use common template",
            command=self.common_template_activate,
        )
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="nsew")
        self.radio_button_2 = customtkinter.CTkRadioButton(
            master=self.radiobutton_frame,
            variable=self.radio_var,
            value=1,
            text="Use new template",
            command=self.new_template_activate,
        )
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="nsew")

        # create scrollable frame
        self.scrollable_checkbox_frame = ScrollableCheckBoxFrame(
            master=self,
            command=self.add_checkbox,
            item_list=[f"{m.common_filters[i]}" for i in range(len(m.common_filters))],
            label_text="Commonly used:",
        )
        self.scrollable_checkbox_frame.grid(
            row=1, column=4, padx=(20, 20), pady=(20, 0), sticky="nsew"
        )

        # create time frame
        self.time_frame = customtkinter.CTkFrame(self)
        self.time_frame.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        self.time_logo_label = customtkinter.CTkLabel(
            self.time_frame,
            text="Session duration:",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self.time_logo_label.grid(row=0, column=1, padx=(10, 0), pady=10)

        self.time_entry_1 = customtkinter.CTkEntry(
            self.time_frame, placeholder_text="Hours", textvariable=None
        )
        self.time_entry_1.grid(
            row=1, column=1, columnspan=1, padx=(15, 10), pady=30, sticky="nsew"
        )
        self.time_entry_2 = customtkinter.CTkEntry(
            self.time_frame, placeholder_text="Minutes", textvariable=None
        )
        self.time_entry_2.grid(
            row=1, column=2, columnspan=1, padx=(20, 10), pady=30, sticky="nsew"
        )

        self.time_entry_button = customtkinter.CTkButton(
            master=self.time_frame,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "#DCE4EE"),
            command=self.start_session,
            text="Start",
        )
        self.time_entry_button.grid(
            row=2, column=1, columnspan=2, padx=(20, 10), pady=0, sticky="nsew"
        )

        # create textbox
        self.textbox = customtkinter.CTkTextbox(
            self,
            height=150,
            text_color="aquamarine4",
            font=customtkinter.CTkFont(
                size=15, weight="normal", slant="roman", family="monospace"
            ),
        )
        self.textbox.grid(row=1, column=1, padx=(20, 0), pady=(20, 100), sticky="EW")

        # set default values
        self.scaling_optionemenu.set("100%")
        self.textbox.insert(
            "0.0",
            f"Наставление на сегодня от {stoic_api.author}:\n\n{stoic_api.quote[:-1]}.",
        )
        self.radio_button_2.select()

    def activate_or_deactivate_button(self, lockmode=False):
        """Depending on the lockmode, activates or deactivates all buttons"""
        if lockmode:
            self.block_button.configure(state="disabled")
            self.unblock_button.configure(state="disabled")
            self.delete_input_button.configure(state="disabled")
            self.entry_button.configure(state="disabled")
            self.entry.configure(state="disabled")
            self.radio_button_1.configure(state="disabled")
            self.radio_button_2.configure(state="disabled")
            self.time_entry_1.configure(state="disabled")
            self.time_entry_2.configure(state="disabled")
            self.time_entry_button.configure(state="disabled")

            for checkbox in self.scrollable_checkbox_frame.checkbox_list:
                checkbox.configure(state="disabled")

        else:
            self.block_button.configure(state="normal")
            self.unblock_button.configure(state="normal")
            self.delete_input_button.configure(state="normal")
            self.entry_button.configure(state="normal")
            self.entry.configure(state="normal")
            self.radio_button_1.configure(state="normal")
            self.radio_button_2.configure(state="normal")
            self.time_entry_1.configure(state="normal")
            self.time_entry_2.configure(state="normal")
            self.time_entry_button.configure(state="normal")

            for checkbox in self.scrollable_checkbox_frame.checkbox_list:
                checkbox.configure(state="normal")

    def lockmode_switcher(self):
        """Returns True or False depending on the lockmode switcher position"""
        return True if self.locked_mode_button.get() == 1 else False

    def new_template_activate(self):
        """When 'Use new template' button is active, deselects all scrollable buttons"""
        m.common_filters = []
        for checkbox in self.scrollable_checkbox_frame.checkbox_list:
            checkbox.deselect()

    def common_template_activate(self):
        """When 'Use common template' button is active, selects all scrollable buttons"""
        for site in m.common_filters:
            m.sites_to_block.append(site)
            m.sites_to_block.append(site[4:])

        for checkbox in self.scrollable_checkbox_frame.checkbox_list:
            checkbox.select()

    def start_session(self):
        """Starts the session (blocks websites), also locks all the buttins depending on the lockmode button"""
        hours = int(self.time_entry_1.get()) if self.time_entry_1.get() else 0
        mins = int(self.time_entry_2.get()) if self.time_entry_2.get() else 0

        curr_date = datetime.now()
        m.end_time = curr_date + timedelta(hours=hours, minutes=mins)
        time_diff = (m.end_time - curr_date).total_seconds()

        m.block_sites(seconds=time_diff)

        lock = self.lockmode_switcher()
        self.activate_or_deactivate_button(lock)

    def add_website_to_block(self):
        """Takes the input from the entry field and adds it to the block list"""
        site = self.entry.get()
        if site.startswith("www.") and site.count(".") >= 2:
            if site.count(" ") == 0:
                m.sites_to_block.append(site)
                m.sites_to_block.append(site[4:])
            else:
                sites = site.split()
                for site in sites:
                    m.sites_to_block.append(site)
                    m.sites_to_block.append(site[4:])

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def add_checkbox(self):
        self.scrollable_checkbox_frame.add_or_del_common_filter_to_sites_to_block()

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(
            text="Enter the site you want to delete starting with 'www:'",
            title="Delete",
        )
        site = dialog.get_input()
        if site in m.sites_to_block:
            m.sites_to_block.remove(site)
            m.sites_to_block.remove(site[4:])


def closing_app():
    m.unblock_sites()
    app.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", closing_app)
    app.mainloop()
