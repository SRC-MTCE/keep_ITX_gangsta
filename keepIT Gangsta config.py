import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import xml.etree.ElementTree as ET
from tkinter import ttk

def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def create_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Copy", command=lambda: widget.event_generate("<Control c>"))
    menu.add_command(label="Paste", command=lambda: widget.event_generate("<Control v>"))
    widget.bind("<Button-3>", lambda event: menu.tk_popup(event.x_root, event.y_root))

def display_xml_contents(tab_name):
    tree = ET.parse('lists.xml')
    root = tree.getroot()

    # Clear existing content in the frame
    for widget in master_list_xml_textbox_frame.winfo_children():
        widget.destroy()

    if tab_name == 'Control Point':
        control_points = root.find('control_points')
        if control_points is not None:
            xml_text = ''
            for control_point in control_points:
                name = control_point.find('name').text
                color = control_point.find('color').text
                xml_text += f"Name: {name}\nColor: {color}\n\n"
            control_point_xml_textbox.delete('1.0', tk.END)  # Clear the text box
            control_point_xml_textbox.insert(tk.INSERT, xml_text)
        else:
            control_point_xml_textbox.insert(tk.INSERT, "No control points found")
    elif tab_name == 'Master List':
        channels = root.find('master_list')
        if channels is not None:
            row = 0
            for channel in channels:
                name = channel.find('name').text

                # Display channel name
                name_label = tk.Label(master_list_xml_textbox_frame, text=f"Name: {name}", font=("Arial", 10, "bold"))
                name_label.grid(row=row, column=0, sticky='w')
                row += 1

                # Display each URL with a right-click option to delete
                urls = channel.findall('url')
                for url in urls:
                    url_text = url.text
                    url_label = tk.Label(master_list_xml_textbox_frame, text=f"URL: {url_text}", fg="blue", cursor="hand2")
                    url_label.grid(row=row, column=1, sticky='w')

                    # Create a context menu for each URL
                    url_menu = tk.Menu(master_list_xml_textbox_frame, tearoff=0)
                    url_menu.add_command(label="Copy", command=lambda u=url_text: copy_url(u))
                    url_menu.add_command(label="Delete", command=lambda u=url_text, n=name: delete_url(None, n, u))

                    # Bind right-click to show the context menu
                    url_label.bind("<Button-3>", lambda event, menu=url_menu: menu.tk_popup(event.x_root, event.y_root))

                    row += 1
        else:
            no_channels_label = tk.Label(master_list_xml_textbox_frame, text="No channels found")
            no_channels_label.grid(row=0, column=0, sticky='w')

    # Update the scroll region of the canvas
    master_list_canvas.update_idletasks()
    master_list_canvas.config(scrollregion=master_list_canvas.bbox("all"))

def copy_url(url_text):
    master_list_xml_textbox.clipboard_clear()
    master_list_xml_textbox.clipboard_append(url_text)
    master_list_xml_textbox.update()  # Now the clipboard contains the URL

def delete_url(event, channel_name, url_text):
    tree = ET.parse('lists.xml')
    root = tree.getroot()

    channels = root.find('master_list')
    for channel in channels.findall('channel'):
        name = channel.find('name').text
        if name == channel_name:
            urls = channel.findall('url')
            for url in urls:
                if url.text == url_text:
                    channel.remove(url)
                    break

            if not channel.findall('url'):
                channels.remove(channel)
                
            break

    indent(root)
    tree.write('lists.xml', encoding='utf-8', xml_declaration=True, method="xml", short_empty_elements=False)
    
    display_xml_contents('Master List')

def add_control_point():
    name = control_point_name_entry.get()
    color = control_point_color_var.get()
    if name and color:
        tree = ET.parse('lists.xml')
        root = tree.getroot()

        control_points = root.find('control_points')
        if control_points is None:
            control_points = ET.SubElement(root, 'control_points')

        control_point = ET.SubElement(control_points, 'control_point')
        control_point_name = ET.SubElement(control_point, 'name')
        control_point_name.text = name
        control_point_color = ET.SubElement(control_point, 'color')
        control_point_color.text = color
        
        indent(root)
        tree.write('lists.xml', encoding='utf-8', xml_declaration=True, method="xml", short_empty_elements=False)
        
        control_point_name_entry.delete(0, tk.END)
        control_point_color_var.set('')
        display_xml_contents('Control Point')
    else:
        messagebox.showerror("Error", "Please enter both name and color")

def add_channel():
    name = channel_name_entry.get()
    url = channel_url_entry.get()
    if name and url:
        tree = ET.parse('lists.xml')
        root = tree.getroot()

        channels = root.find('master_list')
        channel_exists = False
        for channel in channels.findall('channel'):
            channel_name = channel.find('name').text
            if channel_name == name:
                channel_exists = True
                new_url = ET.SubElement(channel, 'url')
                new_url.text = url
                break
        
        if not channel_exists:
            channel = ET.SubElement(channels, 'channel')
            channel_name = ET.SubElement(channel, 'name')
            channel_name.text = name
            channel_url = ET.SubElement(channel, 'url')
            channel_url.text = url
        
        indent(root)
        tree.write('lists.xml', encoding='utf-8', xml_declaration=True, method="xml", short_empty_elements=False)
        
        channel_name_entry.delete(0, tk.END)
        channel_url_entry.delete(0, tk.END)
        display_xml_contents('Master List')
    else:
        messagebox.showerror("Error", "Please enter both name and URL")

def remove_control_point():
    name = control_point_name_entry.get()
    if name:
        tree = ET.parse('lists.xml')
        root = tree.getroot()

        control_points = root.find('control_points')
        for control_point in control_points:
            if control_point.find('name').text == name:
                control_points.remove(control_point)
                tree.write('lists.xml', encoding='utf-8', xml_declaration=True, method="xml", short_empty_elements=False)
                display_xml_contents('Control Point')
                break
        else:
            messagebox.showerror("Error", "Control point not found in the list")
        
        control_point_name_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter the name of the control point to remove")

def remove_channel():
    name = channel_name_entry.get()
    if name:
        tree = ET.parse('lists.xml')
        root = tree.getroot()

        channels = root.find('master_list')
        for channel in channels:
            if channel.find('name').text == name:
                channels.remove(channel)
                tree.write('lists.xml', encoding='utf-8', xml_declaration=True, method="xml", short_empty_elements=False)
                display_xml_contents('Master List')
                break
        else:
            messagebox.showerror("Error", "Channel not found in the list")
        
        channel_name_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter the name of the channel to remove")

root = ctk.CTk()
root.title("Control Point Editor")
root.geometry("600x900")
root.configure(background='#FFFFFF')

tab_control = ttk.Notebook(root)
tab_control.pack(fill=tk.BOTH, expand=True)

control_point_tab = ctk.CTkFrame(tab_control)
master_list_tab = ctk.CTkFrame(tab_control)

tab_control.add(control_point_tab, text='Control Point')
tab_control.add(master_list_tab, text='Master List')

# Create a scrollable canvas for the Master List tab
master_list_canvas = tk.Canvas(master_list_tab)
master_list_scrollbar = tk.Scrollbar(master_list_tab, orient="vertical", command=master_list_canvas.yview)
master_list_xml_textbox_frame = ctk.CTkFrame(master_list_canvas)

# Configure scrollable frame
master_list_xml_textbox_frame.bind("<Configure>", lambda e: master_list_canvas.configure(scrollregion=master_list_canvas.bbox("all")))
master_list_canvas.create_window((0, 0), window=master_list_xml_textbox_frame, anchor="nw")
master_list_canvas.configure(yscrollcommand=master_list_scrollbar.set)

master_list_canvas.pack(side="left", fill="both", expand=True)
master_list_scrollbar.pack(side="right", fill="y")

# Create a text box for control point XML
control_point_xml_textbox = ctk.CTkTextbox(control_point_tab, width=400, height=600)
control_point_xml_textbox.pack(anchor=tk.W, padx=(5, 0), pady=5)

# Entry and button to add a control point
control_point_name_entry = ctk.CTkEntry(control_point_tab, placeholder_text="Control Point Name")
control_point_name_entry.pack(anchor=tk.W, padx=(5, 0), pady=5)

control_point_color_var = tk.StringVar()
control_point_color_entry = ctk.CTkEntry(control_point_tab, textvariable=control_point_color_var, placeholder_text="Color")
control_point_color_entry.pack(anchor=tk.W, padx=(5, 0), pady=5)

add_control_point_button = ctk.CTkButton(control_point_tab, text="Add Control Point", command=add_control_point)
add_control_point_button.pack(anchor=tk.W, padx=(5, 0), pady=5)
remove_control_point_button = ctk.CTkButton(control_point_tab, text="Remove Control Point", command=remove_control_point)
remove_control_point_button.pack(anchor=tk.W, padx=(5, 0), pady=5)

# Entry and button to add a channel
channel_name_entry = ctk.CTkEntry(master_list_tab, placeholder_text="Channel Name")
channel_name_entry.pack(anchor=tk.W, padx=(5, 0), pady=5)
channel_url_entry = ctk.CTkEntry(master_list_tab, placeholder_text="Channel URL")
channel_url_entry.pack(anchor=tk.W, padx=(5, 0), pady=5)
add_channel_button = ctk.CTkButton(master_list_tab, text="Add Channel", command=add_channel)
add_channel_button.pack(anchor=tk.W, padx=(5, 0), pady=5)
remove_channel_button = ctk.CTkButton(master_list_tab, text="Remove Channel", command=remove_channel)
remove_channel_button.pack(anchor=tk.W, padx=(5, 0), pady=5)

# Create display XML buttons
display_control_point_xml_button = ctk.CTkButton(control_point_tab, text="Display XML", command=lambda: display_xml_contents('Control Point'))
display_control_point_xml_button.pack(anchor=tk.W, padx=(5, 0), pady=5)
display_master_list_xml_button = ctk.CTkButton(master_list_tab, text="Display XML", command=lambda: display_xml_contents('Master List'))
display_master_list_xml_button.pack(anchor=tk.W, padx=(5, 0), pady=5)

create_context_menu(control_point_xml_textbox)
create_context_menu(master_list_xml_textbox_frame)

display_xml_contents('Control Point')
display_xml_contents('Master List')

root.mainloop()
