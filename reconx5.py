from tkinter import messagebox, ttk
from bs4 import BeautifulSoup
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore
from ipwhois import IPWhois
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ipwhois import IPWhois
from CTkMenuBar import *
import customtkinter as ctk
import requests
import threading
import os
import subprocess
import socket
import tkinter as tk
import re
import whois

requests.packages.urllib3.disable_warnings()

class ReconX:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("ReconX")
        self.window.geometry("1025x575")
        self.window.configure(bg="#000000")
        self.window.configure(fg_color="#000000")
        # Add window icon (add this after window creation)
        icon_photo = tk.PhotoImage(file="logo.png")
        self.window.iconphoto(False, icon_photo)
        #self.window.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        style = ttk.Style()
        style.configure("Treeview", background="#000000", fieldbackground="#000000", foreground="white", font=("Arial", 14))
        style.map("Treeview", background=[("selected", "#14375e")])

        file_menu = CTkMenuBar(master=self.window, bg_color="#000000")
        file_button = file_menu.add_cascade("File")
        file_button_help =  file_menu.add_cascade("Help")

        submenu = CustomDropdownMenu(widget=file_button, bg_color="#000000")
        submenu.add_option("Save")
        submenu.add_separator()
        submenu.add_option("Exit")

        helpmenu = CustomDropdownMenu(widget=file_button_help, bg_color="#000000")
        helpmenu.add_option("About")

        self.frame = ctk.CTkFrame(self.window, border_width=0, width=780, height=430, fg_color="#000000", border_color="#000000")
        self.frame.pack(padx=10, pady=10)

        self.frame_top = ctk.CTkFrame(self.window, width=780, height=430, fg_color="#000000", border_width=1, border_color="white")
        self.frame_top.pack(side=ctk.RIGHT, padx=10, pady=10)

        self.menu_frame = ctk.CTkFrame(self.frame_top, width=750, height=360, fg_color="#000000")
        self.menu_frame.pack(side=ctk.TOP, padx=10, pady=10)

        self.settings_frame = ctk.CTkFrame(self.window, width=750, height=360, border_width=1, border_color="white", fg_color="#000000")
        self.settings_frame.pack(side=ctk.LEFT, padx=10, pady=10, fill="both", expand=True)
        self.settings_frame.grid_propagate(False)

        self.progress_bar = ctk.CTkProgressBar(self.frame_top, width=700, height=7, corner_radius=10)
        self.progress_bar.pack(side=ctk.BOTTOM, padx=10, pady=10)

        self.progress_label = ctk.CTkLabel(self.frame_top, text="Waiting for input...", font=("Arial", 14), text_color="white")
        self.progress_label.pack(side=ctk.BOTTOM, padx=10, pady=10)

        self.entry = ctk.CTkEntry(self.frame, width=580, height=40, placeholder_text="Enter a domain", font=("Arial", 14), text_color="white", bg_color="#000000", fg_color="#000000")
        self.entry.pack(side=ctk.LEFT, padx=10, pady=10)

        self.start_port_frame = ctk.CTkFrame(self.settings_frame, width=40, height=360, fg_color="#000000")
        self.start_port_frame.pack(side=ctk.BOTTOM, padx=10, pady=10)
        self.start_port_frame.grid_propagate(False)

        self.startport_entry = ctk.CTkEntry(self.start_port_frame, width=50, height=9, placeholder_text="1", font=("Arial", 14), text_color="white", bg_color="#000000", fg_color="#000000")
        self.startport_entry.pack(side=ctk.LEFT, padx=10, pady=10)
        self.endport_entry = ctk.CTkEntry(self.start_port_frame, width=50, height=9, placeholder_text="1024", font=("Arial", 14), text_color="white", bg_color="#000000", fg_color="#000000")
        self.endport_entry.pack(side=ctk.LEFT, padx=10, pady=10)

        self.is_scanning = False
        self.stop_image = ctk.CTkImage(Image.open("stop.png"), size=(20, 20))
        self.stop_button = ctk.CTkButton(self.frame, width=25, height=40, text="", 
                                        font=("Arial", 14), text_color="white",
                                        command=self.stop_scan, image=self.stop_image,
                                        corner_radius=100, fg_color="#14375e")
        self.stop_button.pack(side=ctk.RIGHT, padx=10, pady=10)
        self.stop_button.configure(state=ctk.DISABLED)

        self.start_image = ctk.CTkImage(Image.open("start.png"), size=(20, 20))
        self.button = ctk.CTkButton(self.frame, width=25, height=40, text="", font=("Arial", 14), text_color="white", 
                                    command=self.check_selected, image=self.start_image, corner_radius=100, fg_color="#14375e")
        self.button.pack(side=ctk.RIGHT, padx=10, pady=10)

        self.clear_image = ctk.CTkImage(Image.open("clear.png"), size=(20, 20))
        self.clear_button = ctk.CTkButton(self.frame, width=25, height=40, text="", font=("Arial", 14), text_color="white", 
                                          command=self.clear_textbox, image=self.clear_image, corner_radius=100, fg_color="#14375e")
        self.clear_button.pack(side=ctk.RIGHT, padx=10, pady=10)



        self.waiting_frames = ["Waiting for input", "Waiting for input.", "Waiting for input..", "Waiting for input..."]
        self.current_frame = 0
        self.animate_waiting()

        #self.textbox = ctk.CTkTextbox(self.frame_top, width=760, height=360, font=("Arial", 14), text_color="white", bg_color="#000000", fg_color="#000000")
        #self.textbox.pack(side=ctk.LEFT, padx=10, pady=10)

        self.menu = ctk.CTkOptionMenu(self.frame, width=100, height=25, values=["Headers", "Port Scan", "ASN", "Subdomains", "Links", "JavaScript", "Whois"], font=("Arial", 14), text_color="white", 
                                      bg_color="#000000", fg_color="#000000")
        self.menu.pack(side=ctk.RIGHT, padx=10, pady=10)

        self.tabview = ctk.CTkTabview(self.frame_top, width=760, height=360, text_color="white", fg_color="transparent", 
                                      border_width=0, corner_radius=0, segmented_button_selected_color="#000000", segmented_button_selected_hover_color="#000000", segmented_button_unselected_color="#000000", 
                                      segmented_button_unselected_hover_color="#000000")
        self.tabview.pack(side=ctk.LEFT, padx=10, pady=10)
        self.tabview.add("Home")
        self.tabview.add("Subdomains")
        self.tabview.add("ASN")
        self.tabview.add("Headers")
        self.tabview.add("Links")
        self.tabview.add("JavaScript")
        self.tabview.add("Whois")
        self.tabview._segmented_button.configure(border_width=0, fg_color="#000000", text_color="#000000")


        self.port_services_tabview = ctk.CTkTabview(self.settings_frame, width=200, height=500, text_color="white", fg_color="#000000")
        self.port_services_tabview.pack(side=ctk.TOP, padx=10, pady=10)
        self.port_services_tabview.add("Ports")
        self.port_services_tabview.add("Services")
        self.port_services_tabview._segmented_button.configure(border_width=0, fg_color="#000000", text_color="#000000")

        #self.scrollbar = ctk.CTkScrollbar(self.frame2, width=15, height=360, orientation="vertical")
        #self.scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        #self.textbox.configure(yscrollcommand=self.scrollbar.set)
        #self.scrollbar.configure(command=self.textbox.yview)

        self.logo_image = ctk.CTkImage(Image.open("logo.png"), size=(100, 100)) 
        self.home_label = ctk.CTkLabel(self.tabview.tab("Home"), text="", font=("Arial", 25), text_color="white", image=self.logo_image, compound="top")
        self.home_label.pack(side=ctk.TOP, padx=10, pady=10)

        self.home_label = ctk.CTkLabel(self.tabview.tab("Home"), text="WELCOME TO RECONX", font=("Arial", 25), text_color="white")
        self.home_label.pack(side=ctk.TOP, padx=10, pady=10)
        
        

        self.subdomain_tree = ttk.Treeview(self.tabview.tab("Subdomains"), columns=("Domain", "Status Code", "IP", "Server"), show="headings", style="Treeview")
        self.subdomain_tree.heading("Domain", text="Domain")
        self.subdomain_tree.heading("Status Code", text="Status Code")  # Match the column name
        self.subdomain_tree.heading("IP", text="IP")
        self.subdomain_tree.heading("Server", text="Server")
        # Optional: Set column widths
        self.subdomain_tree.column("Domain", width=150)
        self.subdomain_tree.column("Status Code", width=70)
        self.subdomain_tree.column("IP", width=100)
        self.subdomain_tree.column("Server", width=100)
        # Add scrollbar 
        self.subdomain_scrollbar = ttk.Scrollbar(self.tabview.tab("Subdomains"), orient="vertical", command=self.subdomain_tree.yview)
        self.subdomain_tree.configure(yscrollcommand=self.subdomain_scrollbar.set)
        # Pack the Treeview and scrollbar
        self.subdomain_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.subdomain_scrollbar.pack(side="right", fill="y")

        self.ports_tree = ttk.Treeview(self.port_services_tabview.tab("Ports"), columns=("Ports"), show="headings", style="Treeview")
        self.ports_tree.heading("Ports", text="Ports")

        # Optional: Set column widths
        self.ports_tree.column("Ports", width=150, anchor="center")
        self.ports_tree.pack(side="right", fill="both")


        self.services_tree = ttk.Treeview(self.port_services_tabview.tab("Services"), columns=("Services"), show="headings", style="Treeview")
        self.services_tree.heading("Services", text="Services")

        # Optional: Set column widths
        self.services_tree.column("Services", width=150)
        self.services_tree.pack(side="right", fill="both")

        # ASN Tree
        self.asn_tree = ttk.Treeview(self.tabview.tab("ASN"), 
                                   columns=("Property", "Value"), 
                                   show="headings", 
                                   style="Treeview")
        self.asn_tree.heading("Property", text="Property")
        self.asn_tree.heading("Value", text="Value")
        self.asn_tree.pack(side="left", fill="both", expand=True)

        # Headers Tree
        self.headers_tree = ttk.Treeview(self.tabview.tab("Headers"), 
                                   columns=("Value", "Key"), 
                                   show="headings", 
                                   style="Treeview")
        self.headers_tree.heading("Value", text="Value")
        self.headers_tree.heading("Key", text="Key")
        self.headers_tree.pack(side="left", fill="both", expand=True)

        self.headers_scrollbar = ttk.Scrollbar(self.tabview.tab("Headers"), orient="vertical", command=self.headers_tree.yview)
        self.headers_tree.configure(yscrollcommand=self.headers_scrollbar.set)
        self.headers_scrollbar.pack(side="right", fill="y")

        # Javascript Tree
        self.javascript_tree = ttk.Treeview(self.tabview.tab("JavaScript"), 
                                   columns=("Files", "Status"), 
                                   show="headings", 
                                   style="Treeview")
        self.javascript_tree.heading("Files", text="Files")
        self.javascript_tree.heading("Status", text="Status")
        self.javascript_tree.pack(side="left", fill="both", expand=True)
        self.javascript_tree.column("Status", anchor="center")
        self.javascript_tree.column("Files", width=275)
        self.javascript_scrollbar = ttk.Scrollbar(self.tabview.tab("JavaScript"), orient="vertical", command=self.javascript_tree.yview)
        self.javascript_tree.configure(yscrollcommand=self.javascript_scrollbar.set)
        self.javascript_scrollbar.pack(side="right", fill="y")


        # Links Tree
        self.links_tree = ttk.Treeview(self.tabview.tab("Links"), 
                                   columns=("Links"), 
                                   show="headings", 
                                   style="Treeview")
        self.links_tree.heading("Links", text="Links")
        self.links_tree.pack(side="left", fill="both", expand=True)
        self.links_tree.column("Links", width=250)
        self.links_scrollbar = ttk.Scrollbar(self.tabview.tab("Links"), orient="vertical", command=self.links_tree.yview)
        self.links_tree.configure(yscrollcommand=self.links_scrollbar.set)
        self.links_scrollbar.pack(side="right", fill="y")

        # WHOIS Tree
        self.whois_tree = ttk.Treeview(self.tabview.tab("Whois"), 
                                   columns=("Content", "Value"), 
                                   show="headings", 
                                   style="Treeview")
        self.whois_tree.heading("Content", text="Content")
        self.whois_tree.heading("Value", text="Value")
        self.whois_tree.pack(side="left", fill="both", expand=True)
        self.whois_tree.column("Content", width=150)
        self.whois_tree.column("Value", width=250)
        self.whois_scrollbar = ttk.Scrollbar(self.tabview.tab("Whois"), orient="vertical", command=self.whois_tree.yview)
        self.whois_tree.configure(yscrollcommand=self.whois_scrollbar.set)
        self.whois_scrollbar.pack(side="right", fill="y")



        self.home_image = ctk.CTkImage(Image.open("home.png"), size=(30, 30)) 
        self.home_button = ctk.CTkButton(self.menu_frame, width=20, height=20, text="", font=("Arial", 14), image=self.home_image, 
                                               corner_radius=100, fg_color="transparent", text_color="white", command=lambda: self.switch_tab("Home"))
        self.home_button.pack(side=ctk.LEFT, padx=10, pady=10)


        self.subdomains_image = ctk.CTkImage(Image.open("domains.png"), size=(30, 30)) 
        self.subdomains_button = ctk.CTkButton(self.menu_frame, width=20, height=20, text="", font=("Arial", 14), image=self.subdomains_image, 
                                               corner_radius=100, fg_color="transparent", text_color="white", command=lambda: self.switch_tab("Subdomains"))
        self.subdomains_button.pack(side=ctk.LEFT, padx=10, pady=10)


        self.asn_image = ctk.CTkImage(Image.open("asn.png"), size=(30, 30))     
        self.asn_button = ctk.CTkButton(self.menu_frame, width=20, height=20, text="", font=("Arial", 14), image=self.asn_image, 
                                               corner_radius=100, fg_color="transparent", text_color="white", command=lambda: self.switch_tab("ASN"))
        self.asn_button.pack(side=ctk.LEFT, padx=10, pady=10)

        self.headers_image = ctk.CTkImage(Image.open("headers.png"), size=(30, 30))     
        self.headers_button = ctk.CTkButton(self.menu_frame, width=20, height=20, text="", font=("Arial", 14), image=self.headers_image, 
                                               corner_radius=100, fg_color="transparent", text_color="white", command=lambda: self.switch_tab("Headers"))
        self.headers_button.pack(side=ctk.LEFT, padx=10, pady=10)


        self.javascript_image = ctk.CTkImage(Image.open("javascript.png"), size=(30, 30))     
        self.javascript_button = ctk.CTkButton(self.menu_frame, width=20, height=20, text="", font=("Arial", 14), image=self.javascript_image, 
                                               corner_radius=100, fg_color="transparent", text_color="white", command=lambda: self.switch_tab("JavaScript"))
        self.javascript_button.pack(side=ctk.LEFT, padx=10, pady=10)


        self.links_image = ctk.CTkImage(Image.open("links.png"), size=(30, 30))     
        self.links_button = ctk.CTkButton(self.menu_frame, width=20, height=20, text="", font=("Arial", 14), image=self.links_image, 
                                               corner_radius=100, fg_color="transparent", text_color="white", command=lambda: self.switch_tab("Links"))
        self.links_button.pack(side=ctk.LEFT, padx=10, pady=10)


        self.whois_image = ctk.CTkImage(Image.open("whois.png"), size=(30, 30))     
        self.whois_button = ctk.CTkButton(self.menu_frame, width=20, height=20, text="", font=("Arial", 14), image=self.whois_image, 
                                               corner_radius=100, fg_color="transparent", text_color="white", command=lambda: self.switch_tab("Whois"))
        self.whois_button.pack(side=ctk.LEFT, padx=10, pady=10)

    def stop_scan(self):
        """Stop any running scan"""
        self.is_scanning = False
        self.progress_label.configure(text="Scan stopped by user")
        self.stop_button.configure(state=ctk.DISABLED)
        self.button.configure(state=ctk.NORMAL)
        self.clear_button.configure(state=ctk.NORMAL)

    def start_scan(self):
        """Common method to start any scan"""
        self.is_scanning = True
        self.button.configure(state=ctk.DISABLED)
        self.clear_button.configure(state=ctk.DISABLED)
        self.stop_button.configure(state=ctk.NORMAL)

    def animate_waiting(self):
        """Animate the waiting text"""
        if self.progress_label.cget("text").startswith("Waiting for input"):
            self.current_frame = (self.current_frame + 1) % len(self.waiting_frames)
            self.progress_label.configure(text=self.waiting_frames[self.current_frame])
        self.window.after(500, self.animate_waiting) 

    def switch_tab(self, tab_name):
        """Switch to the specified tab"""
        try:
            self.tabview.set(tab_name)
            
            # Optional: Update button appearances to show active state
            buttons = {
                "Home": self.home_button,
                "Subdomains": self.subdomains_button,
                "ASN": self.asn_button,
                "Headers": self.headers_button,
                "Links": self.links_button,
                "JS Files": self.javascript_button,
                "Whois": self.whois_button
            }
            
            # Reset all buttons to default state
            for button in buttons.values():
                button.configure(fg_color="transparent")
            
            # Highlight active button
            if tab_name in buttons:
                buttons[tab_name].configure(fg_color="#14375e")
                
        except Exception as e:
            print(f"Error switching to tab {tab_name}: {e}")


    def check_selected(self):
        if self.menu.get() == "Headers":
            self.headers_thread()
        elif self.menu.get() == "Subdomains":
            self.subdomain_thread()
        elif self.menu.get() == "Port Scan":
            self.ports_thread()
        elif self.menu.get() == "ASN":
            self.asn_thread()
        elif self.menu.get() == "Headers":
            self.get_headers()
        elif self.menu.get() == "JavaScript":
            self.javascript_thread()
        elif self.menu.get() == "Links":
            self.links_thread()
        elif self.menu.get() == "Whois":
            self.whois_thread()

    def process_link(self, link):
        """Process individual link and return formatted result"""
        try:
            href = link.get('href')
            if href.startswith('//'):
                href = f'https:{href}'
            elif href.startswith('/'):
                base_domain = self.entry.get().replace('https://', '').replace('http://', '')
                href = f'https://{base_domain}{href}'
            elif not href.startswith(('http://', 'https://')):
                base_domain = self.entry.get().replace('https://', '').replace('http://', '')
                href = f'https://{base_domain}/{href}'
            return href
        except Exception as e:
            print(f"Error processing link: {e}")
            return None
        
    def process_whois_data(self, key, value):
        """Process individual whois data entries with better formatting"""
        try:
            # Handle lists
            if isinstance(value, list):
                # Join list items with newlines, handle nested structures
                formatted_items = []
                for item in value:
                    if isinstance(item, (dict, list)):
                        formatted_items.append(self.format_complex_value(item))
                    else:
                        formatted_items.append(str(item))
                value = "\n".join(formatted_items)
            
            # Handle dictionaries
            elif isinstance(value, dict):
                value = self.format_complex_value(value)
            
            # Handle dates
            elif "datetime.datetime" in str(type(value)):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            
            # Handle all other types
            else:
                value = str(value)
            
            return key, value

        except Exception as e:
            print(f"Error processing whois data {key}: {e}")
            return key, "Error processing"

    def format_complex_value(self, value):
        """Format complex data structures (dicts/nested) into readable string"""
        if isinstance(value, dict):
            formatted_items = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    v = self.format_complex_value(v)
                formatted_items.append(f"{k}: {v}")
            return "\n".join(formatted_items)
        
        elif isinstance(value, list):
            for item in value:
                return ",".join(map(str, item))
        
        return str(value)

    def whois(self):
        try:
            domain = self.entry.get()
            self.button.configure(state=ctk.DISABLED)
            self.clear_button.configure(state=ctk.DISABLED)
            
            # Clear existing entries
            for item in self.whois_tree.get_children():
                self.whois_tree.delete(item)
                
            self.progress_bar.start()
            self.progress_label.configure(text="Getting WHOIS information...")

            if not domain:
                messagebox.showerror("Error", "Please enter a domain")
                return

            try:
                self.start_scan()
                # Clean domain
                domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
                
                # Get both WHOIS and RDAP information
                host = socket.gethostbyname(domain)
                
                # Get domain WHOIS
                w = whois.whois(domain)
                whois_data = w.copy()
                
                # Get RDAP data
                obj = IPWhois(host)
                rdap_results = obj.lookup_rdap(depth=1)
                
                # Combine both results
                combined_data = {**whois_data, **rdap_results}
                
                # Filter out None values and process data concurrently
                filtered_data = {k: v for k, v in combined_data.items() if v is not None}
                total_items = len(filtered_data)
                processed = 0

                self.progress_label.configure(text=f"Processing 0/{total_items} WHOIS entries...")

                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_data = {
                        executor.submit(self.process_whois_data, key, value): (key, value)
                        for key, value in filtered_data.items()
                    }

                    for future in as_completed(future_to_data):
                        if not self.is_scanning:
                            executor.shutdown(wait=False)
                            break
                            
                        processed += 1
                        self.progress_label.configure(
                            text=f"Processing {processed}/{total_items} WHOIS entries..."
                        )
                        
                        try:
                            key, value = future.result()
                            if key and value:
                                self.whois_tree.insert("", "end", values=(key, value))
                        except Exception as e:
                            print(f"Error processing future: {e}")

                self.progress_bar.stop()
                self.progress_label.configure(text=f"Done! Found {len(self.whois_tree.get_children())} WHOIS entries")

            except Exception as e:
                self.progress_bar.stop()
                self.progress_label.configure(text=f"Error: {str(e)}")
                messagebox.showerror("Error", str(e))

        finally:
            self.is_scanning = False
            self.stop_button.configure(state=ctk.DISABLED)
            self.button.configure(state=ctk.NORMAL)
            self.clear_button.configure(state=ctk.NORMAL)


    def get_links(self):
        try:
            domain = self.entry.get()
            self.button.configure(state=ctk.DISABLED)
            self.clear_button.configure(state=ctk.DISABLED)
            for item in self.links_tree.get_children():
                self.links_tree.delete(item)
            self.progress_bar.start()
            self.progress_label.configure(text="Getting links...")

            if self.entry.get() == "":
                messagebox.showerror("Error", "Please enter a host")
                self.progress_bar.stop()
                self.progress_label.configure(text="Waiting for input...")
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)

            if "https://" not in domain:
                domain = f"https://{domain}"

            try:
                self.start_scan()
                s = requests.Session()
                r = s.get(domain, verify=False)
                soup = BeautifulSoup(r.content, "html.parser")
                links = soup.find_all('a', href=True)

                total_links = len(links)
                processed = 0
                self.progress_label.configure(text=f"Processing 0/{total_links} links...")

                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_link = {
                        executor.submit(self.process_link, link): link 
                        for link in links
                    }

                    for future in as_completed(future_to_link):
                        if not self.is_scanning:
                            executor.shutdown(wait=False)
                            break

                        processed += 1
                        self.progress_label.configure(text=f"Processing {processed}/{total_links} links...")
                        
                        result = future.result()
                        print(result)
                        if result:
                            self.links_tree.insert("", "end", values=(result,))

                self.progress_bar.stop()
                self.progress_label.configure(text=f"Done! Found {len(self.links_tree.get_children())} links")

            except Exception as e:
                self.progress_bar.stop()
                self.progress_label.configure(text=f"Error: {str(e)}")

        finally:
            self.is_scanning = False
            self.stop_button.configure(state=ctk.DISABLED)
            self.button.configure(state=ctk.NORMAL)
            self.clear_button.configure(state=ctk.NORMAL)



    def get_javascript_files(self):
        """Retrieve JavaScript files from a domain."""
        try:
            domain = self.entry.get()
            self.button.configure(state=ctk.DISABLED)
            self.clear_button.configure(state=ctk.DISABLED)
            for item in self.javascript_tree.get_children():
                self.javascript_tree.delete(item)
            self.progress_bar.start()
            self.progress_label.configure(text="Getting JavaScript files...")

            # Clean up domain input
            if "https://" in domain:
                domain = domain.replace("https://", "")
            if "https://www." in domain:
                domain = domain.replace("https://www.", "")
            if "http://" in domain:
                domain = domain.replace("http://", "")
            if "http://www." in domain:
                domain = domain.replace("http://www.", "")
            if domain == "":
                messagebox.showerror("Error", "Please enter a domain")
                self.progress_bar.stop()
                self.progress_label.configure(text="Waiting for input...")
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)
                return

            # Fetch the main page
            url = f"https://{domain}"
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all script tags
            scripts = [script.get("src") for script in soup.find_all("script") if script.get("src")]
            js_urls = re.findall(r'url\([\'"]?(.*?\.js)[\'"]?\)', response.text)
            for urls in js_urls:
                full_domain = urljoin(domain, urls)
                scripts.append(full_domain)
                print(full_domain)

            # Update progress label with total count
            total_scripts = len(scripts)
            processed = 0
            self.progress_label.configure(text=f"Processing 0/{total_scripts} JavaScript files...")

            # Download JavaScript files concurrently
            try:
                self.start_scan()
                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_script = {
                        executor.submit(self.download_script, url, script): script
                        for script in scripts
                    }

                    for future in as_completed(future_to_script):
                        if not self.is_scanning:
                            executor.shutdown(wait=False)
                            break
                        script = future_to_script[future]
                        try:
                            status = future.result()
                            self.javascript_tree.insert("", "end", values=(script, status))
                            processed += 1
                            self.progress_label.configure(
                                text=f"Processing {processed}/{total_scripts} JavaScript files..."
                            )
                        except Exception as e:
                            print(f"Error downloading {script}: {e}")

                self.progress_bar.stop()
                self.progress_label.configure(
                    text=f"Done! Processed {processed} JavaScript files"
                )
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)
            finally:
                self.is_scanning = False
                self.stop_button.configure(state=ctk.DISABLED)
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)



        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.configure(text="Error")
            self.button.configure(state=ctk.NORMAL)
            self.clear_button.configure(state=ctk.NORMAL)
            print(f"Main error: {e}")

    def download_script(self, base_url, script_url):
        """Download a JavaScript file and return its status."""
        try:
            if not script_url.startswith("http"):
                script_url = f"{base_url}/{script_url.lstrip('/')}"
            response = requests.get(script_url, verify=False)
            if response.status_code == 200:
                return response.status_code
            else:
                return f"{response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"


    def get_asn_info(self):
        """Get ASN information for a domain"""
        try:
            domain = self.entry.get()
            self.button.configure(state=ctk.DISABLED)
            self.clear_button.configure(state=ctk.DISABLED)
            self.progress_bar.start()
            self.progress_label.configure(text="Getting ASN info...")

            if self.entry.get() == "":
                messagebox.showerror("Error", "Please enter a host")
                self.progress_bar.stop()
                self.progress_label.configure(text="Waiting for input...")
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)

            # Get IP address from domain
            ip = socket.gethostbyname(domain)
            
            # Get ASN info
            obj = IPWhois(ip)
            results = obj.lookup_rdap(depth=1)
            
            # Extract relevant ASN information
            asn_info = {
                'ASN': results.get('asn', 'N/A'),
                'ASN Description': results.get('asn_description', 'N/A'),
                'Organization': results.get('network', {}).get('name', 'N/A'),
                'Country': results.get('asn_country_code', 'N/A')
            }

            # Clear existing items
            for item in self.asn_tree.get_children():
                self.asn_tree.delete(item)

            # Add ASN info to tree
            for prop, value in asn_info.items():
                self.asn_tree.insert("", "end", values=(prop, value))

            self.progress_bar.stop()
            self.progress_label.configure(text="ASN info retrieved successfully!")
            self.button.configure(state=ctk.NORMAL)
            self.clear_button.configure(state=ctk.NORMAL)

        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.configure(text=f"Error: {str(e)}")
            self.button.configure(state=ctk.NORMAL)
            self.clear_button.configure(state=ctk.NORMAL)


    def scan_port(self, host, port):
        """Scan a single port and identify its service."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"
                    return port, service
        except Exception as e:
            print(f"Error scanning port {port}: {e}")
        return None

    def scan_ports(self):
            """Scan ports and update both ports and services trees."""
            host = self.entry.get()
            host = socket.gethostbyname(host)

            if self.entry.get() == "":
               messagebox.showerror("Error", "Please enter a host")
               self.progress_bar.stop()
               self.progress_label.configure(text="Waiting for input...")
               self.button.configure(state=ctk.NORMAL)
               self.clear_button.configure(state=ctk.NORMAL)
               return
            elif self.startport_entry.get() == "" or self.endport_entry.get() == "":
                messagebox.showerror("Error", "Please enter a start and end port")
                self.progress_bar.stop()
                self.progress_label.configure(text="Waiting for input...")
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)
                return
            
            # Clear existing entries
            for tree in [self.ports_tree, self.services_tree]:
                for item in tree.get_children():
                    tree.delete(item)
                    
            self.button.configure(state=ctk.DISABLED)
            self.clear_button.configure(state=ctk.DISABLED)
            self.progress_bar.start()

            total_ports = int(self.endport_entry.get())
            start_port = int(self.startport_entry.get())
            if total_ports == "" or start_port == "":
                messagebox.WARNING("Don't leave the port entries blank")

            scanned = 0
            open_ports = []

            try:
                self.start_scan()
                
                with ThreadPoolExecutor(max_workers=100) as executor:
                    futures = {executor.submit(self.scan_port, host, port): port for port in range(start_port, total_ports)}
                    for future in as_completed(futures):
                        if not self.is_scanning:
                            executor.shutdown(wait=False)
                            break
                        scanned += 1
                        self.progress_label.configure(text=f"Scanning ports... ({scanned}/{total_ports-1})")
                        
                        result = future.result()
                        if result:
                            port, service = result
                            open_ports.append(port)
                            self.ports_tree.insert("", "end", values=(port,))
                            self.services_tree.insert("", "end", values=(f"{service}"))

                self.progress_bar.stop()
                self.progress_label.configure(text=f"Done! Found {len(open_ports)} open ports")
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)
            finally:
                self.is_scanning = False
                self.stop_button.configure(state=ctk.DISABLED)
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)



    def get_headers(self):
        try:
            domain = self.entry.get()
            self.button.configure(state=ctk.DISABLED)
            self.clear_button.configure(state=ctk.DISABLED)
            self.progress_bar.start()
            self.progress_label.configure(text="Getting headers...")
            if "https://" in domain:
                domain = domain.replace("https://", "")
            if "https://www." in domain:
                domain = domain.replace("https://www.", "")
            if "http://" in domain:
                domain = domain.replace("http://", "")
            if "http://www." in domain:
                domain = domain.replace("http://www.", "")
            if domain == "":
                messagebox.showerror("Error", "Please enter a domain")

            s = requests.Session()
            r = s.get(f"https://{domain}", verify=False)
            for header, value in r.headers.items():
                self.headers_tree.insert("", "end", values=(header, value))
            self.progress_bar.stop()
            self.progress_label.configure(text="Done!")
            self.button.configure(state=ctk.NORMAL)
            self.clear_button.configure(state=ctk.NORMAL)
        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.configure(text="Error")
            self.button.configure(state=ctk.NORMAL)
            self.clear_button.configure(state=ctk.NORMAL)


    def process_subdomain(self, subdomain):
        """Helper function to process individual subdomains"""
        try:
            s = requests.Session()
            r = s.get(f"https://{subdomain}", verify=False, timeout=5)
            ip = socket.gethostbyname(subdomain)
            return (subdomain, r.status_code, ip, r.headers.get("Server"))
        except Exception as e:
            print(f"Error processing {subdomain}: {e}")
            return (subdomain, "Error", str(e)[:50], "N/A")

    def get_subdomains(self):
        try:
            domain = self.entry.get()
            self.button.configure(state=ctk.DISABLED)
            self.clear_button.configure(state=ctk.DISABLED)
            for item in self.subdomain_tree.get_children():
                self.subdomain_tree.delete(item)
            self.progress_bar.start()
            self.progress_label.configure(text="Getting subdomains...")

            if "https://" in domain:
                domain = domain.replace("https://", "")
            if "https://www." in domain:
                domain = domain.replace("https://www.", "")
            if "http://" in domain:
                domain = domain.replace("http://", "")
            if "http://www." in domain:
                domain = domain.replace("http://www.", "")
            if domain == "":
                messagebox.showerror("Error", "Please enter a domain")
                self.progress_bar.stop()
                self.progress_label.configure(text="Waiting for input...")
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)
                return

            # Get subdomains list first
            cmd = f"subfinder -d {domain} -silent"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            subdomains = [line.decode().strip() for line in p.stdout if line.decode().strip()]

            # Update progress label with total count
            total_subdomains = len(subdomains)
            processed = 0
            self.progress_label.configure(text=f"Processing 0/{total_subdomains} subdomains...")

            # Process subdomains concurrently
            try:
                self.start_scan()
                with ThreadPoolExecutor(max_workers=10) as executor:
                    # Submit all tasks
                    future_to_subdomain = {
                        executor.submit(self.process_subdomain, subdomain): subdomain 
                        for subdomain in subdomains
                    }

                    # Process completed tasks as they finish
                    for future in as_completed(future_to_subdomain):
                        if not self.is_scanning:
                            executor.shutdown(wait=False)
                            break
                        try:
                            result = future.result()
                            if "Error" not in result:
                                self.subdomain_tree.insert("", "end", values=result)
                                processed += 1
                                # Update progress
                                self.progress_label.configure(
                                    text=f"Processing {processed}/{total_subdomains} subdomains..."
                                )
                            elif "Error" in result:
                                pass
                        except Exception as e:
                            print(f"Task error: {e}")

                self.progress_bar.stop()
                self.progress_label.configure(
                    text=f"Done! Found {len(self.subdomain_tree.get_children())} subdomains"
                )
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)
    
            finally:
                self.is_scanning = False
                self.stop_button.configure(state=ctk.DISABLED)
                self.button.configure(state=ctk.NORMAL)
                self.clear_button.configure(state=ctk.NORMAL)    

        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.configure(text="Error")
            self.button.configure(state=ctk.NORMAL)
            self.clear_button.configure(state=ctk.NORMAL)
            print(f"Main error: {e}")

    def clear_textbox(self):
        if self.menu.get() == "Subdomain":
            self.subdomain_tree.delete(*self.subdomain_tree.get_children())
        if self.menu.get() == "Port Scan":
            self.ports_tree.delete(*self.ports_tree.get_children())
            self.services_tree.delete(*self.services_tree.get_children())
        if self.menu.get() == "ASN":
            self.asn_tree.delete(*self.asn_tree.get_children())
        self.progress_label.configure(text="Waiting for input...")
        if self.menu.get() == "JavaScript":
            self.javascript_tree.delete(*self.javascript_tree.get_children())
        self.progress_label.configure(text="Waiting for input...")
        if self.menu.get() == "Headers":
            self.headers_tree.delete(*self.headers_tree.get_children())
            self.progress_label.configure(text="Waiting for input...")

    def subdomain_thread(self):
        threading.Thread(target=self.get_subdomains).start()
    
    def headers_thread(self):
        threading.Thread(target=self.get_headers).start()

    def ports_thread(self):
        threading.Thread(target=self.scan_ports).start()

    def asn_thread(self):
        threading.Thread(target=self.get_asn_info).start()

    def javascript_thread(self):
        threading.Thread(target=self.get_javascript_files).start()

    def links_thread(self):
        threading.Thread(target=self.get_links).start()

    def whois_thread(self):
        threading.Thread(target=self.whois).start()


if __name__ == "__main__":
    reconx = ReconX()
    reconx.window.mainloop()