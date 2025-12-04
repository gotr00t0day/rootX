import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from colorama import Fore, Style
import time
import json
import os
from script_engine import ScriptEngine  # RootX scripting engine

class ChannelWindow:
    def __init__(self, irc_client, channel_name, server):
        self.irc_client = irc_client
        self.channel_name = channel_name
        self.server = server
        self.users = set()
        self.is_closing = False
        
        # Create window
        self.window = tk.Toplevel()
        self.window.title(f"rootX - {channel_name} ({server})")
        
        
        # Create main container
        self.main_container = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left frame for chat
        self.left_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.left_frame, weight=3)
        
        # Create chat display
        #self.chat_display = scrolledtext.ScrolledText(self.left_frame, wrap=tk.WORD)
        #self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Create chat display with color tags
        self.chat_display = scrolledtext.ScrolledText(self.left_frame, wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Create input frame
        self.input_frame = ttk.Frame(self.left_frame)
        self.input_frame.pack(fill=tk.X, pady=5)
        
        # Create message input
        self.message_input = ttk.Entry(self.input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_input.bind('<Return>', self.send_message_event)
        
        # Create send button
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message_from_input)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # Create right frame for users
        self.right_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.right_frame, weight=1)
        
        # Create users label
        self.users_label = ttk.Label(self.right_frame, text="Users")
        self.users_label.pack(pady=5)
        
        # Create users listbox with scrollbars
        self.users_frame = ttk.Frame(self.right_frame)
        self.users_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbars
        self.users_scrollbar = ttk.Scrollbar(self.users_frame)
        self.users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.users_horizontal_scrollbar = ttk.Scrollbar(self.users_frame, orient=tk.HORIZONTAL)
        self.users_horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create listbox
        self.users_listbox = tk.Listbox(
            self.users_frame,
            yscrollcommand=self.users_scrollbar.set,
            xscrollcommand=self.users_horizontal_scrollbar.set,
            width=20,
            height=5
        )
        self.users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        self.users_scrollbar.config(command=self.users_listbox.yview)
        self.users_horizontal_scrollbar.config(command=self.users_listbox.xview)
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
      
        
        # Configure text tags for different message types
        self.chat_display.tag_configure('timestamp', foreground='gray')
        self.chat_display.tag_configure('join', foreground='green')
        self.chat_display.tag_configure('part', foreground='red')
        self.chat_display.tag_configure('quit', foreground='red')
        self.chat_display.tag_configure('nick', foreground='blue')
        self.chat_display.tag_configure('username', foreground='gray')
        self.chat_display.tag_configure('my_username', foreground='magenta')
        self.chat_display.tag_configure('message', foreground='white')
        self.chat_display.tag_configure('kick', foreground='red')
        self.chat_display.tag_configure('ban', foreground='red')
        self.chat_display.tag_configure('op', foreground='yellow')
        self.chat_display.tag_configure('deop', foreground='red')
        self.chat_display.tag_configure('voice', foreground='yellow')
        self.chat_display.tag_configure('devoice', foreground='red')

        # Create user menu
        self.user_menu = tk.Menu(self.window, tearoff=0)
        self.user_menu.add_command(label="Private Message", command=self.open_private_message)
        self.user_menu.add_command(label="Whois", command=self.whois_user)
        self.user_menu.add_separator()
        self.user_menu.add_command(label="OP", command=self.op_user)
        self.user_menu.add_command(label="DeOP", command=self.deop_user)
        self.user_menu.add_command(label="Voice", command=self.voice_user)
        self.user_menu.add_command(label="DeVoice", command=self.devoice_user)
        self.user_menu.add_separator()
        self.user_menu.add_command(label="Kick", command=self.kick_user)
        self.user_menu.add_command(label="Ban", command=self.ban_user)
        
        # Bind double-click instead of right-click
        self.users_listbox.bind("<Double-Button-1>", self.show_user_menu)

        # Add theme settings - MOVED TO IRCClient
        # self.current_theme = "default"
        # self.themes = { ... } # Entire themes dict removed from here

        # Create menu bar
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)

        # Create server menu
        self.server_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.server_menu.add_command(label="NickServ...", command=self.show_nickserv_dialog)
        self.server_menu.add_command(label="ChanServ...", command=self.show_chanserv_dialog)
        self.menu_bar.add_cascade(label="Server", menu=self.server_menu)
        
        # Create theme menu
        self.theme_menu = tk.Menu(self.menu_bar, tearoff=0)
        for theme_name in self.irc_client.themes.keys():
            self.theme_menu.add_command(
                label=theme_name.capitalize(),
                command=lambda t=theme_name: self.apply_theme(t)
            )
        self.menu_bar.add_cascade(label="Theme", menu=self.theme_menu)
        
        # Create Settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Theme Settings", command=self.show_theme_settings)

        self.minimized = False
        self.window.withdraw()  # Start minimized

        # Add batch update variables
        self.batch_updating = False
        self.names_buffer = set()

        # Add action color
        self.chat_display.tag_configure('action', foreground='yellow')
        
        # Apply default theme
        self.apply_theme("default")

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_topic(self, topic):
        """Update the channel topic"""
        if topic:
            self.topic_label.config(text=topic)
        else:
            self.topic_label.config(text="No topic set")

    def show_theme_settings(self):
        """Show theme settings window"""
        theme_window = tk.Toplevel(self.window)
        theme_window.title("Theme Settings")
        theme_window.geometry("300x400")
        theme_window.resizable(False, False)
        
        # Create frame for theme selection
        frame = ttk.LabelFrame(theme_window, text="Select Theme", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create theme selection variable
        theme_var = tk.StringVar(value=self.irc_client.preferences.get('theme', 'default'))
        
        # Create radio buttons for each theme
        for theme_name in self.irc_client.themes.keys():
            ttk.Radiobutton(
                frame,
                text=theme_name.capitalize(),
                value=theme_name,
                variable=theme_var,
                command=lambda t=theme_name: self.apply_theme(t)
            ).pack(anchor=tk.W, pady=5)
        
        # Create preview frame
        preview_frame = ttk.LabelFrame(theme_window, text="Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create preview text
        preview_text = scrolledtext.ScrolledText(preview_frame, height=8, width=30)
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Add sample text with different tags
        preview_text.tag_configure('timestamp', foreground='gray')
        preview_text.tag_configure('join', foreground='green')
        preview_text.tag_configure('message', foreground='white')
        preview_text.tag_configure('kick', foreground='red')
        
        preview_text.insert(tk.END, "[12:34:56] ", 'timestamp')
        preview_text.insert(tk.END, "User1 has joined\n", 'join')
        preview_text.insert(tk.END, "[12:34:57] ", 'timestamp')
        preview_text.insert(tk.END, "<User2> Hello everyone!\n", 'message')
        preview_text.insert(tk.END, "[12:34:58] ", 'timestamp')
        preview_text.insert(tk.END, "* User3 was kicked by Admin\n", 'kick')




        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create buttons frame
        buttons_frame = ttk.Frame(theme_window)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create Apply and Close buttons
        ttk.Button(
            buttons_frame,
            text="Apply",
            command=lambda: self.apply_theme(theme_var.get())
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Close",
            command=theme_window.destroy
        ).pack(side=tk.RIGHT, padx=5)


    def show_nickserv_dialog(self):
        """Show NickServ dialog for user commands"""
        dialog = tk.Toplevel(self.window)
        dialog.title("NickServ Commands")
        
        tk.Label(dialog, text="Enter NickServ Command:").pack(pady=5)
        
        command_entry = tk.Entry(dialog, width=50)
        command_entry.pack(pady=5)
        
        def send_nickserv_command():
            command = command_entry.get().strip()
            if command:
                self.irc_client.send_command(f"PRIVMSG NickServ :{command}", self.server)
                dialog.destroy()
        
        tk.Button(dialog, text="Send", command=send_nickserv_command).pack(pady=5)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

    def show_chanserv_dialog(self):
        """Show ChanServ dialog for user commands"""
        dialog = tk.Toplevel(self.window)
        dialog.title("ChanServ Commands")
        
        tk.Label(dialog, text="Enter ChanServ Command:").pack(pady=5)
        
        command_entry = tk.Entry(dialog, width=50)
        command_entry.pack(pady=5)
        
        def send_chanserv_command():
            command = command_entry.get().strip()
            if command:
                self.irc_client.send_command(f"PRIVMSG ChanServ :{command}", self.server)
                dialog.destroy()
        tk.Button(dialog, text="Send", command=send_chanserv_command).pack(pady=5)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)
        
        
    def apply_theme(self, theme_name):
        """Apply the selected theme to the window"""
        try:
            # Access themes from the main IRCClient instance
            if theme_name in self.irc_client.themes:
                theme = self.irc_client.themes[theme_name]
                # self.current_theme = theme_name # ChannelWindow doesn't need its own current_theme
                
                # Apply background and foreground colors
                self.chat_display.configure(
                    bg=theme['bg'],
                    fg=theme['fg']
                )
                
                self.users_listbox.configure(
                    bg=theme['bg'],
                    fg=theme['fg']
                )
                
                # Configure text tags with theme colors more efficiently
                tag_colors = {
                    'timestamp': 'timestamp',
                    'join': 'join',
                    'part': 'part',
                    'quit': 'quit',
                    'nick': 'nick',
                    'username': 'username',
                    'my_username': 'my_username',
                    'message': 'message',
                    'kick': 'kick',
                    'action': 'action',
                    'ban': 'ban',
                    'op': 'op',
                    'deop': 'deop',
                    'voice': 'voice',
                    'devoice': 'devoice',
                    'status': 'status',
                    'error': 'error',
                    'notice': 'notice'
                }
                
                # Apply all tag configurations in a single loop
                for tag, color_key in tag_colors.items():
                    if color_key in theme:
                        self.chat_display.tag_configure(tag, foreground=theme[color_key])
                
                # Save theme preference
                self.irc_client.save_theme_preference(theme_name)
                
                print(f"DEBUG - Applied theme: {theme_name}")
                
        except Exception as e:
            print(f"Error applying theme: {e}")
            self.chat_display.insert(tk.END, f"Error applying theme: {e}\n", 'error')


    def remove_user(self, user):
        """Remove a user from the channel and update the UI"""
        try:
            # Remove user from set (handle both with and without prefix)
            self.users.discard(user)
            self.users.discard(f"@{user}")
            self.users.discard(f"+{user}")
            
            # Update the users list
            self.update_users_list()
            
             #0\ Update users count
            self.users_label.config(text=f"Users ({len(self.users)})")
            
            print(f"DEBUG - Removed user {user} from {self.channel_name}")
            
        except Exception as e:
            print(f"Error removing user: {e}")
            self.chat_display.insert(tk.END, f"Error removing user: {e}\n", 'error')


    def kick_user(self):
        """Kick selected user from channel"""
        try:
            selected = self.users_listbox.curselection()
            if selected:
                user = self.users_listbox.get(selected[0])
                # Check if it's the current user
                current_nick = self.irc_client.connections[self.server]['nickname']
                if user == current_nick or (user.startswith(('@', '+')) and user[1:] == current_nick):
                    self.chat_display.insert(tk.END, f"You cannot kick yourself from {self.channel_name}\n", 'error')
                    return
                # Remove any prefix character
                if not user[0].isalnum():
                    user = user[1:]
                    
                # Create dialog for kick reason
                reason_dialog = tk.Toplevel(self.window)
                reason_dialog.title("Kick Reason")
                reason_dialog.geometry("300x100")
                
                # Add reason entry
                ttk.Label(reason_dialog, text="Reason:").pack(pady=5)
                reason_entry = ttk.Entry(reason_dialog, width=40)
                reason_entry.pack(pady=5)
                reason_entry.focus()
                
                def do_kick():
                    reason = reason_entry.get() or "No reason given"
                    # Send kick command
                    self.irc_client.send_command(
                        f"KICK {self.channel_name} {user} :{reason}",
                        self.server
                    )
                    
                    # Add kick message immediately (server will confirm)
                    timestamp = datetime.now().strftime("[%H:%M:%S]")
                    self.chat_display.insert(tk.END, 
                        f"{timestamp} * Attempting to kick {user} ({reason})\n", 
                        'kick')
                    self.chat_display.see(tk.END)
                    
                    print(f"DEBUG - Kicking {user} from {self.channel_name}: {reason}")
                    reason_dialog.destroy()
                
                # Add kick button
                ttk.Button(reason_dialog, text="Kick", command=do_kick).pack(pady=5)
                
                # Handle enter key
                reason_entry.bind('<Return>', lambda e: do_kick())
                
        except Exception as e:
            print(f"Error kicking user: {e}")
            self.chat_display.insert(tk.END, f"Error kicking user: {e}\n", 'error')
            
    def ban_user(self):
        """Ban selected user from channel"""
        try:
            selected = self.users_listbox.curselection()
            if selected:
                user = self.users_listbox.get(selected[0])
                # Check if it's the current user
                current_nick = self.irc_client.connections[self.server]['nickname']
                if user == current_nick or (user.startswith(('@', '+')) and user[1:] == current_nick):
                    self.chat_display.insert(tk.END, f"You cannot ban yourself from {self.channel_name}\n", 'error')
                    return
                # Remove any prefix character
                if not user[0].isalnum():
                    user = user[1:]
                    
                # Create dialog for ban options
                ban_dialog = tk.Toplevel(self.window)
                ban_dialog.title("Ban Options")
                ban_dialog.geometry("300x200")
                
                # Add ban type selection
                ttk.Label(ban_dialog, text="Ban Type:").pack(pady=5)
                ban_type = tk.StringVar(value="nick")
                ttk.Radiobutton(ban_dialog, text="Nick Ban", variable=ban_type, value="nick").pack(anchor=tk.W)
                ttk.Radiobutton(ban_dialog, text="Host Ban", variable=ban_type, value="host").pack(anchor=tk.W)
                
                # Add reason entry
                ttk.Label(ban_dialog, text="Reason:").pack(pady=5)
                reason_entry = ttk.Entry(ban_dialog, width=40)
                reason_entry.pack(pady=5)
                
                # Add kick after ban option
                kick_after = tk.BooleanVar(value=True)
                ttk.Checkbutton(ban_dialog, text="Kick after ban", variable=kick_after).pack(pady=5)
                
                def do_ban():
                    reason = reason_entry.get() or "No reason given"
                    
                    # Request whois to get host info if needed
                    if ban_type.get() == "host":
                        # Store the pending ban details
                        self.irc_client.pending_bans[user] = {
                            'channel': self.channel_name,
                            'reason': reason,
                            'kick': kick_after.get()
                        }
                        # Request WHOIS to get user's host
                        self.irc_client.send_command(f"WHOIS {user}", self.server)
                        self.chat_display.insert(tk.END, f"Requesting host information for {user}...\n", 'message')
                    else:
                        # Simple nick ban
                        self.irc_client.send_command(
                            f"MODE {self.channel_name} +b {user}!*@*",
                            self.server
                        )
                        # Add ban message
                        timestamp = datetime.now().strftime("[%H:%M:%S]")
                        self.chat_display.insert(tk.END,
                            f"{timestamp} * Set ban on {user}!*@*\n",
                            'ban')
                            
                        if kick_after.get():
                            self.irc_client.send_command(
                                f"KICK {self.channel_name} {user} :{reason}",
                                self.server
                            )
                            # Add kick message
                            self.chat_display.insert(tk.END,
                                f"{timestamp} * Attempting to kick {user} ({reason})\n",
                                'kick')
                        
                        self.chat_display.see(tk.END)
                    
                    print(f"DEBUG - Banning {user} from {self.channel_name}: {reason}")
                    ban_dialog.destroy()
                
                # Add ban button
                ttk.Button(ban_dialog, text="Ban", command=do_ban).pack(pady=10)
                
        except Exception as e:
            print(f"Error banning user: {e}")
            self.chat_display.insert(tk.END, f"Error banning user: {e}\n", 'error')

    def deop_user(self):
        """Remove operator status from selected user"""
        try:
            selected = self.users_listbox.curselection()
            if selected:
                user = self.users_listbox.get(selected[0])
                # Check if user is not an op
                if not user.startswith('@'):
                    self.chat_display.insert(tk.END, f"{user} is not an operator in {self.channel_name}\n", 'error')
                    return
                # Remove any prefix character
                if not user[0].isalnum():
                    user = user[1:]
                    
                # Send mode command to remove operator status
                self.irc_client.send_command(
                    f"MODE {self.channel_name} -o {user}",
                    self.server
                )
                print(f"DEBUG - Sending DeOP command for {user} in {self.channel_name}")
                
        except Exception as e:
            print(f"Error removing OP status: {e}")
            self.chat_display.insert(tk.END, f"Error removing OP status: {e}\n", 'error')
            
    def devoice_user(self):
        """Remove voice status from selected user"""
        try:
            selected = self.users_listbox.curselection()
            if selected:
                user = self.users_listbox.get(selected[0])
                # Check if user doesn't have voice
                if not user.startswith('+'):
                    self.chat_display.insert(tk.END, f"{user} does not have voice in {self.channel_name}\n", 'error')
                    return
                # Remove any prefix character
                if not user[0].isalnum():
                    user = user[1:]
                    
                # Send mode command to remove voice status
                self.irc_client.send_command(
                    f"MODE {self.channel_name} -v {user}",
                    self.server
                )
                print(f"DEBUG - Sending DeVoice command for {user} in {self.channel_name}")
                
        except Exception as e:
            print(f"Error removing voice status: {e}")
            self.chat_display.insert(tk.END, f"Error removing voice status: {e}\n", 'error')

    def op_user(self):
        """Give operator status to selected user"""
        try:
            selected = self.users_listbox.curselection()
            if selected:
                user = self.users_listbox.get(selected[0])
                # Check if user is already an op
                if user.startswith('@'):
                    self.chat_display.insert(tk.END, f"{user} is already an operator in {self.channel_name}\n", 'error')
                    return
                # Remove any prefix character (not just @ or +)
                if not user[0].isalnum():
                    user = user[1:]
                    
                # Send mode command to give operator status
                self.irc_client.send_command(
                    f"MODE {self.channel_name} +o {user}",
                    self.server
                )
                print(f"DEBUG - Sending OP command for {user} in {self.channel_name}")
                
        except Exception as e:
            print(f"Error giving OP status: {e}")
            self.chat_display.insert(tk.END, f"Error giving OP status: {e}\n", 'error')
            
    def voice_user(self):
        """Give voice status to selected user"""
        try:
            selected = self.users_listbox.curselection()
            if selected:
                user = self.users_listbox.get(selected[0])
                # Check if user already has voice or is an op
                if user.startswith('+'):
                    self.chat_display.insert(tk.END, f"{user} already has voice in {self.channel_name}\n", 'error')
                    return
                if user.startswith('@'):
                    self.chat_display.insert(tk.END, f"{user} is an operator and already has voice privileges in {self.channel_name}\n", 'error')
                    return
                # Check if it's the current user
                if user == self.irc_client.connections[self.server]['nickname']:
                    self.chat_display.insert(tk.END, f"You cannot give yourself voice in {self.channel_name}\n", 'error')
                    return
                # Remove any prefix character
                if not user[0].isalnum():
                    user = user[1:]
                    
                # Send mode command to give voice status
                self.irc_client.send_command(
                    f"MODE {self.channel_name} +v {user}",
                    self.server
                )
                print(f"DEBUG - Sending voice command for {user} in {self.channel_name}")
                
        except Exception as e:
            print(f"Error giving voice status: {e}")
            self.chat_display.insert(tk.END, f"Error giving voice status: {e}\n", 'error')


    def begin_batch_update(self):
        """Start a batch update of the users list"""
        self.batch_updating = True
        self.names_buffer.clear()


    def add_action(self, sender, action_text):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.chat_display.insert(tk.END, f"{timestamp} ", 'timestamp')
        self.chat_display.insert(tk.END, f"* {sender} {action_text}\n", 'action')
        self.chat_display.see(tk.END)

    def show_user_menu(self, event):
        try:
            # Get clicked item
            clicked_index = self.users_listbox.nearest(event.y)
            if clicked_index >= 0:
                # Clear previous selection and select clicked item
                self.users_listbox.selection_clear(0, tk.END)
                self.users_listbox.selection_set(clicked_index)
                
                # Get coordinates relative to the screen
                x = self.users_listbox.winfo_rootx() + event.x
                y = self.users_listbox.winfo_rooty() + event.y
                
                # Show menu at mouse position
                self.user_menu.post(x, y)
        except Exception as e:
            print(f"Error showing menu: {e}")
        
    def open_private_message(self):
        selected = self.users_listbox.curselection()
        if selected:
            user = self.users_listbox.get(selected[0])
            # Remove @ or + if present
            if user.startswith(('@', '+')):
                user = user[1:]
            self.irc_client.create_private_window(user, self.server)  # Pass the server
    
    def whois_user(self):
        selected = self.users_listbox.curselection()
        if selected:
            user = self.users_listbox.get(selected[0])
            if user.startswith(('@', '+')):
                user = user[1:]
            self.irc_client.send_command(f"WHOIS {user}")

        
    def send_message_event(self, event):
        self.send_message_from_input()
        
    def send_message_from_input(self):
        message = self.message_input.get()
        if message:
            if message.startswith('/'):
                self.irc_client.handle_command(message, self.channel_name)
            else:
                # Send the message to the server
                self.irc_client.send_command(f"PRIVMSG {self.channel_name} :{message}", self.server)
                # Add our message locally immediately
                current_nick = self.irc_client.connections[self.server]['nickname']
                self.add_message(f"{current_nick}: {message}")  # No tag needed, will use default
            self.message_input.delete(0, tk.END)
            
    def update_users_list(self):
        """Update the users listbox safely"""
        if self.is_closing:
                return
                
        try:
            # Schedule update in the GUI thread
            self.window.after(0, self._do_update_users_list)
        except Exception as e:
            print(f"Error scheduling users list update: {e}")
            
    def end_batch_update(self):
        """End a batch update and process pending updates"""
        if self.batch_updating:
            self.batch_updating = False
            if self.names_buffer:
                print(f"DEBUG - Processing batch update for {self.channel_name}")
                print(f"DEBUG - Names buffer: {self.names_buffer}")
                self.users = self.names_buffer.copy()
                self.update_users_list()
    
    def _do_update_users_list(self):
        """Performs the actual update of the users list in the GUI thread"""
        try:
            # Filter and sort users first to get the final count
            valid_users = sorted(
                [user for user in self.users 
                 if (user.startswith(('@', '+')) or user[0].isalnum()) and 
                 not any(x in user.lower() for x in ['366', 'list', 'end', 'names'])],
                key=lambda x: (not x.startswith('@'), not x.startswith('+'), x.lower())
            )

            # Update Users Count Label *before* modifying the listbox
            self.users_label.config(text=f"Users: {len(valid_users)}")

            # Now clear and repopulate the listbox
            self.users_listbox.delete(0, tk.END)
            
            # Batch insert users
            for i, user in enumerate(valid_users):
                self.users_listbox.insert(tk.END, user)
                if user.startswith('@'):
                    self.users_listbox.itemconfig(i, foreground='yellow')
                elif user.startswith('+'):
                    self.users_listbox.itemconfig(i, foreground='cyan')
                else:
                    self.users_listbox.itemconfig(i, foreground='white')
        finally:
            self.batch_updating = False

    def _add_message_safe(self, message, tag=None):
        """Internal method to safely add message in the GUI thread"""
        try:
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            
            # Prepare the message parts before inserting to minimize GUI operations
            parts = []
            parts.append(('timestamp', timestamp + " "))
            
            # Handle different types of messages
            if message.startswith('* '):  # System messages
                if 'has joined' in message:
                    parts.append(('join', message + '\n'))
                elif 'has left' in message:
                    parts.append(('part', message + '\n'))
                elif 'has quit' in message:
                    parts.append(('quit', message + '\n'))
                elif 'is now known as' in message:
                    parts.append(('nick', message + '\n'))
                else:
                    parts.append((tag or 'message', message + '\n'))
            else:
                # Regular chat messages
                if ': ' in message:
                    username, text = message.split(': ', 1)
                    # Check if the message is from the current user
                    current_nick = self.irc_client.connections[self.server]['nickname']
                    if username == current_nick:
                        parts.append(('my_username', username + ': '))
                    else:
                        parts.append(('username', username + ': '))
                    parts.append((tag or 'message', text + '\n'))
                else:
                    parts.append((tag or 'message', message + '\n'))
            
            # Insert all parts in a single operation
            for tag_name, text in parts:
                self.chat_display.insert(tk.END, text, tag_name)
            
            # Keep the display scrolled to the bottom
            self.chat_display.see(tk.END)
            
            # Only update the display after all text is inserted
            # No need to call update() every time - let Tkinter handle it naturally
            # This reduces redundant GUI updates that could cause display issues
        except Exception as e:
            print(f"Error in _add_message_safe: {e}")
        
    def add_message(self, message, tag=None):
        """Add a message to the chat display safely"""
        if not self.is_closing:
            try:
                self.window.after(0, self._add_message_safe, message, tag)
            except Exception as e:
                print(f"Error adding message: {e}")
            
    def on_closing(self):
        """Handle window closing properly"""
        try:
            if self.is_closing:
                return  # Prevent multiple closing attempts
                
            self.is_closing = True
            
            # Safely destroy widgets that might cause errors
            try:
                if hasattr(self, 'users_scrollbar'):
                    self.users_scrollbar.destroy()
            except tk.TclError:
                pass
                
            try:
                if hasattr(self, 'users_horizontal_scrollbar'):
                    self.users_horizontal_scrollbar.destroy()
            except tk.TclError:
                pass
                
            try:
                if hasattr(self, 'users_listbox'):
                    self.users_listbox.destroy()
            except tk.TclError:
                pass
            
            # Remove channel from network tree
            server_data = self.irc_client.server_nodes.get(self.server)  # Use self.server instead of current_server
            if server_data and self.channel_name in server_data['channels']:
                try:
                    # Indent this line correctly
                    self.irc_client.network_tree.delete(server_data['channels'][self.channel_name])
                except tk.TclError:
                    pass
                del server_data['channels'][self.channel_name]

            # Clean up channel windows dict
            channel_key = f"{self.server}:{self.channel_name}"
            if channel_key in self.irc_client.channel_windows:
                del self.irc_client.channel_windows[channel_key]
                
            # Send PART command if we're connected
            if self.server in self.irc_client.connections:
                try:
                    # Indent this line
                    self.irc_client.send_command(f"PART {self.channel_name}", self.server)
                except:
                    # Indent this line
                    pass
                
            # Finally destroy the window
            try:
                # Indent this line
                self.window.destroy()
            except tk.TclError:
                # Indent this line
                pass
        except Exception as e:
            print(f"Error in on_closing: {e}")

    def toggle_visibility(self):
        if self.is_closing:
            return
            
        if self.minimized:
            self.window.deiconify()
            self.minimized = False
        else:
            self.window.withdraw()
            self.minimized = True

    def update_channel_users(self, channel_key):
        """Update the users listbox for a channel if needed"""
        # Use run_in_thread to avoid blocking the GUI during user list updates
        self.run_in_thread(
            lambda: self._force_update_users_for_channel(channel_key)
        )
    
    def _force_update_users_for_channel(self, channel_key):
        """Forcefully update the users listbox for a channel without any conditions"""
        try:
            if channel_key not in self.channel_windows:
                return
                
            channel_info = self.channel_windows[channel_key]
            
            # Make sure users set exists
            if 'users' not in channel_info:
                channel_info['users'] = set()
                
            # Get the users list and sort with @ and + first
            users = sorted(list(channel_info['users']), 
                          key=lambda u: (
                              0 if u.startswith('@') else (1 if u.startswith('+') else 2),  # First sort by prefix type
                              u.lstrip('@+').lower()  # Then by nickname alphabetically
                          ))
            
            # If there are too many users, use batched updates
            if len(users) > 100:
                # Schedule batched update on the main thread
                self.window.after(0, lambda: self._batched_user_update(channel_key, users))
                return
            
            # For smaller lists, update directly
            # Make sure users_listbox exists
            if 'users_listbox' not in channel_info:
                return
                
            users_listbox = channel_info['users_listbox']
            
            # Update UI in the main thread
            def update_ui():
                # Clear the listbox
                users_listbox.delete(0, tk.END)
                
                # Batch insert users - more efficient than one at a time
                for i, user in enumerate(users):
                    users_listbox.insert(tk.END, user)
                    # Set color based on user prefix
                    if user.startswith('@'):
                        users_listbox.itemconfig(i, foreground='yellow')  # Ops
                    elif user.startswith('+'):
                        users_listbox.itemconfig(i, foreground='cyan')    # Voice
                    else:
                        users_listbox.itemconfig(i, foreground='white')   # Regular users
                
                # Make sure to update the users count label with the exact number of users displayed
                actual_count = users_listbox.size()
                if 'users_label' in channel_info:
                    channel_info['users_label'].config(text=f"Users: {actual_count}")
            
            # Schedule UI update on the main thread
            self.window.after(0, update_ui)
                
        except Exception as e:
            print(f"Error updating users list: {e}")
            import traceback
            traceback.print_exc()
    
    def _batched_user_update(self, channel_key, users=None):
        """Update users listbox in batches to prevent UI freezing
        
        Args:
            channel_key: The channel key to update
            users: Optional pre-sorted user list 
        """
        try:
            if channel_key not in self.channel_windows:
                return
                
            channel_info = self.channel_windows[channel_key]
            
            # Get users set if not provided
            if users is None:
                users = sorted(list(channel_info.get('users', set())), # Use .get for safety 
                             key=lambda u: (
                                 0 if u.startswith('@') else (1 if u.startswith('+') else 2),
                                 u.lstrip('@+').lower()
                             ))
            
            # Make sure users_listbox exists
            if 'users_listbox' not in channel_info:
                return
                
            users_listbox = channel_info['users_listbox']
            
            # Clear the listbox first
            users_listbox.delete(0, tk.END)
            
            # Store state for batched processing
            batch_state = {
                'users': users,
                'current_index': 0,
                'batch_size': 50,  # Process 50 users at a time
                'total_inserted': 0  # Keep track of actual inserted users
            }
            
            # Define function to process one batch
            def process_batch():
                # Check if channel info still exists (window might close during batch)
                if channel_key not in self.channel_windows:
                    return 
                current_channel_info = self.channel_windows[channel_key]

                if batch_state['current_index'] >= len(batch_state['users']):
                    # Done - update the count with the ACTUAL number of users in the listbox
                    if 'users_label' in current_channel_info:
                        try:
                            # Make sure listbox still exists before getting size
                            if users_listbox.winfo_exists():
                                actual_count = users_listbox.size()
                                current_channel_info['users_label'].config(text=f"Users: {actual_count}")
                        except tk.TclError:
                             # Handle potential error if widget is destroyed during update
                             pass
                    return
                
                # Process next batch
                start_idx = batch_state['current_index']
                end_idx = min(start_idx + batch_state['batch_size'], len(batch_state['users']))
                
                # Check if listbox still exists before inserting
                if not users_listbox.winfo_exists():
                    return 

                try:
                    for i in range(start_idx, end_idx):
                        user = batch_state['users'][i]
                        users_listbox.insert(tk.END, user)
                        idx = users_listbox.size() - 1
                        batch_state['total_inserted'] += 1
                        
                        # Set color based on user prefix
                        if user.startswith('@'):
                            users_listbox.itemconfig(idx, foreground='yellow')  # Ops
                        elif user.startswith('+'):
                            users_listbox.itemconfig(idx, foreground='cyan')    # Voice
                        else:
                            users_listbox.itemconfig(idx, foreground='white')   # Regular users
                    
                    # Remove the label update from inside the loop
                    # if 'users_label' in current_channel_info:
                    #     current_channel_info['users_label'].config(text=f"Users: {batch_state['total_inserted']}")
                    
                    # Update index for next batch
                    batch_state['current_index'] = end_idx
                    
                    # Schedule next batch - use short delay to allow UI to breathe
                    self.window.after(10, process_batch)
                except tk.TclError:
                    # Handle error if listbox is destroyed during insertion
                    print(f"Warning: Listbox for {channel_key} destroyed during batched update.")
                    return

            # Start batch processing
            self.window.after(0, process_batch)
            
        except Exception as e:
            print(f"Error in batched user update: {e}")
            import traceback
            traceback.print_exc()

    # Keep the old method name for now, but make it specific to double-click PM
    def show_user_menu(self, event):
        # This method is now primarily for the old double-click binding, 
        # which we might re-purpose or remove later.
        # For now, it can delegate or simply pass.
        pass # Or potentially call open_private_message if that's the desired double-click action

class PrivateWindow:
    def __init__(self, irc_client, username, server):
        self.irc_client = irc_client
        self.username = username
        self.server = server  # Store server information
        self.pm_key = f"{server}:{username}"  # Create a unique key for this PM window
        self.is_closing = False
        
        # Create window
        self.window = tk.Toplevel()
        self.window.title(f"Private Message - {username} ({server})")
        
        self.window.geometry("600x400")
        
        # Create chat display
        self.chat_display = scrolledtext.ScrolledText(self.window, wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags
        self.chat_display.tag_configure('timestamp', foreground='gray')
        self.chat_display.tag_configure('username', foreground='gray')
        self.chat_display.tag_configure('my_username', foreground='magenta')
        self.chat_display.tag_configure('message', foreground='white')
        
        # Create input frame
        self.input_frame = ttk.Frame(self.window)
        self.input_frame.pack(fill=tk.X, pady=5)
        
        # Create message input
        self.message_input = ttk.Entry(self.input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_input.bind('<Return>', self.send_message)
        
        # Create send button
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Add to network tree instead of window list
        self.irc_client.add_pm_node(username, server)

        # Add action color
        self.chat_display.tag_configure('action', foreground='yellow')


    def add_action(self, sender, action_text):
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            self.chat_display.insert(tk.END, f"{timestamp} ", 'timestamp')
            self.chat_display.insert(tk.END, f"* {sender} {action_text}\n", 'action')
            self.chat_display.see(tk.END)

    def on_closing(self):
        """Handle private window closing properly"""
        try:
            if self.is_closing:
                return  # Prevent multiple closing attempts
                
            self.is_closing = True
            
            # Remove PM node from correct server's tree section (thread-safe)
            server_data = self.irc_client.server_nodes.get(self.server)
            if server_data and self.username in server_data['private_msgs']:
                def remove_tree_node():
                    try:
                        self.irc_client.network_tree.delete(server_data['private_msgs'][self.username])
                        del server_data['private_msgs'][self.username]
                        print(f"DEBUG: Successfully removed PM tree node for {self.username}")
                    except tk.TclError as e:
                        print(f"DEBUG: Error removing PM tree node: {e}")
                try:
                    self.irc_client.window.after(0, remove_tree_node)
                except:
                    # Fallback if window is being destroyed
                    try:
                        self.irc_client.network_tree.delete(server_data['private_msgs'][self.username])
                        del server_data['private_msgs'][self.username]
                    except:
                        pass
                    
            # Clean up private windows dict using the PM key
            if self.pm_key in self.irc_client.private_windows:
                del self.irc_client.private_windows[self.pm_key]
                    
            # Safely destroy widgets
            try:
                # Indent this line
                if hasattr(self, 'chat_display'):
                    self.chat_display.destroy()
            except tk.TclError:
                # Indent this line
                pass
                    
            try:
                # Indent this line
                if hasattr(self, 'message_input'):
                    self.message_input.destroy()
            except tk.TclError:
                # Indent this line
                pass
                    
            try:
                # Indent this line
                if hasattr(self, 'send_button'):
                    self.send_button.destroy()
            except tk.TclError:
                # Indent this line
                pass
                    
            # Finally destroy window
            try:
                # Indent this line
                self.window.destroy()
            except tk.TclError:
                # Indent this line
                pass
        except Exception as e:
            print(f"Error in PM window on_closing: {e}")
        
    def send_message(self, event=None):
        if self.is_closing:
            return
            
        message = self.message_input.get()
        if message:
            # Pass the server along with the message
            self.irc_client.send_private_message(self.username, message, self.server)
            current_nick = self.irc_client.connections[self.server]['nickname']
            self.add_message(f"{current_nick}: {message}")
            self.message_input.delete(0, tk.END)
            
    def add_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.chat_display.insert(tk.END, timestamp + " ", 'timestamp')
        
        if ': ' in message:
            username, text = message.split(': ', 1)
            current_nick = self.irc_client.connections[self.server]['nickname']
            if username == current_nick:
                self.chat_display.insert(tk.END, username + ': ', 'my_username')
            else:
                self.chat_display.insert(tk.END, username + ': ', 'username')
            self.chat_display.insert(tk.END, text + '\n', 'message')
        else:
            self.chat_display.insert(tk.END, message + '\n', 'message')
            
        self.chat_display.see(tk.END)
        

class IRCClient:
    CONFIG_FILE = "network_config.json"

    def __init__(self, master, server=None, port=6667, nickname="PythonUser"):
        # Client version
        self.version = "rootX IRC Client v2"
        
        self.master = master
        self.connections = {}  # Dictionary to store connections by server name
        self.current_server = None  # Track which server is currently active
        self.servers = []  # List of servers to connect to
        
        # Store default settings
        self.default_nickname = nickname
        
        # Initialize status_display to None to prevent exceptions
        self.status_display = None
        
        # Preferences dictionary
        self.preferences = {
            'theme': 'default',
            'show_tabs': False  # Default to hidden tabs
        }
        
        # --- Define Themes dictionary here ---
        self.themes = {
            "default": {
                'bg': 'black',
                'fg': 'white',
                'list_bg': 'black', # Specific background for listbox
                'list_fg': 'white',
                'select_bg': '#333333', # Selection background
                'timestamp': 'gray',
                'join': 'green',
                'part': 'red',
                'quit': 'red',
                'nick': 'blue',
                'username': 'gray',
                'my_username': 'magenta',
                'message': 'white',
                'kick': 'red',
                'action': 'yellow',
                'ban': 'red',
                'op': 'yellow',
                'deop': 'red',
                'voice': 'yellow',
                'devoice': 'red',
                'status': 'cyan',
                'error': 'orange',
                'notice': 'blue'
            },
            "dark": {
                'bg': '#1a1a1a',
                'fg': '#e6e6e6',
                'list_bg': '#2b2b2b', 
                'list_fg': '#e6e6e6',
                'select_bg': '#4a4a4a',
                'timestamp': '#808080',
                'join': '#00cc00',
                'part': '#ff3333',
                'quit': '#ff3333',
                'nick': '#3399ff',
                'username': '#808080',
                'my_username': '#ff66ff',
                'message': '#e6e6e6',
                'kick': '#ff3333',
                'action': '#ffff66',
                'ban': '#ff3333',
                'op': '#ffff66',
                'deop': '#ff3333',
                'voice': '#33ccff',
                'devoice': '#ff3333',
                'status': '#66ffff',
                'error': '#ff9933',
                'notice': '#66ccff'
            },
            "light": {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'list_bg': '#ffffff', 
                'list_fg': '#000000',
                'select_bg': '#cceeff',
                'timestamp': '#666666',
                'join': '#008000',
                'part': '#cc0000',
                'quit': '#cc0000',
                'nick': '#0066cc',
                'username': '#666666',
                'my_username': '#cc00cc',
                'message': '#000000',
                'kick': '#cc0000',
                'action': '#808000',
                'ban': '#cc0000',
                'op': '#ff8000',
                'deop': '#cc0000',
                'voice': '#008080',
                'devoice': '#cc0000',
                'status': '#008080',
                'error': '#ff0000',
                'notice': '#0000ff'
            },
            "matrix": {
                'bg': 'black',
                'fg': '#00ff00',
                'list_bg': '#001a00', 
                'list_fg': '#00ff00',
                'select_bg': '#004d00',
                'timestamp': '#006600',
                'join': '#00ff00',
                'part': '#008800',
                'quit': '#008800',
                'nick': '#00cc00',
                'username': '#006600',
                'my_username': '#00ff00',
                'message': '#00ff00',
                'kick': '#008800',
                'action': '#00aa00',
                'ban': '#008800',
                'op': '#33ff33',
                'deop': '#008800',
                'voice': '#33ff33',
                'devoice': '#008800',
                'status': '#66ff66',
                'error': '#ffff00',
                'notice': '#99ff99'
            }
        }

        # Thread synchronization
        self.lock = threading.Lock()
        self.running = True
        self.disconnecting = False
        
        # Windows dictionary - keyed by unique identifiers
        self.channel_windows = {}  # Use server:channel as key
        self.private_windows = {}  # Use server:nickname as key
        self.status_window = None
        
        # Tab-related variables
        self.notebook = None  # Notebook widget for tabs
        self.tabs = {}  # Dictionary of tab frames keyed by tab_id
        self.current_tab = None  # Currently active tab id
        self.tabs_visible = self.preferences.get('show_tabs', False)  # Tab visibility state
        
        # Pending connection attempts
        self.connection_attempts = {}
        self.reconnect_attempts = {}
        self.max_reconnect_attempts = 3
        
        # Pending operations
        self.pending_bans = {}  # Track pending ban operations by target_nick
        
        # Create main window
        self.window = master
        self.window.title("RootXIRC")
        
        # Create main container
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create main paned window to separate sidebar and content
        self.main_paned = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar frame for server/channel tree
        self.sidebar_frame = ttk.Frame(self.main_paned, width=200)
        self.main_paned.add(self.sidebar_frame, weight=1)
        
        # Create network tree inside a frame with scrollbar
        self.tree_frame = ttk.Frame(self.sidebar_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(self.tree_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the network tree
        self.network_tree = ttk.Treeview(
            self.tree_frame, 
            selectmode='browse',
            yscrollcommand=tree_scrollbar.set,
            show='tree',
            height=20
        )
        self.network_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.config(command=self.network_tree.yview)
        
        # Bind events for tree items
        self.network_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.network_tree.bind('<Double-1>', self.on_tree_double_click)
        self.network_tree.bind('<Button-3>', self.show_tree_menu)
        
        # Create content frame for notebook/tabs
        self.content_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.content_frame, weight=3)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Apply tab visibility setting
        if not self.tabs_visible:
            style = ttk.Style()
            style.layout('TNotebook.Tab', [])  # Empty layout removes the tabs
        
        # State for tree nodes
        self.server_nodes = {}  # Dictionary to track server nodes and their channels
        
        # Create context menu for tree
        self.tree_menu = tk.Menu(self.window, tearoff=0)
        self.tree_menu.add_command(label="Connect", command=self.connect_selected)
        self.tree_menu.add_command(label="Disconnect", command=self.disconnect_selected)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Join Channel", command=self.show_join_dialog)
        self.tree_menu.add_command(label="Close Tab", command=self.close_selected)
        
        # Create context menu specifically for channel nodes in the tree
        self.channel_tree_menu = tk.Menu(self.window, tearoff=0)
        self.channel_tree_menu.add_command(label="Part Channel", command=self.part_selected_channel_from_menu)
        
        # Create context menu specifically for PM nodes in the tree
        self.pm_tree_menu = tk.Menu(self.window, tearoff=0)
        self.pm_tree_menu.add_command(label="Close PM", command=self.close_selected_pm_from_menu)
        
        # Load icons for tree - Create empty PhotoImage objects as fallbacks
        self.server_icon = tk.PhotoImage(width=1, height=1)
        self.channel_icon = tk.PhotoImage(width=1, height=1)
        self.pm_icon = tk.PhotoImage(width=1, height=1)
        
        try:
            # Try to load icons if available
            from PIL import Image, ImageTk
            try:
                server_img = Image.open("icons/server.png").resize((16, 16))
                channel_img = Image.open("icons/channel.png").resize((16, 16))
                pm_img = Image.open("icons/pm.png").resize((16, 16))
                
                self.server_icon = ImageTk.PhotoImage(server_img)
                self.channel_icon = ImageTk.PhotoImage(channel_img)
                self.pm_icon = ImageTk.PhotoImage(pm_img)
            except FileNotFoundError as e:
                print(f"Error loading icons: {e}")
                print("Using default empty icons")
        except ImportError:
            print("PIL not available, using default empty icons")
        
        # Create main menu
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Connect to Server...", command=self.show_connect_dialog)
        self.file_menu.add_command(label="Disconnect", command=self.show_disconnect_dialog)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_exit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Channel menu
        self.channel_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.channel_menu.add_command(label="Join Channel...", command=self.show_join_dialog)
        self.channel_menu.add_command(label="Channel List", command=self.show_channel_list)
        self.menu_bar.add_cascade(label="Channel", menu=self.channel_menu)
        
        # Server menu
        self.server_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.server_menu.add_command(label="Server Settings", command=self.show_server_settings)
        self.menu_bar.add_cascade(label="Server", menu=self.server_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about_dialog)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        # View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Show/Hide Tabs", command=self.toggle_tabs)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        
        # Store channel list windows
        self.channel_list_windows = {}

        # Create status bar
        self.status_bar = ttk.Label(self.window, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Thread for receiving data
        self.receive_threads = {}
        
        # Create status window first so we can show messages
        self.create_status_window()
        
        # Initialize scripting engine after window is ready
        self.script_engine = ScriptEngine(self)
        self.add_status_message("Scripting engine initialized")
        
        # Load all scripts from scripts directory
        script_results = self.script_engine.load_all_scripts()
        
        # Display loaded scripts summary
        events = self.script_engine.list_events()
        aliases = self.script_engine.list_aliases()
        
        self.add_status_message("----------------------------------------")
        if not self.script_engine.loaded_scripts:
             self.add_status_message("Scripting Engine: No scripts loaded (checked scripts/ folder)")
        else:
            self.add_status_message(f"Scripting Engine: {len(self.script_engine.loaded_scripts)} script(s) loaded")
            for name in self.script_engine.loaded_scripts:
                self.add_status_message(f"  + {name}")
                
        if events:
            self.add_status_message(f"  + {len(events)} event handlers registered")
        if aliases:
            self.add_status_message(f"  + {len(aliases)} aliases registered")
        self.add_status_message("----------------------------------------")
        
        # Connect to default server if provided
        if server:
            self.connect_to_server(server, port, nickname)
            
        # Reference to the network list window (only one instance)
        self.network_list_window = None
            
    def on_tab_changed(self, event):
        """Handle when user switches between tabs"""
        selected_tab = self.notebook.select()
        if not selected_tab:
            return
            
        # Use run_with_busy_cursor to indicate processing during tab change
        def tab_change_handler():
            # Find the tab id (server:channel or status)
            tab_id = None
            for key, frame in self.tabs.items():
                if str(frame) == str(selected_tab):
                    tab_id = key
                    break
                    
            if tab_id:
                self.current_tab = tab_id
                # If this is a channel tab, update current server and channel context
                if ':' in tab_id and tab_id != 'status':
                    server, channel = tab_id.split(':', 1)
                    self.current_server = server
                    
                    # Update tree selection to match the current tab
                    for server_id, server_data in self.server_nodes.items():
                        if server_id == server:
                            for chan, chan_id in server_data['channels'].items():
                                if chan == channel:
                                    self.network_tree.selection_set(chan_id)
                                    break
                                    
                # Schedule user list update for channels with a delay to allow UI to refresh
                if ':' in tab_id and tab_id in self.channel_windows:
                    # Don't block the UI - schedule user list update after a short delay
                    self.window.after(200, lambda: self.run_in_thread(
                        lambda: self._force_update_users_for_channel(tab_id)
                    ))
        
        # Run the tab change logic with busy cursor
        self.run_with_busy_cursor(tab_change_handler)
        
    def show_channel_list(self):
        """Show channel list dialog"""
        if not self.current_server:
            self.add_status_message("Not connected to any server", 'error')
            return

        server = self.current_server

        # Check if window already exists for this server
        if server in self.channel_list_windows:
            try:
                # Bring existing window to front
                existing_window = self.channel_list_windows[server]
                if existing_window.window.winfo_exists():
                    existing_window.window.lift()
                    existing_window.window.focus_force()
                    return # Window already open
                else:
                    # Window was closed unexpectedly, remove reference
                    del self.channel_list_windows[server]
            except tk.TclError:
                # Window likely destroyed, remove reference
                del self.channel_list_windows[server]

        # Create new window
        self.add_status_message(f"Opening channel list window for {server}", 'status')
        new_window = ChannelListWindow(self, server)
        self.channel_list_windows[server] = new_window

        # No longer need to send LIST here, the window does it
        # self.add_status_message(f"Requesting channel list from {self.current_server}")
        # self.send_command("LIST", self.current_server)

    def on_tree_double_click(self, event):
        """Handle double-click on tree items. 
           - Channel nodes: Show context menu.
           - Other nodes: Switch to the corresponding tab.
        """
        item = self.network_tree.identify_row(event.y) # More reliable way to get item under cursor
        if not item:
            return # Clicked on empty space

        self.network_tree.selection_set(item) # Select the item
        item_tags = self.network_tree.item(item)['tags']
        item_text = self.network_tree.item(item)['text']
        
        if 'channel' in item_tags:
            # Show the specific channel context menu on double-click
            self.channel_tree_menu.tk_popup(event.x_root, event.y_root)
            return "break" # Prevent potential interference with other bindings
        
        elif 'server' in item_tags:
            # For server nodes, select the status tab and set current server
            self.select_tab('status')
            self.current_server = item_text
        
        elif 'pm' in item_tags:
            # Show the PM context menu on double-click
            self.pm_tree_menu.tk_popup(event.x_root, event.y_root)
            return "break"  # Prevent potential interference with other bindings

    def part_selected_channel_from_menu(self):
        """Handles the 'Part Channel' action from the channel tree menu."""
        selection = self.network_tree.selection()
        if not selection:
            self.add_status_message("No channel selected in tree.", 'error')
            return
            
        item = selection[0]
        # Verify it's actually a channel node that's selected
        if 'channel' not in self.network_tree.item(item)['tags']:
            # This shouldn't happen if the menu is shown correctly, but check anyway
            self.add_status_message("Selected item is not a channel.", 'error')
            return
            
        channel = self.network_tree.item(item)['text']
        parent = self.network_tree.parent(item)
        server = self.network_tree.item(parent)['text']
        
        # Use the existing robust method for closing/parting
        self.close_channel_tab(channel, server)
    
    def close_selected_pm_from_menu(self):
        """Handles the 'Close PM' action from the PM tree menu."""
        selection = self.network_tree.selection()
        if not selection:
            self.add_status_message("No PM selected in tree.", 'error')
            return
            
        item = selection[0]
        # Verify it's actually a PM node that's selected
        if 'pm' not in self.network_tree.item(item)['tags']:
            self.add_status_message("Selected item is not a PM.", 'error')
            return
            
        # Extract username from the PM node text (format: "PM: username")
        item_text = self.network_tree.item(item)['text']
        username = item_text.replace("PM: ", "")
        
        # Get the server from the parent node
        parent = self.network_tree.parent(item)
        server = self.network_tree.item(parent)['text']
        
        # Create the PM key and close the tab
        pm_key = f"{server}:{username}"
        print(f"DEBUG: Closing PM - username={username}, server={server}, pm_key={pm_key}")
        print(f"DEBUG: PM key in private_windows? {pm_key in self.private_windows}")
        
        if pm_key in self.private_windows:
            pm_info = self.private_windows[pm_key]
            tab_id = f"pm:{username}"
            
            # Remove the tab from notebook
            if tab_id in self.tabs:
                try:
                    tab = self.tabs[tab_id]
                    self.notebook.forget(tab)
                    del self.tabs[tab_id]
                    print(f"DEBUG: Removed PM tab for {username}")
                except Exception as e:
                    print(f"DEBUG: Error removing PM tab: {e}")
            
            # Remove from private_windows
            del self.private_windows[pm_key]
            
            # Remove PM node from tree
            server_data = self.server_nodes.get(server)
            if server_data and username in server_data['private_msgs']:
                try:
                    self.network_tree.delete(server_data['private_msgs'][username])
                    del server_data['private_msgs'][username]
                    print(f"DEBUG: Removed PM tree node for {username}")
                except tk.TclError as e:
                    print(f"DEBUG: Error removing PM tree node: {e}")
            
            self.add_status_message(f"Closed PM with {username} on {server}")
        else:
            # If the PM doesn't exist, just remove the tree node directly
            print(f"DEBUG: PM not found, removing tree node directly")
            server_data = self.server_nodes.get(server)
            if server_data and username in server_data['private_msgs']:
                try:
                    self.network_tree.delete(server_data['private_msgs'][username])
                    del server_data['private_msgs'][username]
                    self.add_status_message(f"Removed PM node for {username} on {server}")
                except tk.TclError as e:
                    self.add_status_message(f"Error removing PM node: {e}", 'error')

    def select_tab(self, tab_id):
        """Select and activate a tab in the notebook
        
        Args:
            tab_id: The identifier of the tab to select (e.g., 'status', 'server_name', 'channel_name')
        """
        if tab_id in self.tabs:
            tab_index = self.notebook.index(self.tabs[tab_id])
            self.notebook.select(tab_index)
            self.current_tab = tab_id
            
            # Set focus to the appropriate input field
            if tab_id == 'status':
                self.command_input.focus_set()
            elif tab_id.startswith('#') or tab_id.startswith('pm:'):
                # Channel or PM tabs
                if hasattr(self, f'input_{tab_id.replace(":", "_")}'):
                    getattr(self, f'input_{tab_id.replace(":", "_")}').focus_set()
            else:
                # Server tabs
                if hasattr(self, f'input_{tab_id}'):
                    getattr(self, f'input_{tab_id}').focus_set()
                    
            # Update the tree selection to match the tab
            self.update_tree_selection(tab_id)
    
    def update_tree_selection(self, tab_id):
        """Update the tree selection to match the active tab
        
        Args:
            tab_id: The identifier of the current tab
        """
        for item in self.network_tree.get_children():
            # Check if this is a server item
            if tab_id == self.network_tree.item(item, 'text'):
                self.network_tree.selection_set(item)
                return
                
            # Check children for channels/PMs
            for child in self.network_tree.get_children(item):
                if tab_id == self.network_tree.item(child, 'text'):
                    self.network_tree.selection_set(child)
                    return
                    
        # If no match found and it's the status tab
        if tab_id == 'status':
            # Clear selection and select the first item (status)
            self.network_tree.selection_set('')
            if self.network_tree.get_children():
                self.network_tree.selection_set(self.network_tree.get_children()[0])
                
    def on_tab_change(self, event):
        """Handle tab change events"""
        selected_tab = self.notebook.select()
        if selected_tab:
            # Find the tab_id for this tab widget
            for tab_id, tab_widget in self.tabs.items():
                if str(tab_widget) == str(selected_tab):
                    self.current_tab = tab_id
                    self.update_tree_selection(tab_id)
                    break
        
    def save_theme_preference(self, theme_name):
        """Save theme preference"""
        self.preferences['theme'] = theme_name
        # You could also save to a config file here if desired
        
    def get_theme_preference(self):
        """Get saved theme preference"""
        return self.preferences.get('theme', 'default')

    def quit_server(self, server, quit_message="Leaving"):
        """Quit from a server and clean up"""
        if server in self.connections:
            try:
                # Try to send a QUIT message before disconnecting
                try:
                    self.send_command(f"QUIT :{quit_message}", server)
                except:
                    pass
                
                # Use the improved disconnect method to handle the rest
                self.disconnect_from_server(server)
                
            except Exception as e:
                self.add_status_message(f"Error quitting {server}: {e}")
                # Try to disconnect anyway even if there was an error
                try:
                    self.disconnect_from_server(server)
                except:
                    pass

    def remove_server_node(self, server):
        """Remove a server node and all its child nodes from the tree"""
        if server in self.server_nodes:
            server_data = self.server_nodes[server]
            
            # Use close_channel_tab for proper cleanup
            for channel in list(server_data.get('channels', {}).keys()):
                self.close_channel_tab(channel, server)
            
            # Use close_pm_tab for proper cleanup
            for username in list(server_data.get('private_msgs', {}).keys()):
                self.close_pm_tab(username, server)
            
            # Delete the server node from the tree
            try:
                self.network_tree.delete(server_data['node'])
            except Exception as e:
                print(f"Error deleting server node: {e}")

            # Remove from server_nodes dictionary
            del self.server_nodes[server]
                
            # If this was the current server, set current_server to None
            if self.current_server == server:
                self.current_server = None
                if self.connections:
                    self.current_server = next(iter(self.connections.keys()))

    def add_server_node(self, server):
        """Add a server node to the tree"""
        if server not in self.server_nodes:
            server_node = self.network_tree.insert(
                '', 'end', 
                text=server,
                tags=('server',),
                image=self.server_icon
            )
            self.server_nodes[server] = {
                'node': server_node,
                'channels': {},
                'private_msgs': {}
            }
            self.current_server = server
            return server_node
        return self.server_nodes[server]['node']

    def add_channel_node(self, channel, server):
        """Add a channel under the specified server"""
        if server and server in self.server_nodes:
            server_data = self.server_nodes[server]
            if channel not in server_data['channels']:
                channel_node = self.network_tree.insert(
                    server_data['node'], 'end',
                    text=channel,
                    tags=('channel',),
                    image=self.channel_icon
                )
                server_data['channels'][channel] = channel_node
                return channel_node
        return None

    def add_pm_node(self, username, server):
        """Add a private message node to the network tree under the correct server"""
        if not server or server not in self.server_nodes:
            # Server node doesn't exist, create it first
            server_node = self.add_server_node(server)
        
        server_data = self.server_nodes[server]
        if username not in server_data['private_msgs']:
            pm_node = self.network_tree.insert(
                server_data['node'], 'end',
                text=f"PM: {username}",
                tags=('pm',),
                image=self.pm_icon
            )
            server_data['private_msgs'][username] = pm_node
            return pm_node
        return server_data['private_msgs'][username]

    def remove_channel_node(self, channel, server):
        """Remove a channel node from the treeview."""
        try:
            if server in self.server_nodes:
                server_data = self.server_nodes[server]
                if channel in server_data['channels']:
                    # Get the channel node ID and delete it
                    channel_node = server_data['channels'][channel]
                    self.network_tree.delete(channel_node)
                    # Remove from the channels dictionary
                    del server_data['channels'][channel]
        except Exception as e:
            self.add_status_message(f"Error removing channel node: {e}", "error")
            traceback.print_exc()

    def close_channel_tab(self, channel, server):
        """Close a channel tab and clean up resources"""
        try:
            channel_key = f"{server}:{channel}"
            print(f"Closing channel tab for {channel_key}")
            
            # Remove the channel node from the tree
            self.remove_channel_node(channel, server)
            
            # If we're still connected, send PART command
            if server in self.connections and self.connections[server].get('socket'):
                try:
                    self.send_command(f"PART {channel}", server)
                except Exception as e:
                    print(f"Error sending PART command: {e}")
            
            # Remove the tab
            if channel_key in self.channel_windows:
                channel_info = self.channel_windows[channel_key]
                
                # Check if 'tab' exists in the dictionary
                if 'tab' in channel_info:
                    tab_id = channel_info['tab']
                    if tab_id:
                        # Remove the tab from the notebook
                        try:
                            self.notebook.forget(tab_id)
                            print(f"Removed tab for {channel_key}")
                        except Exception as e:
                            print(f"Error removing tab for {channel_key}: {e}")
                
                # Remove from channel_windows dictionary
                del self.channel_windows[channel_key]
                print(f"Removed {channel_key} from channel_windows dictionary")
                
                # If no more tabs, select the status tab
                if self.notebook.index("end") == 1:  # Only status tab remains
                    self.notebook.select(0)  # Select the status tab
        except Exception as e:
            self.add_status_message(f"Error closing channel tab {channel} on {server}: {e}")
            traceback.print_exc()

    def remove_pm_node(self, username):
        """Remove a private message node"""
        if self.current_server and self.current_server in self.server_nodes:
            server_data = self.server_nodes[self.current_server]
            if username in server_data['private_msgs']:
                self.network_tree.delete(server_data['private_msgs'][username])
                del server_data['private_msgs'][username]

    def toggle_window_from_tree(self, event):
        """Handle double-click on tree items"""
        item = self.network_tree.selection()[0]
        item_tags = self.network_tree.item(item)['tags']
        item_text = self.network_tree.item(item)['text']

        if 'channel' in item_tags:
            # Get the server from the parent item
            parent = self.network_tree.parent(item)
            server = self.network_tree.item(parent)['text']
            channel_key = f"{server}:{item_text}"
            
            if channel_key in self.channel_windows:
                self.channel_windows[channel_key].toggle_visibility()
        elif 'pm' in item_tags:
            username = item_text.replace('PM: ', '')
            if username in self.private_windows:
                self.private_windows[username].toggle_visibility()

    def send_ctcp_request(self, target, request, server=None):
        """Send a CTCP request"""
        self.send_command(f"PRIVMSG {target} :\x01{request}\x01", server)

    def send_ctcp_reply(self, target, reply):
        """Send a CTCP reply"""
        self.send_command(f"NOTICE {target} :\x01{reply}\x01")

    def handle_ctcp(self, sender, target, command):
        """Handle CTCP requests and actions"""
        command = command.strip('\x01')  # Remove CTCP markers
        parts = command.split(maxsplit=1)
        ctcp_command = parts[0].upper()
        params = parts[1] if len(parts) > 1 else ''
        
        if ctcp_command == 'VERSION':
            self.send_ctcp_reply(sender, f"VERSION {self.version}")
        elif ctcp_command == 'TIME':
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.send_ctcp_reply(sender, f"TIME {current_time}")
        elif ctcp_command == 'PING':
            self.send_ctcp_reply(sender, f"PING {params}")
        elif ctcp_command == 'SOURCE':
            self.send_ctcp_reply(sender, "SOURCE https://github.com/yourusername/rootX")
        elif ctcp_command == 'CLIENTINFO':
            supported_commands = "VERSION TIME PING SOURCE CLIENTINFO ACTION"
            self.send_ctcp_reply(sender, f"CLIENTINFO {supported_commands}")
        elif ctcp_command == 'ACTION':
            # Handle /me actions
            if target in self.channel_windows:
                self.channel_windows[target].add_action(sender, params)
            elif target == self.nickname and sender in self.private_windows:
                self.private_windows[sender].add_action(sender, params)


    def create_private_window(self, username, server):
        """Create a private message window as a tab in the notebook"""
        pm_key = f"{server}:{username}"
        
        if pm_key not in self.private_windows:
            # Create a new tab frame in the notebook
            pm_tab = ttk.Frame(self.notebook)
            
            # Create chat display
            chat_display = scrolledtext.ScrolledText(pm_tab, wrap=tk.WORD)
            chat_display.pack(fill=tk.BOTH, expand=True)
            
            # Configure text tags
            chat_display.tag_configure('timestamp', foreground='gray')
            chat_display.tag_configure('username', foreground='gray')
            chat_display.tag_configure('my_username', foreground='magenta')
            chat_display.tag_configure('message', foreground='white')
            chat_display.tag_configure('action', foreground='purple')
            
            # Create input frame
            input_frame = ttk.Frame(pm_tab)
            input_frame.pack(fill=tk.X, pady=5)
            
            # Create message input
            message_input = ttk.Entry(input_frame)
            message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            setattr(self, f'input_{pm_key.replace(":", "_")}', message_input)
            
            # Create send button
            send_button = ttk.Button(
                input_frame, 
                text="Send", 
                command=lambda: self.send_pm_message(username, message_input.get(), server)
            )
            send_button.pack(side=tk.RIGHT, padx=5)
            
            # Bind Enter key to send message
            message_input.bind('<Return>', lambda event: self.send_pm_message(username, message_input.get(), server))
            
            # Add the tab to the notebook with PM prefix for clarity
            tab_text = f"PM: {username}"
            self.notebook.add(pm_tab, text=tab_text)
            
            # Store tab in tabs dictionary with pm: prefix
            tab_id = f"pm:{username}"
            self.tabs[tab_id] = pm_tab
            
            # Create PM info object to store data
            pm_info = {
                'tab': pm_tab,
                'chat_display': chat_display,
                'message_input': message_input,
                'server': server,
                'username': username
            }
            
            # Store in private_windows dictionary
            self.private_windows[pm_key] = pm_info
            
            # Add to tree view
            self.add_pm_node(username, server)
            
            # Add welcome message
            self.add_pm_message(pm_key, f"* Started private chat with {username}")
            
            # Select the new tab
            self.select_tab(tab_id)
            
            # Update status
            self.add_status_message(f"Started private chat with {username} on {server}")
        else:
            # If window exists, just select the tab
            self.select_tab(f"pm:{username}")

    def send_pm_message(self, username, message, server):
        """Send a private message and update the PM tab"""
        if not message.strip():
            return

        pm_key = f"{server}:{username}"
        if pm_key in self.private_windows:
            # Send the message to the server
            self.send_command(f"PRIVMSG {username} :{message}", server)
        
            # Get our nickname
            current_nick = self.connections[server]['nickname']
            
            # Add message to the PM tab
            self.add_pm_message(pm_key, f"{current_nick}: {message}")
            
            # Clear the input field
            self.private_windows[pm_key]['message_input'].delete(0, tk.END)
        
    def show_user_context_menu(self, event, channel_key):
        """Display the user context menu at the click position."""
        try:
            # Get the specific channel's info
            if channel_key not in self.channel_windows:
                print(f"Error: Channel info not found for {channel_key}")
                return
            channel_info = self.channel_windows[channel_key]
            users_listbox = channel_info.get('users_listbox')
            user_menu = channel_info.get('user_menu') # Get the correct menu
            
            if not users_listbox or not user_menu:
                print(f"Error: Listbox or menu not found for {channel_key}")
                return

            # Check if listbox exists
            if not users_listbox.winfo_exists():
                print(f"Error: Listbox for {channel_key} does not exist.")
                return

            # Get clicked item index
            clicked_index = users_listbox.nearest(event.y)
            
            # Check if the click was actually on an item
            if clicked_index < 0 or clicked_index >= users_listbox.size():
                 # Click was outside the list items, do nothing
                 return

            # Check if index is valid (important after nearest)
            if clicked_index >= 0:
                # Select the clicked item
                users_listbox.selection_clear(0, tk.END)
                users_listbox.selection_set(clicked_index)
                users_listbox.activate(clicked_index) # Highlight the selected item
                
                # Show menu at mouse position relative to screen
                user_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error showing user context menu: {e}")
            import traceback
            traceback.print_exc()
        
    def create_channel_window(self, channel, server):
        """Create a new channel window"""
        channel_key = f"{server}:{channel}"
        if channel_key in self.channel_windows:
            self.select_tab(channel_key)
            return # Already exists, just select it

        # --- Create Main Tab Frame ---
        channel_tab = ttk.Frame(self.notebook)

        # --- Top Frame for Topic ---
        topic_outer_frame = ttk.Frame(channel_tab)
        topic_outer_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0)) # Padding top/bottom
        topic_frame = ttk.Frame(topic_outer_frame, relief=tk.GROOVE, borderwidth=1)
        topic_frame.pack(fill=tk.X, expand=True)
        topic_label = ttk.Label(topic_frame, text="Requesting topic...", wraplength=600, padding=3)
        topic_label.pack(fill=tk.X, padx=2, pady=2) # Internal padding

        # --- Main Paned Window for Chat/Users ---
        paned = ttk.PanedWindow(channel_tab, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Left Pane: Chat Area ---
        chat_frame = ttk.Frame(paned)
        paned.add(chat_frame, weight=3) # Chat area takes more space

        # Chat display
        chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD)
        chat_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configure text tags (Add all necessary tags here)
        chat_display.tag_configure('timestamp', foreground='gray')
        chat_display.tag_configure('join', foreground='green')
        chat_display.tag_configure('part', foreground='red')
        chat_display.tag_configure('quit', foreground='red')
        chat_display.tag_configure('nick', foreground='blue')
        chat_display.tag_configure('username', foreground='gray')
        chat_display.tag_configure('my_username', foreground='magenta')
        chat_display.tag_configure('message', foreground='white')
        chat_display.tag_configure('action', foreground='purple')
        chat_display.tag_configure('status', foreground='cyan')
        chat_display.tag_configure('error', foreground='orange')


        # Input area (at the bottom of the chat frame)
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        message_input = ttk.Entry(input_frame)
        message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        setattr(self, f'input_{channel_key.replace(":", "_")}', message_input) # For focus setting

        send_button = ttk.Button(input_frame, text="Send",
                               command=lambda: self.send_channel_message(channel, message_input.get(), server))
        send_button.pack(side=tk.RIGHT)

        # Bind Enter key
        message_input.bind('<Return>', lambda event: self.send_channel_message(channel, message_input.get(), server))

        # --- Right Pane: Users Panel ---
        users_panel_frame = ttk.Frame(paned)
        paned.add(users_panel_frame, weight=1) # User list takes less space

        # Users label (inside the right panel, above the list)
        users_label = ttk.Label(users_panel_frame, text="Users: 0")
        users_label.pack(side=tk.TOP, padx=5, pady=(0, 2)) # Align top, remove fill=tk.X

        # Users list frame (contains listbox and scrollbars)
        users_list_frame = ttk.Frame(users_panel_frame)
        users_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5) # Fill remaining space

        # Scrollbars
        users_scrollbar = ttk.Scrollbar(users_list_frame)
        users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        users_horizontal_scrollbar = ttk.Scrollbar(users_list_frame, orient=tk.HORIZONTAL)
        users_horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Listbox
        users_listbox = tk.Listbox(users_list_frame,
                                 yscrollcommand=users_scrollbar.set,
                                 xscrollcommand=users_horizontal_scrollbar.set,
                                 activestyle='none') # Optional: better selection look
        users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        users_scrollbar.config(command=users_listbox.yview)
        users_horizontal_scrollbar.config(command=users_listbox.xview)

        # User Menu
        user_menu = tk.Menu(users_listbox, tearoff=0)
        user_menu.add_command(label="Private Message", command=lambda: self.open_pm_from_userlist(channel_key))
        user_menu.add_command(label="Whois", command=lambda: self.whois_from_userlist(channel_key))
        user_menu.add_separator()
        user_menu.add_command(label="Op", command=lambda: self.op_from_userlist(channel_key))
        user_menu.add_command(label="Deop", command=lambda: self.deop_from_userlist(channel_key))
        user_menu.add_command(label="Voice", command=lambda: self.voice_from_userlist(channel_key))
        user_menu.add_command(label="Devoice", command=lambda: self.devoice_from_userlist(channel_key))
        user_menu.add_separator()
        user_menu.add_command(label="Kick", command=lambda: self.kick_from_userlist(channel_key))
        user_menu.add_command(label="Ban", command=lambda: self.ban_from_userlist(channel_key))

        # Bind user list context menu
        users_listbox.bind("<Button-3>", lambda event, ck=channel_key: self.show_user_context_menu(event, ck))  # Right-click shows menu
        users_listbox.bind("<Double-Button-1>", lambda event, ck=channel_key: self.open_pm_from_userlist(ck, event))  # Double left-click opens PM directly


        # --- Final Setup ---
        # Add the tab to the notebook
        self.notebook.add(channel_tab, text=channel)
        self.tabs[channel_key] = channel_tab

        # Store channel info
        channel_info = {
            'tab': channel_tab,
            'chat_display': chat_display,
            'message_input': message_input,
            'topic_label': topic_label,
            'users_label': users_label, # Crucial: store the correct label
            'users': set(),
            'users_listbox': users_listbox,
            'user_menu': user_menu,
            'batch_updating': False,
            'names_buffer': set()
        }
        self.channel_windows[channel_key] = channel_info

        # Add node to the network tree
        self.add_channel_node(channel, server)

        # Request initial data
        self.send_command(f"NAMES {channel}", server)
        self.send_command(f"TOPIC {channel}", server)

        # Display join message
        self.add_channel_message(channel_key, f"* Joined channel {channel}", 'join')

        # Activate the new tab
        self.select_tab(channel_key)

        # Update status bar
        self.add_status_message(f"Joined channel: {channel} on {server}")

    def open_pm_from_userlist(self, channel_key, event=None):
        """Open a private message window for the selected user in a channel list.
        
        Can be called either from a menu action or directly from an event.
        """
        try:
            if channel_key not in self.channel_windows:
                self.add_status_message(f"Error: Channel key {channel_key} not found.", 'error')
                return
                
            channel_info = self.channel_windows[channel_key]
            users_listbox = channel_info.get('users_listbox')
            
            if not users_listbox:
                self.add_status_message("Error: User listbox not found for channel.", 'error')
                return
            
            # Handle selection differently based on how this was called
            if event:
                # Called from double-click event
                clicked_index = users_listbox.nearest(event.y)
                if clicked_index < 0 or clicked_index >= users_listbox.size():
                    return  # Click was outside valid items
                selected_user = users_listbox.get(clicked_index)
            else:
                # Called from menu
                selected_indices = users_listbox.curselection()
                if not selected_indices:
                    self.add_status_message("No user selected.", 'error')
                    return 
                selected_user = users_listbox.get(selected_indices[0])
            
            # Extract username (remove prefix)
            username = selected_user.lstrip('@+')
            
            # Extract server from channel_key
            server = channel_key.split(':', 1)[0]
            
            # Open the PM window
            self.create_private_window(username, server)
            
        except Exception as e:
            self.add_status_message(f"Error opening PM from user list: {e}", 'error')
            import traceback
            traceback.print_exc()

    def create_status_window(self):
        """Create the status window as a tab in the notebook"""
        # Create status tab frame
        self.status_window = ttk.Frame(self.notebook)
        self.tabs['status'] = self.status_window
        
        # Add the tab to the notebook
        self.notebook.add(self.status_window, text="Status")
        
        # Create status display in the tab
        self.status_display = scrolledtext.ScrolledText(self.status_window, wrap=tk.WORD)
        self.status_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.status_display.tag_configure('timestamp', foreground='gray')
        self.status_display.tag_configure('status', foreground='green')
        self.status_display.tag_configure('error', foreground='red')
        self.status_display.tag_configure('notice', foreground='blue')
        
        # Create input frame
        self.input_frame = ttk.Frame(self.status_window)
        self.input_frame.pack(fill=tk.X, pady=5)
        
        # Create command input
        self.command_input = ttk.Entry(self.input_frame)
        self.command_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.command_input.bind('<Return>', self.handle_status_input)
        
        # Add a send button
        send_button = ttk.Button(self.input_frame, text="Send", command=self.handle_status_command)
        send_button.pack(side=tk.RIGHT, padx=5)
        
        # Welcome message
        self.add_status_message(f"Welcome to {self.version}")
        self.add_status_message("Use /server hostname port nickname to connect to an IRC server")
        self.add_status_message("Example: /server irc.libera.chat 6667 YourNickname")
        
        # Make status tab active
        self.select_tab('status')
        
    def handle_status_input(self, event):
        """Handle input in the status window"""
        self.handle_status_command()
        
    def handle_status_command(self):
        """Process a command from the status input"""
        command = self.command_input.get().strip()
        if not command:
            return
            
        # Clear input field
        self.command_input.delete(0, tk.END)
        
        # If it's a server command, process it
        if command.startswith('/server'):
            parts = command.split()
            if len(parts) >= 2:
                server = parts[1]
                port = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 6667
                nickname = parts[3] if len(parts) > 3 else self.default_nickname
                self.connect_to_server(server, port, nickname)
                return
        
        # Handle script commands (work without server connection)
        if command.startswith('/script') or command.startswith('/alias') or command.startswith('/timer'):
            self.add_status_message(f"DEBUG: Processing script command: {command}")
            self.handle_command(command, None)
            return
                
        # For other commands, try to process with current server
        if command.startswith('/'):
            if self.current_server and self.current_server in self.connections:
                self.process_command(command, self.current_server)
            else:
                self.add_status_message("Not connected to any server. Use /server to connect.", 'error')
            return
            
        # Just display as a message if not a command
        self.add_status_message(command)

    def show_about_dialog(self):
        """Show the About rootX dialog"""
        about_window = tk.Toplevel(self.status_window)
        about_window.title("About rootX")
        about_window.geometry("400x500")
        about_window.transient(self.status_window)
        about_window.grab_set()
        
        # Make window non-resizable
        about_window.resizable(False, False)
        
        # Create main frame with padding
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title_label = ttk.Label(
            main_frame, 
            text="rootX IRC Client",
            font=("", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        try:
            # Load and display logo
            logo_path = os.path.join("icons", "rootx_logo.png")
            logo = tk.PhotoImage(file=logo_path).subsample(2, 2)
            logo_label = ttk.Label(main_frame, image=logo)
            logo_label.image = logo  # Keep reference
            logo_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        # Version info
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            version_frame,
            text="Version: 1.0.0",
            font=("", 10)
        ).pack()
        
        # Description
        desc_text = (
            "rootX is a modern, feature-rich IRC client built with Python and Tkinter. "
            "It provides an intuitive interface for IRC communication while maintaining "
            "the powerful features expected from a professional IRC client."
        )
        
        desc_label = ttk.Label(
            main_frame,
            text=desc_text,
            wraplength=350,
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20))
        
        # Features frame
        features_frame = ttk.LabelFrame(main_frame, text="Key Features", padding="10")
        features_frame.pack(fill=tk.X, pady=(0, 20))
        
        features = [
            "Multi-server support",
            "Channel management",
            "Private messaging",
            "User-friendly interface",
            "Customizable themes",
            "Advanced IRC commands"
        ]
        
        for feature in features:
            ttk.Label(features_frame, text=f"• {feature}").pack(anchor=tk.W)
        
        # Credits
        credits_frame = ttk.Frame(main_frame)
        credits_frame.pack(fill=tk.X)
        
        ttk.Label(
            credits_frame,
            text="Created by c0d3ninja",
            font=("", 9)
        ).pack()
        
        ttk.Label(
            credits_frame,
            text="© 2024 rootX Project",
            font=("", 9)
        ).pack()
        
        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=about_window.destroy
        ).pack(pady=(20, 0))



    def show_server_settings(self):
        """Show the Network List window (replaces old behavior)."""
        if self.network_list_window is not None:
            try:
                if self.network_list_window.winfo_exists():
                    self.network_list_window.lift()
                    self.network_list_window.focus_force()
                    return # Already open
                else:
                    self.network_list_window = None # Stale reference
            except tk.TclError:
                self.network_list_window = None # Stale reference

        # Create and show the window, passing the current theme
        # Ensure preferences and themes are loaded before this is called
        theme_name = self.preferences.get('theme', 'default')
        current_theme_dict = self.themes.get(theme_name, self.themes['default'])
        self.network_list_window = NetworkListWindow(self, current_theme_dict)

    def show_join_dialog(self):
        """Show join channel dialog"""
        if not self.connections:
            self.add_status_message("Not connected to any server")
            return
            
        servers_list = ", ".join(self.connections.keys())
        self.add_status_message(f"Connected to: {servers_list}")
        self.add_status_message("Use the /join command to join a channel")
        self.add_status_message("Example: /join #python")
        
        if len(self.connections) > 1:
            self.add_status_message("To join a channel on a specific server:")
            self.add_status_message("Example: /join #python irc.libera.chat")

    def show_connect_dialog(self):
        """Show a dialog to connect to a server"""
        if self.connections:
            servers_list = ", ".join(self.connections.keys())
            self.add_status_message(f"Already connected to: {servers_list}")
            self.add_status_message("Use /server hostname port nickname to connect to another server")
            self.add_status_message("Example: /server irc.esper.net 6667 MyNick")
            return
            
        self.add_status_message("Use /server hostname port nickname to connect")
        self.add_status_message("Example: /server irc.libera.chat 6667 PythonUser")
        
    def show_disconnect_dialog(self):
        """Show a dialog to disconnect from a server"""
        if not self.connections:
            self.add_status_message("Not connected to any server")
            return
            
        servers_list = ", ".join(self.connections.keys())
        self.add_status_message(f"Connected to: {servers_list}")
        self.add_status_message("Use /quit [message] to disconnect")
        self.add_status_message("Example: /quit Goodbye!")

    def disconnect_from_server(self, server):
        """Safely disconnect from a server"""
        try:
            self.disconnecting = True
            
            with self.lock:
                if server in self.connections:
                    self.add_status_message(f"Disconnecting from {server}...")
                    
                    # Close tabs using the new methods before removing server node
                    self.remove_server_node(server)
                    
                    # Try to send a QUIT message before disconnecting
                    try:
                        self.send_command(f"QUIT :Disconnecting", server)
                    except:
                        pass
                        
                    # Wait a moment for the QUIT message to be sent
                    time.sleep(0.5)
                    
                    # Close the socket
                    try:
                        sock = self.connections[server]['socket']
                        sock.shutdown(socket.SHUT_RDWR)
                        sock.close()
                    except:
                        pass
                        
                    # Remove from connections dictionary
                    del self.connections[server]
                    
                    # Wait for receive thread to terminate
                    if server in self.receive_threads:
                        current_thread = threading.current_thread()
                        if current_thread != self.receive_threads[server]:
                            try:
                                self.receive_threads[server].join(2.0)
                            except RuntimeError:
                                pass 
                        del self.receive_threads[server]
                    
                    # Update status
                    self.add_status_message(f"Disconnected from {server}")
                    
        except Exception as e:
            self.add_status_message(f"Error during disconnect from {server}: {e}", 'error')
        finally:
            self.disconnecting = False

    # --- Network Config Load/Save ---
    def load_network_config(self):
        """Loads network configuration from JSON file."""
        default_config = {
            "user_info": {
                "nick1": self.default_nickname,
                "nick2": "",
                "nick3": "",
                "username": self.default_nickname
            },
            "networks": []
        }
        if not os.path.exists(self.CONFIG_FILE):
            return default_config
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Simple validation/merge with defaults
                if "user_info" not in config: config["user_info"] = default_config["user_info"]
                if "networks" not in config: config["networks"] = default_config["networks"]
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading network config: {e}. Using defaults.")
            return default_config

    def save_network_config(self, config_data):
        """Saves network configuration to JSON file."""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
        except IOError as e:
            print(f"Error saving network config: {e}")
    # --- End Network Config ---

    def toggle_window(self, event):
        selection = self.windows_listbox.curselection()
        if not selection:
            return
            
        window_name = self.windows_listbox.get(selection[0])
        if window_name == "Status":
            return
            
        # Check if it's a channel with server prefix
        if ':' in window_name:
            if window_name in self.channel_windows:
                self.channel_windows[window_name].toggle_visibility()
        else:
            # Handle private messages
            if window_name in self.private_windows:
                self.private_windows[window_name].toggle_visibility()

    def send_command(self, command, server=None):
        """Send command to specified server or current server"""
        if server is None:
            server = self.current_server
        if server in self.connections:
            self.connections[server]['socket'].send(f"{command}\r\n".encode('utf-8'))

        
    def send_channel_message(self, channel, message, server):
        """Send a message to a channel and update the channel tab
        
        Args:
            channel: The channel name
            message: The message to send
            server: The server to send on
        """
        if not message.strip():
            return
            
        # First try to handle commands
        if message.startswith("/"):
            self.process_command(message, server)
            channel_key = f"{server}:{channel}"
            if channel_key in self.channel_windows:
                self.channel_windows[channel_key]['message_input'].delete(0, tk.END)
            return
            
        # Send to the server
        self.send_command(f"PRIVMSG {channel} :{message}", server)
        
        # Get our nickname
        current_nick = self.connections[server]['nickname']
        
        # Add to the channel tab
        channel_key = f"{server}:{channel}"
        self.add_channel_message(channel_key, f"{current_nick}: {message}")
        
        # Clear the input field
        if channel_key in self.channel_windows:
            self.channel_windows[channel_key]['message_input'].delete(0, tk.END)
        
    def handle_command(self, command, current_channel):
        # Check for script aliases first
        if self.script_engine:
            server = self.current_server if self.current_server else ''
            target = current_channel if current_channel else ''
            if self.script_engine.check_alias(command, server, target):
                return  # Alias was executed
        
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == '/quit':
            # Get server parameter if provided, otherwise use current_server
            if len(parts) > 1:
                # Check if the first parameter is a server name
                potential_server = parts[1]
                if potential_server in self.connections:
                    server = potential_server
                    quit_message = ' '.join(parts[2:]) if len(parts) > 2 else "Leaving"
                else:
                    # If first parameter isn't a server, use it as quit message
                    server = self.current_server
                    quit_message = ' '.join(parts[1:])
            else:
                server = self.current_server
                quit_message = "Leaving"
                
            if server:
                self.quit_server(server, quit_message)
            else:
                self.add_status_message("Not connected to any server")
            return

        if cmd == '/join':
            if len(parts) > 1:
                channel = parts[1]
                server = parts[2] if len(parts) > 2 else self.current_server
                if server in self.connections:
                    self.current_server = server
                    self.send_command(f"JOIN {channel}", server)
                    # Add this line to create the window/tab and tree node
                    self.create_channel_window(channel, server)
                else:
                    self.add_status_message(f"Not connected to server: {server}")
            else:
                self.add_status_message("Usage: /join #channel [server]")

        elif cmd == '/part':
            if current_channel:
                channel_key = f"{self.current_server}:{current_channel}"
                if channel_key in self.channel_windows:
                    self.send_command(f"PART {current_channel}", self.current_server)
                    self.channel_windows[channel_key].window.destroy()
                    del self.channel_windows[channel_key]

        elif cmd == '/server':
            try:
                if len(parts) >= 2:
                    server = parts[1]
                    # Use defaults if not provided
                    try:
                        port = int(parts[2]) if len(parts) > 2 else 6667
                    except ValueError:
                        self.add_status_message("Port must be a number, using default 6667", 'error')
                        port = 6667
                        
                    nickname = parts[3] if len(parts) > 3 else self.default_nickname
                    self.add_status_message(f"Connecting to {server}:{port} as {nickname}...")
                    self.connect_to_server(server, port, nickname)
                else:
                    self.add_status_message("Usage: /server <server> [port] [nickname]")
            except Exception as e:
                self.add_status_message(f"Error executing /server command: {e}", 'error')


            # Fix /me command handling
        elif cmd == '/me':
                if len(parts) > 1 and current_channel:
                    action_text = ' '.join(parts[1:])
                    channel_key = f"{self.current_server}:{current_channel}"
                    self.send_ctcp_request(current_channel, f"ACTION {action_text}", self.current_server)
                    if channel_key in self.channel_windows:
                        self.channel_windows[channel_key].add_action(
                            self.connections[self.current_server]['nickname'], 
                            action_text
                        )

        elif cmd == '/nick':
            if len(parts) > 1:
                new_nick = parts[1]
                self.send_command(f"NICK {new_nick}")

        elif cmd == '/list':
            self.send_command("LIST")


        elif cmd == '/nickserv' or cmd == '/ns':
            if len(parts) > 1:
                nickserv_command = ' '.join(parts[1:])  # Join all remaining parts
                self.send_command(f"PRIVMSG NickServ :{nickserv_command}", self.current_server)
            else:
                self.add_status_message("Usage: /nickserv identify <password> or /nickserv register <password> <email>")

        elif cmd == '/chanserv' or cmd == '/cs':
            if len(parts) > 1:
                chanserv_command = ' '.join(parts[1:])
                self.send_command(f"PRIVMSG ChanServ :{chanserv_command}", self.current_server)
            else:
                self.add_status_message("Usage: /chanserv identify <password>")
        
        # Script management commands
        elif cmd == '/script':
            self.handle_script_command(parts[1:] if len(parts) > 1 else [])
        
        elif cmd == '/alias':
            self.handle_alias_command(parts[1:] if len(parts) > 1 else [])
        
        elif cmd == '/timer':
            self.handle_timer_command(parts[1:] if len(parts) > 1 else [], current_channel)
        
        else:
            # Unknown command
            self.add_status_message(f"Unknown command: {cmd}")
                
    def handle_script_command(self, args):
        """Handle /script commands for managing scripts"""
        if not args:
            self.add_status_message("Script commands: /script load <file> | unload | reload | list | eval <code>")
            return
        
        subcmd = args[0].lower()
        
        if subcmd == 'load':
            if len(args) > 1:
                filename = args[1]
                success, msg = self.script_engine.load_script(filename)
                self.add_status_message(msg, 'status' if success else 'error')
            else:
                self.add_status_message("Usage: /script load <filename>")
        
        elif subcmd == 'reload':
            self.script_engine.clear_all()
            results = self.script_engine.load_all_scripts()
            for filename, success, msg in results:
                self.add_status_message(f"{filename}: {msg}", 'status' if success else 'error')
            self.add_status_message(f"Reloaded {len(results)} script(s)")
        
        elif subcmd == 'unload':
            self.script_engine.clear_all()
            self.add_status_message("All scripts unloaded")
        
        elif subcmd == 'list':
            events = self.script_engine.list_events()
            aliases = self.script_engine.list_aliases()
            timers = self.script_engine.list_timers()
            
            self.add_status_message(f"=== Scripts: {len(self.script_engine.loaded_scripts)} loaded ===")
            for name in self.script_engine.loaded_scripts:
                self.add_status_message(f"  {name}")
            
            self.add_status_message(f"=== Events: {len(events)} ===")
            for e in events:
                self.add_status_message(f"  [{e['index']}] on {e['type']}:{e['match']}:{e['target']}")
            
            self.add_status_message(f"=== Aliases: {len(aliases)} ===")
            for a in aliases:
                self.add_status_message(f"  /{a['name']}")
            
            self.add_status_message(f"=== Timers: {len(timers)} ===")
            for t in timers:
                self.add_status_message(f"  {t['name']}: {t['interval']}ms, {t['current_rep']}/{t['repetitions']}")
        
        elif subcmd == 'eval':
            if len(args) > 1:
                code = ' '.join(args[1:])
                context = {
                    'nick': '',
                    'chan': '',
                    'target': '',
                    'text': '',
                    'server': self.current_server or '',
                    'me': self.script_engine._get_my_nick(self.current_server or '')
                }
                self.script_engine.execute_commands(code, context, self.current_server or '', '')
            else:
                self.add_status_message("Usage: /script eval <code>")
        
        else:
            self.add_status_message("Unknown script command. Use: load, unload, reload, list, eval")
    
    def handle_alias_command(self, args):
        """Handle /alias commands for managing aliases"""
        if not args:
            # List all aliases
            aliases = self.script_engine.list_aliases()
            self.add_status_message(f"=== Aliases ({len(aliases)}) ===")
            for a in aliases:
                self.add_status_message(f"  /{a['name']}: {a['commands']}")
            return
        
        # Check if defining new alias: /alias /name { commands }
        alias_text = ' '.join(args)
        if alias_text.startswith('/'):
            # Parse: /aliasname { commands } or /aliasname commands
            match = __import__('re').match(r'/(\w+)\s*{\s*([\s\S]*?)\s*}', alias_text)
            if match:
                name, commands = match.groups()
                self.script_engine.register_alias(f'/{name}', commands)
                self.add_status_message(f"Alias /{name} defined")
            else:
                # Simple alias without braces
                parts = alias_text.split(None, 1)
                if len(parts) == 2:
                    name = parts[0]
                    commands = parts[1]
                    self.script_engine.register_alias(name, commands)
                    self.add_status_message(f"Alias {name} defined")
        else:
            self.add_status_message("Usage: /alias /name { commands } or /alias /name command")
    
    def handle_timer_command(self, args, current_channel):
        """Handle /timer commands"""
        if not args:
            timers = self.script_engine.list_timers()
            self.add_status_message(f"=== Active Timers ({len(timers)}) ===")
            for t in timers:
                self.add_status_message(f"  {t['name']}: {t['interval']}ms, rep {t['current_rep']}/{t['repetitions']}")
            return
        
        # /timer name off
        if len(args) >= 2 and args[1].lower() == 'off':
            name = args[0]
            if name in self.script_engine.timers:
                timer = self.script_engine.timers[name]
                if timer.timer_id:
                    self.window.after_cancel(timer.timer_id)
                del self.script_engine.timers[name]
                self.add_status_message(f"Timer '{name}' stopped")
            else:
                self.add_status_message(f"Timer '{name}' not found")
            return
        
        # /timer name interval reps command
        if len(args) >= 4:
            name, interval, reps = args[0], args[1], args[2]
            commands = ' '.join(args[3:])
            try:
                interval = int(interval)
                reps = int(reps)
                
                context = {
                    'nick': '',
                    'chan': current_channel or '',
                    'target': current_channel or '',
                    'text': '',
                    'server': self.current_server or '',
                    'me': self.script_engine._get_my_nick(self.current_server or '')
                }
                
                timer_args = f"{name} {interval} {reps} {{ {commands} }}"
                self.script_engine._cmd_timer(timer_args, context, self.current_server or '', current_channel or '')
                self.add_status_message(f"Timer '{name}' started: {interval}ms, {reps} reps")
            except ValueError:
                self.add_status_message("Usage: /timer <name> <interval_ms> <reps> <command>")
        else:
            self.add_status_message("Usage: /timer <name> <interval_ms> <reps> <command> | /timer <name> off")

    def _add_status_message_gui(self, message, tag):
        """Internal method to add status message in GUI thread"""
        try:
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            
            # Insert with appropriate tag
            self.status_display.insert(tk.END, timestamp + " ", 'timestamp')
            self.status_display.insert(tk.END, message + "\n", tag)
            self.status_display.see(tk.END)
        
            # Update status bar if available
            if hasattr(self, 'status_bar') and self.status_bar is not None:
                self.status_bar.config(text=message)
        except Exception as e:
            # If anything goes wrong, fallback to console output
            print(f"Status: {message} (GUI error: {e})")
    
    def add_status_message(self, message, tag='status'):
        """Add a message to the status window (thread-safe)"""
        if not hasattr(self, 'status_display') or self.status_display is None:
            print(f"Status: {message}")  # Fallback if GUI not initialized
            return
            
        try:
            # Schedule GUI update on main thread to avoid threading issues
            self.window.after(0, self._add_status_message_gui, message, tag)
        except Exception as e:
            # If anything goes wrong, fallback to console output
            print(f"Status: {message} (Scheduling error: {e})")
    
    def handle_server_message(self, data, server):
        """Handle a message from the server"""
        if not data:
            return
            
        try:
            if data.startswith('ERROR :') or 'Connection closed' in data:
                error_msg = data.split(':', 1)[1].strip()
                self.add_status_message(f"Server {server} disconnected: {error_msg}")
                self.quit_server(server)
                self.remove_server_node(server)
                return
                
            # Print raw data to status window for debugging
            self.add_status_message(f"DEBUG: {data}")
            
            if data.startswith('PING'):
                ping_param = data.split(':', 1)[1] if ':' in data else data.split('PING', 1)[1]
                self.send_command(f'PONG :{ping_param.strip()}', server)
                self.add_status_message(f"PONG sent to {server}")
                return
            elif data.startswith('PONG'):
                return
            
            # Handle PRIVMSG (including channel messages and private messages)
            elif 'PRIVMSG' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        sender = parts[0].lstrip(':')
                        target = data.split('PRIVMSG')[1].split(':', 1)[0].strip()
                        message = data.split('PRIVMSG')[1].split(':', 1)[1].strip()
                        
                        # Handle ACTION messages
                        if message.startswith('\x01ACTION') and message.endswith('\x01'):
                            action_text = message[8:-1]
                            if target.startswith('#'):  # Channel action
                                channel_key = f"{server}:{target}"
                                if channel_key in self.channel_windows:
                                    self.add_channel_action(channel_key, sender, action_text)
                                # Trigger ACTION script event
                                if self.script_engine:
                                    self.script_engine.trigger_event('ACTION', sender, target, action_text, server)
                            else:  # Private message action
                                pm_key = f"{server}:{sender}"
                                if pm_key not in self.private_windows:
                                    self.create_private_window(sender, server)
                                self.add_pm_action(pm_key, sender, action_text)
                                # Trigger ACTION script event for PM
                                if self.script_engine:
                                    self.script_engine.trigger_event('ACTION', sender, sender, action_text, server)
                        else:
                            # Handle regular messages
                            if target.startswith('#'):  # Channel message
                                channel_key = f"{server}:{target}"
                                if channel_key in self.channel_windows:
                                    self.add_channel_message(channel_key, f"{sender}: {message}")
                                # Trigger TEXT script event
                                if self.script_engine:
                                    self.script_engine.trigger_event('TEXT', sender, target, message, server)
                            else:  # Private message
                                pm_key = f"{server}:{sender}"
                                if pm_key not in self.private_windows:
                                    self.create_private_window(sender, server)
                                self.add_pm_message(pm_key, f"{sender}: {message}")
                                # Trigger TEXT script event for PM
                                if self.script_engine:
                                    self.script_engine.trigger_event('TEXT', sender, '?', message, server)
                                
                    # Return after processing PRIVMSG to prevent duplicate processing
                    return
                except Exception as e:
                    self.add_status_message(f"Error handling message: {e}")
                    return

            # Handle MODE changes
            elif 'MODE' in data:
                try:
                    parts = data.split()
                    if len(parts) >= 4:
                        setter = parts[0].split('!')[0].lstrip(':')
                        channel = parts[2]
                        mode = parts[3]
                        target = parts[4] if len(parts) > 4 else None
                        
                        channel_key = f"{server}:{channel}"
                        if channel_key in self.channel_windows:
                            channel_info = self.channel_windows[channel_key]
                            
                            if target:
                                # Handle user modes
                                if '+o' in mode:
                                    # Add @ to user in list
                                    channel_info['users'].discard(target)
                                    channel_info['users'].add(f"@{target}")
                                    self.update_channel_users(channel_key)
                                    self.add_channel_message(channel_key, f"* {setter} gives channel operator status to {target}", 'status')
                                    
                                elif '-o' in mode:
                                    # Remove @ from user
                                    channel_info['users'].discard(f"@{target}")
                                    channel_info['users'].add(target)
                                    self.update_channel_users(channel_key)
                                    self.add_channel_message(channel_key, f"* {setter} removes channel operator status from {target}", 'status')
                                    
                                elif '+v' in mode:
                                    # Add + to user
                                    channel_info['users'].discard(target)
                                    channel_info['users'].add(f"+{target}")
                                    self.update_channel_users(channel_key)
                                    self.add_channel_message(channel_key, f"* {setter} gives voice to {target}", 'status')
                                    
                                elif '-v' in mode:
                                    # Remove + from user
                                    channel_info['users'].discard(f"+{target}")
                                    channel_info['users'].add(target)
                                    self.update_channel_users(channel_key)
                                    self.add_channel_message(channel_key, f"* {setter} removes voice from {target}", 'status')
                except Exception as e:
                    self.add_status_message(f"Error handling mode: {e}")
                            
            # Handle JOIN messages
            elif 'JOIN' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        user = parts[0].lstrip(':')
                        channel = data.split('JOIN')[1].strip().lstrip(':')
                        channel_key = f"{server}:{channel}"
                        
                        if channel_key in self.channel_windows:
                            channel_info = self.channel_windows[channel_key]
                            channel_info['users'].add(user)
                            self.update_channel_users(channel_key)
                            self.add_channel_message(channel_key, f"* {user} has joined {channel}", 'join')
                            
                            # Request NAMES list if we joined
                            if user == self.connections[server]['nickname']:
                                # Mark that we are waiting for the initial NAMES list
                                if channel_key in self.channel_windows:
                                    self.channel_windows[channel_key]['waiting_for_names'] = True
                                self.send_command(f"NAMES {channel}", server)
                        
                        # Trigger JOIN script event
                        if self.script_engine:
                            self.script_engine.trigger_event('JOIN', user, channel, '', server)
                except Exception as e:
                    self.add_status_message(f"Error handling join: {e}")
                    
            # Handle NAMES reply (numeric 353)
            elif ' 353 ' in data:  # NAMES reply
                try:
                    # Parse channel name
                    channel = None
                    parts = data.split()
                    for i, part in enumerate(parts):
                        if part in ['=', '*', '@'] and i + 1 < len(parts): # Channel type indicators
                            channel = parts[i + 1]
                            break
                    
                    if channel:
                        channel_key = f"{server}:{channel}"
                        if channel_key in self.channel_windows:
                            channel_info = self.channel_windows[channel_key]
                            
                            # If this is the first NAMES reply after joining, clear existing users
                            if channel_info.get('waiting_for_names', False):
                                print(f"DEBUG - Clearing users for {channel_key} on first NAMES reply.")
                                channel_info['users'] = set() # Clear the set
                                channel_info['waiting_for_names'] = False # Reset flag
                            
                            # Get the users part (after the last ':')
                            users_part = data.split(':', 2)[-1].strip()
                            users_list = users_part.split()
                            
                            # Add users directly to the main set
                            channel_info['users'].update(users_list)
                            # Do NOT trigger UI update here - wait for 366
                except Exception as e:
                    self.add_status_message(f"Error processing NAMES (353): {e}")
                    traceback.print_exc()
                    
            # Handle end of NAMES list (numeric 366)
            elif ' 366 ' in data:  # End of NAMES
                try:
                    # Find channel name
                    channel = None
                    parts = data.split()
                    for part in parts:
                        if part.startswith('#'):
                            channel = part
                            break
                    
                    if channel:
                        channel_key = f"{server}:{channel}"
                        if channel_key in self.channel_windows:
                            channel_info = self.channel_windows[channel_key]
                            
                            # Mark that initial names are received (if flag was used)
                            channel_info['waiting_for_names'] = False 
                            
                            # Now that the list is complete, trigger the update
                            print(f"DEBUG - End of NAMES for {channel_key}, triggering update.")
                            self.update_channel_users(channel_key)
                except Exception as e:
                    self.add_status_message(f"Error handling end of NAMES (366): {e}")
                    traceback.print_exc()

            # --- Handle LIST replies (321, 322, 323) ---
            elif ' 321 ' in data: # RPL_LISTSTART
                # Find the channel list window for this server and tell it to clear
                if server in self.channel_list_windows:
                    try:
                        if self.channel_list_windows[server].window.winfo_exists():
                            self.channel_list_windows[server].clear_list()
                            def update_status():
                                self.channel_list_windows[server].status_label.config(text="Receiving list...")
                            self.window.after(0, update_status)
                    except Exception as e:
                        print(f"Error clearing channel list window: {e}")
                return # Don't print raw 321 message to status
            
            elif ' 322 ' in data: # RPL_LIST
                # :irc.libera.chat 322 YourNick #channel 123 :Topic text here
                try:
                    parts = data.split(' ', 4) # Split into server, code, nick, channel, rest
                    if len(parts) >= 4:
                        channel = parts[3]
                        users_topic_part = data.split(channel, 1)[1].strip() # Get part after channel name
                        users_topic_parts = users_topic_part.split(' :', 1) # Split users count and topic
                        users_count = users_topic_parts[0].strip()
                        topic = users_topic_parts[1].strip() if len(users_topic_parts) > 1 else ""

                        # Find the channel list window and add the entry
                        if server in self.channel_list_windows:
                            try:
                                if self.channel_list_windows[server].window.winfo_exists():
                                    self.channel_list_windows[server].add_channel_entry(channel, users_count, topic)
                            except Exception as e:
                                print(f"Error adding channel list entry: {e}")
                except Exception as e:
                    self.add_status_message(f"Error parsing LIST reply (322): {e}")
                    traceback.print_exc()
                return # Don't print raw 322 message to status
            
            elif ' 323 ' in data: # RPL_LISTEND
                # Find the channel list window and mark as complete
                if server in self.channel_list_windows:
                    try:
                        if self.channel_list_windows[server].window.winfo_exists():
                            self.channel_list_windows[server].list_complete()
                    except Exception as e:
                        print(f"Error finalizing channel list window: {e}")
                return # Don't print raw 323 message to status
            # --- End LIST handling ---

            # Handle PART messages
            elif 'PART' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        user = parts[0].lstrip(':')
                        channel = data.split('PART')[1].split()[0].strip()
                        channel_key = f"{server}:{channel}"
                        
                        # Trigger PART script event
                        if self.script_engine:
                            self.script_engine.trigger_event('PART', user, channel, '', server)
                        
                        # If we left the channel, close the tab
                        if user == self.connections[server]['nickname']:
                            self.add_status_message(f"You left {channel} on {server}", 'part')
                            self.close_channel_tab(channel, server)
                        # If someone else left
                        elif channel_key in self.channel_windows:
                            channel_info = self.channel_windows[channel_key]
                            # Remove user with any prefix
                            for u in list(channel_info['users']):
                                if u == user or u.lstrip('@+') == user:
                                    channel_info['users'].discard(u)
                            self.update_channel_users(channel_key)
                            self.add_channel_message(channel_key, f"* {user} has left {channel}", 'part')
                except Exception as e:
                    self.add_status_message(f"Error handling part: {e}")

            # Handle KICK messages
            elif 'KICK' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        kicker = parts[0].lstrip(':')
                        kicked_parts = data.split('KICK')[1].split(':', 1)
                        channel_and_user = kicked_parts[0].strip().split()
                        channel = channel_and_user[0]
                        kicked_user = channel_and_user[1]
                        reason = kicked_parts[1].strip() if len(kicked_parts) > 1 else "No reason given"
                        
                        # Trigger KICK script event
                        if self.script_engine:
                            self.script_engine.trigger_event('KICK', kicker, channel, reason, server, 
                                {'knick': kicked_user, 'kicked': kicked_user})
                        
                        channel_key = f"{server}:{channel}"
                        if channel_key in self.channel_windows:
                            channel_info = self.channel_windows[channel_key]
                            
                            # Remove the kicked user from users list
                            for u in list(channel_info['users']):
                                if u == kicked_user or u.lstrip('@+') == kicked_user:
                                    channel_info['users'].discard(u)
                            self.update_channel_users(channel_key)
                            
                            if kicked_user == self.connections[server]['nickname']:
                                # We were kicked
                                self.add_channel_message(channel_key, f"* You were kicked from {channel} by {kicker} ({reason})", 'part')
                                # Close the tab immediately, not after a delay
                                self.close_channel_tab(channel, server)
                            else:
                                self.add_channel_message(channel_key, f"* {kicked_user} was kicked from {channel} by {kicker} ({reason})", 'part')
                except Exception as e:
                    self.add_status_message(f"Error handling kick: {e}")

            # Handle QUIT messages
            elif 'QUIT' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        user = parts[0].lstrip(':')
                        quit_msg = data.split('QUIT')[1].strip()
                        if ':' in quit_msg:
                            quit_msg = quit_msg.split(':', 1)[1].strip()
                        
                        # Trigger QUIT script event
                        if self.script_engine:
                            self.script_engine.trigger_event('QUIT', user, '*', quit_msg, server)
                        
                        # Update all channel windows where this user was present
                        for channel_key, channel_info in self.channel_windows.items():
                            if channel_key.startswith(f"{server}:"):
                                # Check all users (including those with prefixes)
                                for u in list(channel_info['users']):
                                    if u == user or u.lstrip('@+') == user:
                                        channel_info['users'].discard(u)
                                        self.update_channel_users(channel_key)
                                        self.add_channel_message(channel_key, f"* {user} has quit ({quit_msg})", 'quit')
                                        break
                except Exception as e:
                    self.add_status_message(f"Error handling quit: {e}")

            # Handle nickname changes
            elif 'NICK' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        old_nick = parts[0].lstrip(':')
                        new_nick = data.split('NICK')[1].strip().lstrip(':')
                        
                        # Trigger NICK script event
                        if self.script_engine:
                            self.script_engine.trigger_event('NICK', old_nick, '*', new_nick, server,
                                {'newnick': new_nick, 'oldnick': old_nick})
                        
                        # Update all channel windows where this user was present
                        for channel_key, channel_info in self.channel_windows.items():
                            if channel_key.startswith(f"{server}:"):
                                # Check if old_nick is in users list (with or without prefix)
                                user_found = False
                                for u in list(channel_info['users']):
                                    if u == old_nick or u.lstrip('@+') == old_nick:
                                        prefix = ''
                                        if u.startswith('@'):
                                            prefix = '@'
                                        elif u.startswith('+'):
                                            prefix = '+'
                                        
                                        # Remove old nick and add new nick with same prefix
                                        channel_info['users'].discard(u)
                                        channel_info['users'].add(f"{prefix}{new_nick}")
                                        user_found = True
                                        break
                                
                                if user_found:
                                    self.update_channel_users(channel_key)
                                    self.add_channel_message(channel_key, f"* {old_nick} is now known as {new_nick}", 'nick')
                        
                        # Update our own nickname if it's us
                        if old_nick == self.connections[server]['nickname']:
                            self.connections[server]['nickname'] = new_nick
                            self.add_status_message(f"Your nickname on {server} is now {new_nick}")
                except Exception as e:
                    self.add_status_message(f"Error handling nick change: {e}")

            # Handle topic change
            elif 'TOPIC' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        setter = parts[0].lstrip(':')
                        topic_parts = data.split('TOPIC')[1].split(':', 1)
                        channel = topic_parts[0].strip()
                        topic = topic_parts[1].strip() if len(topic_parts) > 1 else ""
                        
                    channel_key = f"{server}:{channel}"
                    if channel_key in self.channel_windows:
                        # Update the topic label (thread-safe)
                        channel_info = self.channel_windows[channel_key]
                        def update_topic():
                            channel_info['topic_label'].config(text=topic if topic else "No topic set")
                        self.window.after(0, update_topic)
                        
                        # Add message to channel
                        self.add_channel_message(channel_key, f"* {setter} has changed the topic to: {topic}", 'status')
                except Exception as e:
                    self.add_status_message(f"Error handling topic change: {e}")
                    
            # Handle topic reply (numeric 332)
            elif ' 332 ' in data:
                try:
                    parts = data.split(' 332 ')[1].split(':', 1)
                    channel = parts[0].strip().split()[1]
                    topic = parts[1].strip() if len(parts) > 1 else "No topic set"
                    
                    channel_key = f"{server}:{channel}"
                    if channel_key in self.channel_windows:
                        # Update the topic label (thread-safe)
                        channel_info = self.channel_windows[channel_key]
                        def update_topic():
                            channel_info['topic_label'].config(text=topic)
                        self.window.after(0, update_topic)
                except Exception as e:
                    self.add_status_message(f"Error handling topic reply: {e}")
                
        except Exception as e:
            self.add_status_message(f"Error processing message: {e}")

    def connect_to_server(self, server, port, nickname):
        """Connect to an IRC server and set up the connection"""
        try:
            # Check if already connected to this server
            if server in self.connections:
                self.add_status_message(f"Already connected to {server}")
                # Set as current server
                self.current_server = server
                return
            
            # Add debug message
            self.add_status_message(f"Attempting to connect to {server}:{port} as {nickname}", 'notice')
                
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Make the socket keep-alive
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Set a timeout for the connection attempt only
            sock.settimeout(15)
            
            # Log connection attempt
            self.add_status_message(f"Connecting to {server}:{port}...")
            
            # Connect to server
            sock.connect((server, int(port)))
            
            # After successful connection, set to blocking mode with a small timeout
            # to allow for periodic checks of disconnecting flag
            sock.settimeout(0.5)
            
            # Log successful connection
            self.add_status_message(f"Socket connected to {server}:{port}")
            
            # Store connection info
            self.connections[server] = {
                'socket': sock,
                'nickname': nickname,
                'channels': set(),
                'users': {},  # Track users per server
                'last_ping': time.time()  # Track time of last ping
            }
            
            # Set as current server
            self.current_server = server
            
            # Add server node to tree if it doesn't exist (thread-safe)
            if server not in self.server_nodes:
                def add_node():
                    # Create server node in tree
                    server_node = self.network_tree.insert("", "end", text=server, tags=("server",))
                    self.server_nodes[server] = {
                        'node': server_node,
                        'channels': {},
                        'private_msgs': {}
                    }
                self.window.after(0, add_node)
            
            # Send registration commands
            self.add_status_message(f"Sending registration commands...")
            sock.send(f"NICK {nickname}\r\n".encode('utf-8'))
            sock.send(f"USER {nickname} 0 * :{nickname}\r\n".encode('utf-8'))
            
            # Start receive thread
            receive_thread = threading.Thread(
                target=self.receive_data,
                args=(server,),
                daemon=True
            )
            self.receive_threads[server] = receive_thread
            receive_thread.start()
            
            # Start a ping thread to keep the connection alive
            ping_thread = threading.Thread(
                target=self.ping_server_periodically,
                args=(server,),
                daemon=True
            )
            ping_thread.start()
            
            # Update status
            self.add_status_message(f"Connected to {server}:{port} as {nickname}")
            
        except ConnectionRefusedError:
            self.add_status_message(f"Error: Connection to {server}:{port} refused", 'error')
            # Clean up failed connection
            if server in self.connections:
                del self.connections[server]
        except socket.gaierror:
            self.add_status_message(f"Error: Could not resolve hostname {server}", 'error')
            # Clean up failed connection
            if server in self.connections:
                del self.connections[server]
        except socket.timeout:
            self.add_status_message(f"Error: Connection to {server}:{port} timed out", 'error')
            # Clean up failed connection
            if server in self.connections:
                del self.connections[server]
        except Exception as e:
            self.add_status_message(f"Error connecting to {server}: {e}", 'error')
            # Clean up failed connection
            if server in self.connections:
                del self.connections[server]
                
            # Try to clean up socket
            try:
                sock.close()
            except:
                pass
                
    def ping_server_periodically(self, server):
        """Send periodic pings to keep the connection alive"""
        try:
            ping_interval = 30  # Ping every 30 seconds
            while server in self.connections and not self.disconnecting:
                # Wait for the interval
                time.sleep(ping_interval)
                
                # Check if we're still connected
                if server not in self.connections or self.disconnecting:
                    break
                    
                # Send a ping
                try:
                    current_time = int(time.time())
                    self.send_command(f"PING :{current_time}", server)
                    self.connections[server]['last_ping'] = time.time()
                except Exception as e:
                    self.add_status_message(f"Error sending ping to {server}: {e}", 'error')
                    break
                    
        except Exception as e:
            self.add_status_message(f"Error in ping thread for {server}: {e}", 'error')
        finally:
            # Thread is exiting - if we're still connected, something went wrong
            if server in self.connections and not self.disconnecting:
                self.add_status_message(f"Ping thread for {server} exited unexpectedly", 'error')

    def run(self):
        """Start the IRC client"""
        try:
            # Start periodic task processor to keep UI responsive
            self.process_deferred_ui_tasks()
            
            # Start the main loop
            self.window.mainloop()
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            # Cleanup when the program exits
            self.running = False
            self.disconnecting = True
            with self.lock:
                for server, conn in self.connections.items():
                    try:
                        conn['socket'].close()
                    except:
                        pass
                
                # Wait for all receive threads to terminate
                for server, thread in list(self.receive_threads.items()):
                    thread.join(0.5)  # Short timeout

    def receive_data(self, server):
        """Receive and process data from a specific server connection"""
        try:
            buffer = ""
            sock = self.connections[server]['socket']
            
            # Set a small timeout for quicker response to disconnect
            # This is already set in connect_to_server
            
            # Track consecutive timeouts
            consecutive_timeouts = 0
            max_consecutive_timeouts = 20  # About 10 seconds with 0.5s timeout
            
            self.add_status_message(f"Started receive thread for {server}")
            
            while server in self.connections and not self.disconnecting:
                try:
                    data = sock.recv(4096).decode('utf-8', errors='replace')
                    if not data:  # Connection closed by server
                        # Only consider it closed if we've received nothing multiple times
                        consecutive_timeouts += 1
                        if consecutive_timeouts >= 3:  # Three consecutive empty reads
                            self.add_status_message(f"Connection to {server} closed by remote host", 'error')
                        break
                        # Otherwise, try again
                        continue
                    
                    # Reset timeout counter on successful data
                    consecutive_timeouts = 0
                    
                    # Add data to buffer and process complete lines
                    buffer += data
                    lines = buffer.split('\r\n')
                    buffer = lines.pop()  # Keep incomplete line in buffer
                    
                    for line in lines:
                        print(f"RECV {server}: {line}")
                        self.handle_server_message(line, server)
                        
                except socket.timeout:
                    # Count consecutive timeouts
                    consecutive_timeouts += 1
                    
                    # If too many consecutive timeouts, check connection with a PING
                    if consecutive_timeouts >= max_consecutive_timeouts:
                        # Send a ping to check if connection is still alive
                        try:
                            current_time = int(time.time())
                            self.send_command(f"PING :{current_time}", server)
                            consecutive_timeouts = 0  # Reset counter on successful send
                        except socket.error:
                            self.add_status_message(f"Connection to {server} appears to be lost", 'error')
                            break
                    continue
                    
                except UnicodeDecodeError as e:
                    self.add_status_message(f"Unicode decode error for {server}: {e}", 'error')
                    consecutive_timeouts = 0  # Reset counter on any activity
                    continue
                    
                except socket.error as e:
                    self.add_status_message(f"Socket error for {server}: {e}", 'error')
                    break
                    
        except Exception as e:
            self.add_status_message(f"Error in receive thread for {server}: {e}", 'error')
        finally:
            # Clean up but only if not already being cleaned up elsewhere
            if server in self.connections and not self.disconnecting:
                try:
                    self.disconnect_from_server(server)
                except Exception as e:
                    self.add_status_message(f"Error disconnecting from {server}: {e}", 'error')
                    
            self.add_status_message(f"Receive thread for {server} terminated")

    def on_tree_select(self, event):
        """Handle tree item selection"""
        selected = self.network_tree.selection()
        if not selected:
            return
            
        item = selected[0]
        item_tags = self.network_tree.item(item)['tags']
        item_text = self.network_tree.item(item)['text']
        
        # Server node selected
        if 'server' in item_tags:
            self.current_server = item_text
            # Display the server in status window
            self.add_status_message(f"Selected server: {item_text}")
            
        # Channel node selected
        elif 'channel' in item_tags:
            # Get the server from the parent node
            parent = self.network_tree.parent(item)
            server = self.network_tree.item(parent)['text']
            
            # Create the channel_key
            channel_key = f"{server}:{item_text}"
            
            # Select the corresponding tab
            if channel_key in self.channel_windows:
                self.select_tab(channel_key)
            
        # PM node selected
        elif 'pm' in item_tags:
            # Extract the username from "PM: username"
            username = item_text.replace("PM: ", "")
            
            # Get the server from the parent node
            parent = self.network_tree.parent(item)
            server = self.network_tree.item(parent)['text']
            
            # Create the pm_key
            pm_key = f"{server}:{username}"
            
            # Select the corresponding tab
            if pm_key in self.private_windows:
                tab_id = f"pm:{username}"
                self.select_tab(tab_id)

    def process_command(self, message, server):
        """Process commands that start with /
        
        Args:
            message: The message to process
            server: The server to run the command on
        """
        if not message.startswith('/'):
            return False
            
        # Extract command and arguments
        parts = message.split(' ', 1)
        command = parts[0][1:].lower()  # Remove / and make lowercase
        args = parts[1] if len(parts) > 1 else ""
        
        # Handle various commands
        if command == 'join':
            channel = args.split()[0] if args else ""
            if channel:
                if not channel.startswith('#'):
                    channel = f"#{channel}"
                self.send_command(f"JOIN {channel}", server)
                # Add this line to create the window/tab and tree node
                self.create_channel_window(channel, server)
                return True
                
        elif command == 'part':
            channel = args.split()[0] if args else ""
            reason = ' '.join(args.split()[1:]) if len(args.split()) > 1 else "Leaving"
            if channel:
                if not channel.startswith('#'):
                    channel = f"#{channel}"
                self.send_command(f"PART {channel} :{reason}", server)
                return True
                
        elif command == 'quit':
            reason = args if args else "Leaving"
            self.quit_server(server, reason)
            return True
            
        elif command == 'msg' or command == 'query':
            parts = args.split(' ', 1)
            if len(parts) >= 2:
                target = parts[0]
                msg = parts[1]
                self.send_command(f"PRIVMSG {target} :{msg}", server)
                
                # For query, also open a PM window
                if command == 'query' and not target.startswith('#'):
                    self.create_private_window(target, server)
                return True
                
        elif command == 'nick':
            new_nick = args.strip()
            if new_nick:
                self.send_command(f"NICK {new_nick}", server)
                return True
                
        elif command == 'me':
            if self.current_tab and ':' in self.current_tab:
                server_name, channel = self.current_tab.split(':', 1)
                if server_name == server:
                    self.send_command(f"PRIVMSG {channel} :\x01ACTION {args}\x01", server)
                    # Add to display
                    if channel.startswith('#'):
                        self.add_channel_action(self.current_tab, self.connections[server]['nickname'], args)
                    else:
                        self.add_pm_action(self.current_tab, self.connections[server]['nickname'], args)
                    return True
                    
        elif command == 'whois':
            target = args.split()[0] if args else ""
            if target:
                self.send_command(f"WHOIS {target}", server)
                return True
                
        elif command == 'kick':
            parts = args.split()
            if len(parts) >= 2:
                channel = parts[0]
                user = parts[1]
                reason = ' '.join(parts[2:]) if len(parts) > 2 else "Kicked"
                if not channel.startswith('#'):
                    channel = f"#{channel}"
                self.send_command(f"KICK {channel} {user} :{reason}", server)
                return True
                
        elif command == 'ban':
            parts = args.split()
            if len(parts) >= 2:
                channel = parts[0]
                user = parts[1]
                if not channel.startswith('#'):
                    channel = f"#{channel}"
                self.send_command(f"MODE {channel} +b {user}!*@*", server)
                return True
                
        elif command == 'op':
            parts = args.split()
            if len(parts) >= 2:
                channel = parts[0]
                user = parts[1]
                if not channel.startswith('#'):
                    channel = f"#{channel}"
                self.send_command(f"MODE {channel} +o {user}", server)
                return True
                
        elif command == 'deop':
            parts = args.split()
            if len(parts) >= 2:
                channel = parts[0]
                user = parts[1]
                if not channel.startswith('#'):
                    channel = f"#{channel}"
                self.send_command(f"MODE {channel} -o {user}", server)
                return True
                
        elif command == 'voice':
            parts = args.split()
            if len(parts) >= 2:
                channel = parts[0]
                user = parts[1]
                if not channel.startswith('#'):
                    channel = f"#{channel}"
                self.send_command(f"MODE {channel} +v {user}", server)
                return True
                
        elif command == 'devoice':
            parts = args.split()
            if len(parts) >= 2:
                channel = parts[0]
                user = parts[1]
                if not channel.startswith('#'):
                    channel = f"#{channel}"
                self.send_command(f"MODE {channel} -v {user}", server)
                return True
                
        elif command == 'topic':
            if self.current_tab and ':' in self.current_tab:
                server_name, channel = self.current_tab.split(':', 1)
                if server_name == server and channel.startswith('#'):
                    if args:
                        self.send_command(f"TOPIC {channel} :{args}", server)
                    else:
                        self.send_command(f"TOPIC {channel}", server)
                    return True
                    
        elif command == 'mode':
            parts = args.split()
            if len(parts) >= 2:
                target = parts[0]
                mode = parts[1]
                params = ' '.join(parts[2:]) if len(parts) > 2 else ""
                self.send_command(f"MODE {target} {mode} {params}", server)
                return True
                
        elif command == 'server':
            parts = args.split()
            if len(parts) >= 1:
                new_server = parts[0]
                port = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 6667
                nickname = parts[2] if len(parts) > 2 else self.default_nickname
                self.connect_to_server(new_server, port, nickname)
                return True
        
        # If no command matched, send as raw command
        self.send_command(message[1:], server)
        return True

    def show_tree_menu(self, event):
        """Show context menu for tree items"""
        # Get the item under cursor
        item = self.network_tree.identify('item', event.x, event.y)
        if not item:
            return
            
        # Select the item
        self.network_tree.selection_set(item)
        
        # Get item info
        item_tags = self.network_tree.item(item)['tags']
        
        # Configure menu based on item type
        if 'server' in item_tags:
            # Server context menu
            self.tree_menu.entryconfig("Connect", state="normal")
            self.tree_menu.entryconfig("Disconnect", state="normal")
            self.tree_menu.entryconfig("Join Channel", state="normal")
            self.tree_menu.entryconfig("Close Tab", state="disabled")
        elif 'channel' in item_tags:
            # Channel context menu
            self.tree_menu.entryconfig("Connect", state="disabled")
            self.tree_menu.entryconfig("Disconnect", state="disabled")
            self.tree_menu.entryconfig("Join Channel", state="disabled")
            self.tree_menu.entryconfig("Close Tab", state="normal")
        elif 'pm' in item_tags:
            # PM context menu
            self.tree_menu.entryconfig("Connect", state="disabled")
            self.tree_menu.entryconfig("Disconnect", state="disabled")
            self.tree_menu.entryconfig("Join Channel", state="disabled")
            self.tree_menu.entryconfig("Close Tab", state="normal")
        else:
            # Other item or no item - disable all
            self.tree_menu.entryconfig("Connect", state="disabled")
            self.tree_menu.entryconfig("Disconnect", state="disabled")
            self.tree_menu.entryconfig("Join Channel", state="disabled")
            self.tree_menu.entryconfig("Close Tab", state="disabled")
            
        # Display the menu
        self.tree_menu.tk_popup(event.x_root, event.y_root)
        
    def connect_selected(self):
        """Connect to the selected server"""
        selection = self.network_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_tags = self.network_tree.item(item)['tags']
        
        if 'server' in item_tags:
            server = self.network_tree.item(item)['text']
            if server not in self.connections:
                # Show connect dialog for this server
                self.add_status_message(f"Use /server {server} port nickname to connect")
            else:
                self.add_status_message(f"Already connected to {server}")
                
    def disconnect_selected(self):
        """Disconnect from the selected server"""
        selection = self.network_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_tags = self.network_tree.item(item)['tags']
        
        if 'server' in item_tags:
            server = self.network_tree.item(item)['text']
            if server in self.connections:
                self.quit_server(server, "Disconnecting")
            else:
                self.add_status_message(f"Not connected to {server}")
                
    def close_selected(self):
        """Close the selected window or tab"""
        selection = self.network_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_tags = self.network_tree.item(item)['tags']
        item_text = self.network_tree.item(item)['text']
        
        if 'channel' in item_tags:
            # Get the server from the parent
            parent = self.network_tree.parent(item)
            server = self.network_tree.item(parent)['text']
            
            # Create channel key
            channel_key = f"{server}:{item_text}"
            if channel_key in self.channel_windows:
                # Part the channel
                self.send_command(f"PART {item_text}", server)
                # Close the tab - pass channel and server separately instead of channel_key
                self.close_channel_tab(item_text, server)
                
        elif 'pm' in item_tags:
            # Extract the username from "PM: username"
            username = item_text.replace("PM: ", "")
            
            # Get the server from the parent
            parent = self.network_tree.parent(item)
            server = self.network_tree.item(parent)['text']
            
            # Create the pm_key
            pm_key = f"{server}:{username}"
            if pm_key in self.private_windows:
                self.close_pm_tab(pm_key)
     
    def on_exit(self):
        """Handle application exit"""
        # Disconnect from all servers
        for server in list(self.connections.keys()):
            try:
                self.quit_server(server, "Client closing")
            except:
                pass
            
        # Destroy the main window
        self.window.destroy()

    # Add these methods for UI responsiveness
    def process_deferred_ui_tasks(self):
        """Process UI tasks in small chunks to avoid freezing the GUI"""
        try:
            # Process Tkinter events to keep UI responsive
            self.window.update_idletasks()
        except Exception as e:
            print(f"Error in process_deferred_ui_tasks: {e}")
        finally:
            # Re-schedule this method to run periodically
            self.window.after(50, self.process_deferred_ui_tasks)
    
    def run_with_busy_cursor(self, func, *args, **kwargs):
        """Run a function with busy cursor to indicate processing
        
        Args:
            func: The function to run
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        original_cursor = self.window.cget("cursor")
        try:
            # Show busy cursor
            self.window.config(cursor="watch")
            self.window.update_idletasks()
            
            # Call the function
            result = func(*args, **kwargs)
            
            return result
        finally:
            # Restore original cursor
            self.window.config(cursor=original_cursor)
            self.window.update_idletasks()
    
    def run_in_thread(self, func, callback=None, *args, **kwargs):
        """Run a function in a background thread to avoid blocking the GUI
        
        Args:
            func: The function to run in the background
            callback: Optional function to call in the main thread when done
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        def thread_func():
            try:
                result = func(*args, **kwargs)
                
                # If callback provided, schedule it in the main thread
                if callback:
                    self.window.after(0, lambda: callback(result))
            except Exception as e:
                print(f"Error in background thread: {e}")
                import traceback
                traceback.print_exc()
        
        # Start the thread
        thread = threading.Thread(target=thread_func)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def _add_channel_message_gui(self, channel_key, message, tag):
        """Internal method to add channel message in GUI thread"""
        if channel_key in self.channel_windows:
            # Get the channel info
            channel_info = self.channel_windows[channel_key]
            chat_display = channel_info['chat_display']
            
            # Add timestamp
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            chat_display.insert(tk.END, f"{timestamp} ", 'timestamp')
            
            # Add message with tag if specified
            if tag:
                chat_display.insert(tk.END, f"{message}\n", tag)
            else:
                # Parse for username if message is in format "username: message"
                if ': ' in message:
                    username, text = message.split(': ', 1)
                    current_nick = self.connections.get(channel_key.split(':')[0], {}).get('nickname', '')
                    
                    if username == current_nick:
                        chat_display.insert(tk.END, f"{username}: ", 'my_username')
                    else:
                        chat_display.insert(tk.END, f"{username}: ", 'username')
                    
                    chat_display.insert(tk.END, f"{text}\n", 'message')
                else:
                    chat_display.insert(tk.END, f"{message}\n", 'message')
            
            # Scroll to bottom
            chat_display.see(tk.END)
    
    def add_channel_message(self, channel_key, message, tag=None):
        """Add a message to a channel tab (thread-safe)
        
        Args:
            channel_key: The channel key in format server:channel
            message: The message to add
            tag: Optional tag for styling
        """
        try:
            # Schedule GUI update on main thread
            self.window.after(0, self._add_channel_message_gui, channel_key, message, tag)
        except Exception as e:
            print(f"Error scheduling channel message: {e}")
            
    def _add_channel_action_gui(self, channel_key, sender, action_text):
        """Internal method to add channel action in GUI thread"""
        if channel_key in self.channel_windows:
            channel_info = self.channel_windows[channel_key]
            chat_display = channel_info['chat_display']
            
            # Add timestamp
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            chat_display.insert(tk.END, f"{timestamp} ", 'timestamp')
            
            # Add action
            chat_display.insert(tk.END, f"* {sender} {action_text}\n", 'action')
            
            # Scroll to bottom
            chat_display.see(tk.END)
    
    def add_channel_action(self, channel_key, sender, action_text):
        """Add an action message to a channel tab (thread-safe)
        
        Args:
            channel_key: The channel key in format server:channel
            sender: The username performing the action
            action_text: The action text
        """
        try:
            # Schedule GUI update on main thread
            self.window.after(0, self._add_channel_action_gui, channel_key, sender, action_text)
        except Exception as e:
            print(f"Error scheduling channel action: {e}")
            
    def _add_pm_message_gui(self, pm_key, message, tag):
        """Internal method to add PM message in GUI thread"""
        if pm_key in self.private_windows:
            # Get the PM info
            pm_info = self.private_windows[pm_key]
            chat_display = pm_info['chat_display']
            
            # Add timestamp
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            chat_display.insert(tk.END, f"{timestamp} ", 'timestamp')
            
            # Add message with tag if specified
            if tag:
                chat_display.insert(tk.END, f"{message}\n", tag)
            else:
                # Parse for username if message is in format "username: message"
                if ': ' in message:
                    username, text = message.split(': ', 1)
                    current_nick = self.connections.get(pm_key.split(':')[0], {}).get('nickname', '')
                    
                    if username == current_nick:
                        chat_display.insert(tk.END, f"{username}: ", 'my_username')
                    else:
                        chat_display.insert(tk.END, f"{username}: ", 'username')
                    
                    chat_display.insert(tk.END, f"{text}\n", 'message')
                else:
                    chat_display.insert(tk.END, f"{message}\n", 'message')
            
            # Scroll to bottom
            chat_display.see(tk.END)
    
    def add_pm_message(self, pm_key, message, tag=None):
        """Add a message to a private message tab (thread-safe)
        
        Args:
            pm_key: The PM key in format server:username
            message: The message to add
            tag: Optional tag for styling
        """
        try:
            # Schedule GUI update on main thread
            self.window.after(0, self._add_pm_message_gui, pm_key, message, tag)
        except Exception as e:
            print(f"Error scheduling PM message: {e}")
            
    def _add_pm_action_gui(self, pm_key, sender, action_text):
        """Internal method to add PM action in GUI thread"""
        if pm_key in self.private_windows:
            pm_info = self.private_windows[pm_key]
            chat_display = pm_info['chat_display']
            
            # Add timestamp
            timestamp = datetime.now().strftime("[%H:%M:%S]")
            chat_display.insert(tk.END, f"{timestamp} ", 'timestamp')
            
            # Add action
            chat_display.insert(tk.END, f"* {sender} {action_text}\n", 'action')
            
            # Scroll to bottom
            chat_display.see(tk.END)
    
    def add_pm_action(self, pm_key, sender, action_text):
        """Add an action message to a private message tab (thread-safe)
        
        Args:
            pm_key: The PM key in format server:username
            sender: The username performing the action
            action_text: The action text
        """
        try:
            # Schedule GUI update on main thread
            self.window.after(0, self._add_pm_action_gui, pm_key, sender, action_text)
        except Exception as e:
            print(f"Error scheduling PM action: {e}")

    def update_channel_users(self, channel_key):
        """Update the users listbox for a channel if needed"""
        # Use run_in_thread to avoid blocking the GUI during user list updates
        self.run_in_thread(
            lambda: self._force_update_users_for_channel(channel_key)
        )
    
    def _force_update_users_for_channel(self, channel_key):
        """Forcefully update the users listbox for a channel without any conditions"""
        try:
            if channel_key not in self.channel_windows:
                return
                
            channel_info = self.channel_windows[channel_key]
            
            # Make sure users set exists
            if 'users' not in channel_info:
                channel_info['users'] = set()
                
            # Get the users list and sort with @ and + first
            users = sorted(list(channel_info['users']), 
                          key=lambda u: (
                              0 if u.startswith('@') else (1 if u.startswith('+') else 2),  # First sort by prefix type
                              u.lstrip('@+').lower()  # Then by nickname alphabetically
                          ))
            
            # If there are too many users, use batched updates
            if len(users) > 100:
                # Schedule batched update on the main thread
                self.window.after(0, lambda: self._batched_user_update(channel_key, users))
                return
            
            # For smaller lists, update directly
            # Make sure users_listbox exists
            if 'users_listbox' not in channel_info:
                return
                
            users_listbox = channel_info['users_listbox']
            
            # Update UI in the main thread
            def update_ui():
                # Clear the listbox
                users_listbox.delete(0, tk.END)
                
                # Batch insert users - more efficient than one at a time
                for i, user in enumerate(users):
                    users_listbox.insert(tk.END, user)
                    # Set color based on user prefix
                    if user.startswith('@'):
                        users_listbox.itemconfig(i, foreground='yellow')  # Ops
                    elif user.startswith('+'):
                        users_listbox.itemconfig(i, foreground='cyan')    # Voice
                    else:
                        users_listbox.itemconfig(i, foreground='white')   # Regular users
                
                # Make sure to update the users count label with the exact number of users displayed
                actual_count = users_listbox.size()
                if 'users_label' in channel_info:
                    channel_info['users_label'].config(text=f"Users: {actual_count}")
            
            # Schedule UI update on the main thread
            self.window.after(0, update_ui)
                
        except Exception as e:
            print(f"Error updating users list: {e}")
            import traceback
            traceback.print_exc()
    
    def _batched_user_update(self, channel_key, users=None):
        """Update users listbox in batches to prevent UI freezing
        
        Args:
            channel_key: The channel key to update
            users: Optional pre-sorted user list 
        """
        try:
            if channel_key not in self.channel_windows:
                return
                
            channel_info = self.channel_windows[channel_key]
            
            # Get users set if not provided
            if users is None:
                users = sorted(list(channel_info.get('users', set())), # Use .get for safety 
                             key=lambda u: (
                                 0 if u.startswith('@') else (1 if u.startswith('+') else 2),
                                 u.lstrip('@+').lower()
                             ))
            
            # Make sure users_listbox exists
            if 'users_listbox' not in channel_info:
                return
                
            users_listbox = channel_info['users_listbox']
            
            # Clear the listbox first
            users_listbox.delete(0, tk.END)
            
            # Store state for batched processing
            batch_state = {
                'users': users,
                'current_index': 0,
                'batch_size': 50,  # Process 50 users at a time
                'total_inserted': 0  # Keep track of actual inserted users
            }
            
            # Define function to process one batch
            def process_batch():
                # Check if channel info still exists (window might close during batch)
                if channel_key not in self.channel_windows:
                    return 
                current_channel_info = self.channel_windows[channel_key]

                if batch_state['current_index'] >= len(batch_state['users']):
                    # Done - update the count with the ACTUAL number of users in the listbox
                    if 'users_label' in current_channel_info:
                        try:
                            # Make sure listbox still exists before getting size
                            if users_listbox.winfo_exists():
                                actual_count = users_listbox.size()
                                current_channel_info['users_label'].config(text=f"Users: {actual_count}")
                        except tk.TclError:
                             # Handle potential error if widget is destroyed during update
                             pass
                    return
                
                # Process next batch
                start_idx = batch_state['current_index']
                end_idx = min(start_idx + batch_state['batch_size'], len(batch_state['users']))
                
                # Check if listbox still exists before inserting
                if not users_listbox.winfo_exists():
                    return 

                try:
                    for i in range(start_idx, end_idx):
                        user = batch_state['users'][i]
                        users_listbox.insert(tk.END, user)
                        idx = users_listbox.size() - 1
                        batch_state['total_inserted'] += 1
                        
                        # Set color based on user prefix
                        if user.startswith('@'):
                            users_listbox.itemconfig(idx, foreground='yellow')  # Ops
                        elif user.startswith('+'):
                            users_listbox.itemconfig(idx, foreground='cyan')    # Voice
                        else:
                            users_listbox.itemconfig(idx, foreground='white')   # Regular users
                    
                    # Remove the label update from inside the loop
                    # if 'users_label' in current_channel_info:
                    #     current_channel_info['users_label'].config(text=f"Users: {batch_state['total_inserted']}")
                    
                    # Update index for next batch
                    batch_state['current_index'] = end_idx
                    
                    # Schedule next batch - use short delay to allow UI to breathe
                    self.window.after(10, process_batch)
                except tk.TclError:
                    # Handle error if listbox is destroyed during insertion
                    print(f"Warning: Listbox for {channel_key} destroyed during batched update.")
                    return

            # Start batch processing
            self.window.after(0, process_batch)
            
        except Exception as e:
            print(f"Error in batched user update: {e}")
            import traceback
            traceback.print_exc()

    def toggle_tabs(self):
        """Toggle the visibility of tabs"""
        self.tabs_visible = not self.tabs_visible
        if self.tabs_visible:
            self.show_tabs()
        else:
            self.hide_tabs()
        # Save preference
        self.preferences['show_tabs'] = self.tabs_visible
        self.add_status_message(f"Tabs {'shown' if self.tabs_visible else 'hidden'}", 'status')

    def show_tabs(self):
        """Show the tabs in the notebook"""
        style = ttk.Style()
        style.layout('TNotebook.Tab', [])  # Remove the empty layout
        style.layout('TNotebook.Tab', [
            ('Notebook.tab', {
                'sticky': 'nswe',
                'children': [
                    ('Notebook.padding', {
                        'sticky': 'nswe',
                        'children': [
                            ('Notebook.label', {'sticky': 'nswe'})
                        ]
                    })
                ]
            })
        ])

    def hide_tabs(self):
        """Hide the tabs in the notebook"""
        style = ttk.Style()
        style.layout('TNotebook.Tab', [])  # Empty layout removes the tabs

    def close_pm_tab(self, username_or_pm_key, server=None):
        """Close a PM tab and clean up resources
        
        Can be called with either:
        - close_pm_tab(pm_key): where pm_key is in format "server:username"
        - close_pm_tab(username, server): with username and server as separate parameters
        """
        try:
            # Handle both calling patterns
            if server is None:
                # Called with pm_key
                pm_key = username_or_pm_key
                if ":" in pm_key:
                    server, username = pm_key.split(":", 1)
                else:
                    print(f"Invalid PM key format: {pm_key}")
                    return
            else:
                # Called with username, server
                username = username_or_pm_key
                pm_key = f"{server}:{username}"
                
            self.add_status_message(f"Closing PM with: {username}")

            # Remove PM node from tree
            server_data = self.server_nodes.get(server)
            if server_data and username in server_data.get('private_msgs', {}):
                try:
                    pm_node = server_data['private_msgs'][username]
                    self.network_tree.delete(pm_node)
                except Exception as e:
                    print(f"Error removing PM node: {e}")
                del server_data['private_msgs'][username]

            # Close the tab/window
            if pm_key in self.private_windows:
                pm_info = self.private_windows[pm_key]
                
                # Remove tab from notebook if it exists
                if 'tab' in pm_info and pm_info['tab'] in self.notebook.tabs():
                    self.notebook.forget(pm_info['tab'])
                
                # Delete PM info from dictionary
                del self.private_windows[pm_key]
                
                # Remove from tabs dictionary
                if f"pm:{username}" in self.tabs:
                    del self.tabs[f"pm:{username}"]
                
                # Select status tab if no other tabs remain
                if len(self.notebook.tabs()) == 1:
                    self.select_tab('status')
            else:
                print(f"PM {pm_key} not found in private_windows")
        except Exception as e:
            print(f"Error closing PM tab: {e}")
            traceback.print_exc()

    def get_channel_info(self, channel_key):
        """Retrieve channel info dictionary safely."""
        return self.channel_windows.get(channel_key)

    def get_private_window_info(self, pm_key):
        """Retrieve private window info dictionary safely."""
        return self.private_windows.get(pm_key)

    # --- User List Context Menu Helper Methods ---

    def _get_selected_user_from_list(self, channel_key):
        """Helper to get the selected username and listbox from a channel."""
        if channel_key not in self.channel_windows:
            self.add_status_message(f"Error: Channel key {channel_key} not found.", 'error')
            return None, None, None

        channel_info = self.channel_windows[channel_key]
        users_listbox = channel_info.get('users_listbox')

        if not users_listbox or not users_listbox.winfo_exists():
            self.add_status_message("Error: User listbox not found or invalid for channel.", 'error')
            return None, None, None

        selected_indices = users_listbox.curselection()
        if not selected_indices:
            return None, None, users_listbox # Return listbox even if no selection

        selected_user_raw = users_listbox.get(selected_indices[0])
        username = selected_user_raw.lstrip('@+') # Remove status prefix
        return username, selected_user_raw, users_listbox

    def whois_from_userlist(self, channel_key):
        """Perform WHOIS on the selected user in a channel list."""
        try:
            username, _, _ = self._get_selected_user_from_list(channel_key)
            if not username:
                return # Error or no selection handled in helper

            server = channel_key.split(':', 1)[0]
            self.send_command(f"WHOIS {username}", server)
            self.add_channel_message(channel_key, f"* Sent WHOIS request for {username}", 'status')
        except Exception as e:
            self.add_status_message(f"Error in whois_from_userlist: {e}", 'error')
            traceback.print_exc()

    def op_from_userlist(self, channel_key):
        """Give OP status to selected user from the channel's user list."""
        try:
            username, selected_user_raw, _ = self._get_selected_user_from_list(channel_key)
            if not username:
                return

            server, channel = channel_key.split(':', 1)

            if selected_user_raw.startswith('@'):
                 self.add_channel_message(channel_key, f"{username} is already an operator.", 'error')
                 return

            self.send_command(f"MODE {channel} +o {username}", server)
            self.add_channel_message(channel_key, f"* Attempting to give op status to {username}", 'status')
        except Exception as e:
            self.add_status_message(f"Error in op_from_userlist: {e}", 'error')
            traceback.print_exc()

    def deop_from_userlist(self, channel_key):
        """Remove OP status from selected user."""
        try:
            username, selected_user_raw, _ = self._get_selected_user_from_list(channel_key)
            if not username:
                return

            server, channel = channel_key.split(':', 1)

            if not selected_user_raw.startswith('@'):
                 self.add_channel_message(channel_key, f"{username} is not an operator.", 'error')
                 return

            self.send_command(f"MODE {channel} -o {username}", server)
            self.add_channel_message(channel_key, f"* Attempting to remove op status from {username}", 'status')
        except Exception as e:
            self.add_status_message(f"Error in deop_from_userlist: {e}", 'error')
            traceback.print_exc()

    def voice_from_userlist(self, channel_key):
        """Give voice status to selected user."""
        try:
            username, selected_user_raw, _ = self._get_selected_user_from_list(channel_key)
            if not username:
                return

            server, channel = channel_key.split(':', 1)

            if selected_user_raw.startswith(('+', '@')): # Ops also have voice
                 self.add_channel_message(channel_key, f"{username} already has voice.", 'error')
                 return

            self.send_command(f"MODE {channel} +v {username}", server)
            self.add_channel_message(channel_key, f"* Attempting to give voice status to {username}", 'status')
        except Exception as e:
            self.add_status_message(f"Error in voice_from_userlist: {e}", 'error')
            traceback.print_exc()

    def devoice_from_userlist(self, channel_key):
        """Remove voice status from selected user."""
        try:
            username, selected_user_raw, _ = self._get_selected_user_from_list(channel_key)
            if not username:
                return

            server, channel = channel_key.split(':', 1)

            if not selected_user_raw.startswith('+'):
                 self.add_channel_message(channel_key, f"{username} does not have voice.", 'error')
                 return

            self.send_command(f"MODE {channel} -v {username}", server)
            self.add_channel_message(channel_key, f"* Attempting to remove voice status from {username}", 'status')
        except Exception as e:
            self.add_status_message(f"Error in devoice_from_userlist: {e}", 'error')
            traceback.print_exc()

    def kick_from_userlist(self, channel_key):
        """Kick the selected user from the channel."""
        try:
            username, selected_user_raw, users_listbox = self._get_selected_user_from_list(channel_key)
            if not username:
                return

            server, channel = channel_key.split(':', 1)
            current_nick = self.connections[server]['nickname']

            if username == current_nick:
                 self.add_channel_message(channel_key, f"You cannot kick yourself.", 'error')
                 return

            # Create dialog for kick reason
            reason_dialog = tk.Toplevel(self.window) # Use main window as parent
            reason_dialog.title("Kick Reason")
            reason_dialog.geometry("300x100")
            reason_dialog.transient(self.window) # Make it modal relative to main window
            reason_dialog.grab_set()

            ttk.Label(reason_dialog, text="Reason:").pack(pady=5)
            reason_entry = ttk.Entry(reason_dialog, width=40)
            reason_entry.pack(pady=5)
            reason_entry.focus()

            def do_kick():
                reason = reason_entry.get() or "Kicked"
                self.send_command(f"KICK {channel} {username} :{reason}", server)
                self.add_channel_message(channel_key, f"* Attempting to kick {username} ({reason})", 'kick')
                reason_dialog.destroy()

            ttk.Button(reason_dialog, text="Kick", command=do_kick).pack(pady=5)
            reason_entry.bind('<Return>', lambda e: do_kick())

        except Exception as e:
            self.add_status_message(f"Error in kick_from_userlist: {e}", 'error')
            traceback.print_exc()

    def ban_from_userlist(self, channel_key):
        """Ban the selected user from the channel."""
        try:
            username, selected_user_raw, users_listbox = self._get_selected_user_from_list(channel_key)
            if not username:
                return

            server, channel = channel_key.split(':', 1)
            current_nick = self.connections[server]['nickname']

            if username == current_nick:
                 self.add_channel_message(channel_key, f"You cannot ban yourself.", 'error')
                 return

            # Create dialog for ban options (Simplified: just ban nick!*@*)
            ban_dialog = tk.Toplevel(self.window)
            ban_dialog.title(f"Ban {username} Options")
            ban_dialog.geometry("300x150")
            ban_dialog.transient(self.window)
            ban_dialog.grab_set()

            ttk.Label(ban_dialog, text=f"Ban mask: {username}!*@*").pack(pady=5)

            kick_after = tk.BooleanVar(value=True)
            ttk.Checkbutton(ban_dialog, text="Kick after ban", variable=kick_after).pack(pady=5)

            ttk.Label(ban_dialog, text="Reason:").pack(pady=5)
            reason_entry = ttk.Entry(ban_dialog, width=40)
            reason_entry.pack(pady=5)

            def do_ban():
                reason = reason_entry.get() or "Banned"
                ban_mask = f"{username}!*@*"
                self.send_command(f"MODE {channel} +b {ban_mask}", server)
                self.add_channel_message(channel_key, f"* Set ban on {ban_mask}", 'ban')

                if kick_after.get():
                    self.send_command(f"KICK {channel} {username} :{reason}", server)
                    self.add_channel_message(channel_key, f"* Attempting to kick {username} ({reason})", 'kick')

                ban_dialog.destroy()

            ttk.Button(ban_dialog, text="Ban", command=do_ban).pack(pady=10)

        except Exception as e:
            self.add_status_message(f"Error in ban_from_userlist: {e}", 'error')
            traceback.print_exc()

    # --- End User List Helpers ---

# --- Channel List Window Class ---
class ChannelListWindow:
    def __init__(self, irc_client, server):
        self.irc_client = irc_client
        self.server = server
        self.full_channel_list = [] # Store tuples: (channel, users, topic)

        # Create Toplevel window
        self.window = tk.Toplevel(irc_client.window)
        self.window.title(f"Channel List - {server}")
        self.window.geometry("700x500")
        self.window.transient(irc_client.window)

        # Top frame for search
        search_frame = ttk.Frame(self.window, padding=5)
        search_frame.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(search_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_var.trace_add("write", self.filter_list)

        # Treeview frame
        tree_frame = ttk.Frame(self.window)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview scrollbars
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview widget
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("channel", "users", "topic"),
            show="headings",
            yscrollcommand=tree_scrollbar_y.set,
            xscrollcommand=tree_scrollbar_x.set
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar_y.config(command=self.tree.yview)
        tree_scrollbar_x.config(command=self.tree.xview)

        # Define headings
        self.tree.heading("channel", text="Channel")
        self.tree.heading("users", text="Users")
        self.tree.heading("topic", text="Topic")

        # Define column properties
        self.tree.column("channel", anchor=tk.W, width=150)
        self.tree.column("users", anchor=tk.E, width=60)
        self.tree.column("topic", anchor=tk.W, width=450)

        # Bind double-click to join
        self.tree.bind("<Double-1>", self.join_selected)

        # Bottom frame for buttons
        button_frame = ttk.Frame(self.window, padding=5)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(button_frame, text="Requesting list...")
        self.status_label.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="Close", command=self.on_closing).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Join", command=self.join_selected).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Refresh", command=self.request_list).pack(side=tk.RIGHT)

        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initial request
        self.request_list()

    def request_list(self):
        """Clear list and send LIST command to server."""
        self.clear_list()
        self.status_label.config(text="Requesting list...")
        self.irc_client.send_command("LIST", self.server)

    def clear_list(self):
        """Clear the treeview and the internal data list."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.full_channel_list = []

    def add_channel_entry(self, channel, users, topic):
        """Add a channel entry to the internal list and potentially the treeview."""
        self.full_channel_list.append((channel, users, topic))
        # Add to treeview only if it matches current filter (or if filter is empty)
        search_term = self.search_var.get().lower()
        if not search_term or search_term in channel.lower() or search_term in topic.lower():
            self.tree.insert("", tk.END, values=(channel, users, topic))

    def list_complete(self):
        """Called when RPL_LISTEND is received."""
        self.status_label.config(text=f"List complete ({len(self.full_channel_list)} channels)")

    def filter_list(self, *args):
        """Filter the treeview based on the search entry."""
        search_term = self.search_var.get().lower()

        # Clear current treeview items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Repopulate with filtered items from full list
        for channel, users, topic in self.full_channel_list:
            if not search_term or search_term in channel.lower() or search_term in topic.lower():
                self.tree.insert("", tk.END, values=(channel, users, topic))

    def join_selected(self, event=None):
        """Join the currently selected channel in the treeview."""
        selected_item = self.tree.focus() # Get selected item ID
        if not selected_item:
            return
        item_values = self.tree.item(selected_item)['values']
        if not item_values:
            return

        channel_name = item_values[0]
        if channel_name:
            self.irc_client.process_command(f"/join {channel_name}", self.server)
            # Optional: Close list window after joining
            # self.on_closing()

    def on_closing(self):
        """Clean up when the window is closed."""
        # Remove reference from IRCClient
        if self.server in self.irc_client.channel_list_windows:
            del self.irc_client.channel_list_windows[self.server]
        # Destroy window
        try:
            if self.window.winfo_exists():
                self.window.destroy()
        except tk.TclError:
            pass # Window might already be destroyed

# --- Network List Dialog Classes ---
class AddEditNetworkDialog(tk.Toplevel):
    """Dialog for adding or editing network details."""
    def __init__(self, parent, theme, title="Network Details", network_info=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.result = None # Store the entered data
        self.geometry("400x250")

        # Apply theme background
        self.configure(bg=theme.get('bg', 'SystemButtonFace'))

        # --- Widgets ---
        frame = ttk.Frame(self, padding=10)
        # frame.configure(style='Themed.TFrame') # Alternative using style if defined
        frame.pack(fill=tk.BOTH, expand=True)

        # Configure frame background if needed (ttk might inherit)
        # frame.configure(bg=theme.get('bg')) # Less reliable for ttk

        # Use theme colors for labels and entries (ttk styling preferred but direct config shown)
        label_fg = theme.get('fg', 'black')
        entry_bg = theme.get('entry_bg', theme.get('bg', 'white')) # Use specific entry bg or main bg
        entry_fg = theme.get('fg', 'black')

        ttk.Label(frame, text="Network Name:", foreground=label_fg).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.grid(row=0, column=1, pady=2)
        # Style entries if needed: self.name_entry.configure(foreground=entry_fg, background=entry_bg)

        ttk.Label(frame, text="Server Address:", foreground=label_fg).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.server_entry = ttk.Entry(frame, width=40)
        self.server_entry.grid(row=1, column=1, pady=2)

        ttk.Label(frame, text="Port(s):", foreground=label_fg).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.port_entry = ttk.Entry(frame, width=40)
        self.port_entry.grid(row=2, column=1, pady=2)

        ttk.Label(frame, text="Auto-Join Channels:", foreground=label_fg).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.channels_entry = ttk.Entry(frame, width=40)
        self.channels_entry.grid(row=3, column=1, pady=2)
        ttk.Label(frame, text="(comma-separated, e.g., #chan1,#chan2)", foreground=label_fg).grid(row=4, column=1, sticky=tk.W, pady=(0, 5))

        # --- Populate if editing ---
        if network_info:
            self.name_entry.insert(0, network_info.get('name', ''))
            self.server_entry.insert(0, network_info.get('server', ''))
            self.port_entry.insert(0, network_info.get('port', '6667'))
            self.channels_entry.insert(0, network_info.get('channels', ''))

        # --- Buttons ---
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window(self) # Wait until dialog is closed

    def on_ok(self):
        name = self.name_entry.get().strip()
        server = self.server_entry.get().strip()
        port_str = self.port_entry.get().strip() or "6667"
        channels = self.channels_entry.get().strip()

        if not name or not server:
            # Show error message (implementation omitted for brevity)
            print("Error: Network Name and Server Address are required.")
            return

        # Basic port validation (can be improved)
        try:
            # Allow comma-separated ports, but only validate the first for now
            first_port = int(port_str.split(',')[0].strip())
            if not 1 <= first_port <= 65535:
                raise ValueError()
        except ValueError:
            print(f"Error: Invalid Port number: {port_str}")
            return

        self.result = {
            'name': name,
            'server': server,
            'port': port_str,
            'channels': channels
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

class NetworkListWindow(tk.Toplevel):
    CONFIG_FILE = "network_config.json"

    def __init__(self, irc_client, theme):
        super().__init__(irc_client.window)
        self.irc_client = irc_client
        self.theme = theme # Store the theme
        self.config_data = {"user_info": {}, "networks": []} # Holds loaded/current config
        self.selected_network_index = None

        self.title("Network List")
        self.geometry("550x450")
        self.transient(irc_client.window)
        self.grab_set()

        # --- Apply Theme Colors ---
        bg_color = theme.get('bg', 'SystemButtonFace')
        fg_color = theme.get('fg', 'black')
        list_bg = theme.get('list_bg', bg_color) # Specific list bg or main bg
        list_fg = theme.get('list_fg', fg_color) # Specific list fg or main fg
        list_select_bg = theme.get('select_bg', '#333333') # Selection color

        self.configure(bg=bg_color)

        # --- Main Frames ---
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        network_frame = ttk.Frame(self, padding=10)
        network_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # --- User Information (Top Frame) ---
        user_info_frame = ttk.LabelFrame(top_frame, text="User Information", padding=5)
        user_info_frame.pack(fill=tk.X)
        # user_info_frame.configure(style='Themed.TLabelframe') # If using ttk styles

        # Apply theme to labels/entries within user info
        ttk.Label(user_info_frame, text="Nick name:", foreground=fg_color).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.nick1_entry = ttk.Entry(user_info_frame, width=30)
        self.nick1_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(user_info_frame, text="Second choice:", foreground=fg_color).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.nick2_entry = ttk.Entry(user_info_frame, width=30)
        self.nick2_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(user_info_frame, text="Third choice:", foreground=fg_color).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.nick3_entry = ttk.Entry(user_info_frame, width=30)
        self.nick3_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(user_info_frame, text="User name:", foreground=fg_color).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.username_entry = ttk.Entry(user_info_frame, width=30)
        self.username_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)

        user_info_frame.columnconfigure(1, weight=1)

        # --- Networks (Middle Frame) ---
        networks_label_frame = ttk.LabelFrame(network_frame, text="Networks", padding=5)
        networks_label_frame.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.Frame(networks_label_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        button_list_frame = ttk.Frame(networks_label_frame)
        button_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))

        # Listbox Scrollbar
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox - Apply theme colors directly to tk.Listbox
        self.network_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=list_scrollbar.set,
            exportselection=False, # Prevent selection loss when focus moves
            bg=list_bg,
            fg=list_fg,
            selectbackground=list_select_bg,
            selectforeground=list_fg,
            borderwidth=0,
            highlightthickness=0
        )
        self.network_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.config(command=self.network_listbox.yview)
        self.network_listbox.bind('<<ListboxSelect>>', self.on_network_select)

        # Network Buttons
        ttk.Button(button_list_frame, text="Add...", command=self.add_network).pack(fill=tk.X, pady=2)
        self.remove_button = ttk.Button(button_list_frame, text="Remove", command=self.remove_network, state=tk.DISABLED)
        self.remove_button.pack(fill=tk.X, pady=2)
        self.edit_button = ttk.Button(button_list_frame, text="Edit...", command=self.edit_network, state=tk.DISABLED)
        self.edit_button.pack(fill=tk.X, pady=2)

        # --- Bottom Buttons ---
        self.connect_button = ttk.Button(bottom_frame, text="Connect", command=self.connect_selected, state=tk.DISABLED)
        self.connect_button.pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="Close", command=self.on_closing).pack(side=tk.RIGHT)

        # --- Load Data ---
        self.load_data_to_gui()

        # --- Window Closing Handler ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data_to_gui(self):
        """Load config from file and populate the GUI elements."""
        self.config_data = self.irc_client.load_network_config() # Use client method

        # Populate User Info
        user_info = self.config_data.get('user_info', {})
        self.nick1_entry.delete(0, tk.END)
        self.nick1_entry.insert(0, user_info.get('nick1', 'PythonUser'))
        self.nick2_entry.delete(0, tk.END)
        self.nick2_entry.insert(0, user_info.get('nick2', ''))
        self.nick3_entry.delete(0, tk.END)
        self.nick3_entry.insert(0, user_info.get('nick3', ''))
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, user_info.get('username', 'PythonUser'))

        # Populate Network Listbox
        self.network_listbox.delete(0, tk.END)
        for network in self.config_data.get('networks', []):
            self.network_listbox.insert(tk.END, network.get('name', '?'))

        self.update_button_states()

    def save_data_from_gui(self):
        """Read data from GUI and prepare config dictionary for saving."""
        print("DEBUG: save_data_from_gui called") # <-- Debug print
        user_info = {
            'nick1': self.nick1_entry.get(),
            'nick2': self.nick2_entry.get(),
            'nick3': self.nick3_entry.get(),
            'username': self.username_entry.get()
        }
        # Note: self.config_data['networks'] is updated by Add/Remove/Edit methods
        self.config_data['user_info'] = user_info
        print(f"DEBUG: Data being passed to save_network_config: {self.config_data}") # <-- Debug print
        self.irc_client.save_network_config(self.config_data) # Use client method

    def update_button_states(self):
        """Enable/disable buttons based on listbox selection."""
        if self.selected_network_index is not None:
            self.remove_button.config(state=tk.NORMAL)
            self.edit_button.config(state=tk.NORMAL)
            self.connect_button.config(state=tk.NORMAL)
        else:
            self.remove_button.config(state=tk.DISABLED)
            self.edit_button.config(state=tk.DISABLED)
            self.connect_button.config(state=tk.DISABLED)

    def on_network_select(self, event):
        """Handle selection change in the network listbox."""
        selection = self.network_listbox.curselection()
        if selection:
            self.selected_network_index = selection[0]
        else:
            self.selected_network_index = None
        self.update_button_states()

    def add_network(self):
        """Open dialog to add a new network."""
        # Pass self (the NetworkListWindow instance) as the parent, not self.window
        dialog = AddEditNetworkDialog(self, self.theme, title="Add Network") # Pass theme
        if dialog.result:
            # --- Debug Prints --- 
            print(f"DEBUG: Adding network: {dialog.result}") 
            print(f"DEBUG: self.config_data['networks'] BEFORE append: {self.config_data['networks']}")
            # --- End Debug --- 
            self.config_data['networks'].append(dialog.result)
            # --- Debug Prints --- 
            print(f"DEBUG: self.config_data['networks'] AFTER append: {self.config_data['networks']}")
            # --- End Debug --- 
            self.network_listbox.insert(tk.END, dialog.result['name'])
            # Optionally select the newly added item
            self.network_listbox.selection_clear(0, tk.END)

    def remove_network(self):
        """Remove the selected network."""
        if self.selected_network_index is None:
            return
        del self.config_data['networks'][self.selected_network_index]
        self.network_listbox.delete(self.selected_network_index)
        self.selected_network_index = None
        self.update_button_states()

    def edit_network(self):
        """Open dialog to edit the selected network."""
        if self.selected_network_index is None:
            return
        current_info = self.config_data['networks'][self.selected_network_index]

        # Pass self (the NetworkListWindow instance) as the parent, not self.window
        dialog = AddEditNetworkDialog(self, self.theme, title="Edit Network", network_info=current_info) # Pass theme
        if dialog.result:
            # Update the stored data
            self.config_data['networks'][self.selected_network_index] = dialog.result

    def connect_selected(self, event=None):
        """Connect to the selected network."""
        if self.selected_network_index is None:
            return
        network_info = self.config_data['networks'][self.selected_network_index]
        user_info = self.config_data.get('user_info', {})

        server = network_info.get('server')
        port_str = network_info.get('port', '6667')
        # Use the first port if multiple are comma-separated
        try:
            port = int(port_str.split(',')[0].strip())
        except ValueError:
            self.irc_client.add_status_message(f"Invalid port '{port_str}' for network {network_info.get('name')}. Using 6667.", 'error')
            port = 6667

        # Choose nickname
        nick = user_info.get('nick1') or self.irc_client.default_nickname
        # TODO: Add logic to try nick2, nick3 if nick1 is taken (requires server feedback)

        if not server:
            self.irc_client.add_status_message(f"Server address missing for network {network_info.get('name')}. Cannot connect.", 'error')
            return

        # Trigger connection via IRCClient
        self.irc_client.connect_to_server(server, port, nick)
        # TODO: Handle auto-join channels after connection is successful

        self.on_closing(save=False) # Close window without saving again

    def on_closing(self, save=True):
        """Save data and destroy the window."""
        print(f"DEBUG: NetworkListWindow on_closing called (save={save})") # <-- Debug print
        if save:
            self.save_data_from_gui()
        # Remove reference from client
        if hasattr(self.irc_client, 'network_list_window') and self.irc_client.network_list_window == self:
            self.irc_client.network_list_window = None
        try:
            self.destroy()
        except tk.TclError:
            pass

    # --- Network Config Load/Save ---
    def load_network_config(self):
        """Loads network configuration from JSON file."""
        default_config = {
            "user_info": {
                "nick1": self.default_nickname,
                "nick2": "",
                "nick3": "",
                "username": self.default_nickname
            },
            "networks": []
        }
        if not os.path.exists(self.CONFIG_FILE):
            return default_config
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Simple validation/merge with defaults
                if "user_info" not in config: config["user_info"] = default_config["user_info"]
                if "networks" not in config: config["networks"] = default_config["networks"]
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading network config: {e}. Using defaults.")
            return default_config

    def save_network_config(self, config_data):
        """Saves network configuration to JSON file."""
        print(f"DEBUG: IRCClient.save_network_config called with data: {config_data}") # <-- Debug print
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
            print(f"DEBUG: Successfully saved config to {self.CONFIG_FILE}") # <-- Debug print
        except IOError as e:
            print(f"Error saving network config: {e}") # Existing error print
    # --- End Network Config ---

    def ping_server_periodically(self, server):
        """Send periodic pings to keep the connection alive"""
                    
def main():
    # Configuration info - but don't connect automatically
    default_server = "irc.libera.chat"  # Default server
    default_port = 6667  # Default port
    default_nickname = "PythonUser"  # Default nickname
    
    # Import required modules
    import tkinter as tk
    from tkinter import ttk
    import tkinter.scrolledtext as scrolledtext
    import threading
    import socket
    import time
    from datetime import datetime
    import os
    
    # Create Tkinter root window
    root = tk.Tk()
    root.title("RootX IRC Client")
    root.geometry("1000x700")
    
    # Set up dark theme for the entire application
    style = ttk.Style()
    style.theme_use('default')
    
    # Configure dark theme colors
    style.configure('TFrame', background='black')
    style.configure('TLabel', background='black', foreground='white')
    style.configure('TButton', background='#333333', foreground='white')
    style.configure('TEntry', fieldbackground='black', foreground='white')
    style.configure('TNotebook', background='black')
    style.configure('TNotebook.Tab', background='black', foreground='white')
    style.configure('TPanedwindow', background='black')
    style.configure('Treeview', background='black', foreground='white', fieldbackground='black')
    style.map('Treeview', background=[('selected', '#333333')], foreground=[('selected', 'white')])
    style.configure('TSeparator', background='#333333')
    style.configure('TMenubutton', background='black', foreground='white')
    style.configure('TCheckbutton', background='black', foreground='white')
    style.configure('Vertical.TScrollbar', background='#333333', troughcolor='black')
    style.configure('Horizontal.TScrollbar', background='#333333', troughcolor='black')
    
    # Set root window background
    root.configure(background='black')
    
    # Override default text widget configuration
    root.option_add('*Text.Background', 'black')
    root.option_add('*Text.Foreground', 'white')
    root.option_add('*Text.selectBackground', '#333333')
    root.option_add('*Text.selectForeground', 'white')
    
    # Override scrolledtext defaults
    root.option_add('*ScrolledText.Background', 'black')
    root.option_add('*ScrolledText.Foreground', 'white')
    
    # Override listbox defaults
    root.option_add('*Listbox.Background', 'black')
    root.option_add('*Listbox.Foreground', 'white')
    root.option_add('*Listbox.selectBackground', '#333333')
    root.option_add('*Listbox.selectForeground', 'white')
    
    # Override menu defaults
    root.option_add('*Menu.Background', 'black')
    root.option_add('*Menu.Foreground', 'white')
    root.option_add('*Menu.activeBackground', '#333333')
    root.option_add('*Menu.activeForeground', 'white')
    
    # Initialize the client with the root window but don't connect yet
    irc_client = IRCClient(root, None, default_port, default_nickname)
    
    # Display connection instructions (if not already displayed by init)
    # irc_client.add_status_message("Welcome to rootX IRC Client!")
    if default_server:
         irc_client.add_status_message(f"To connect, use: /server {default_server} {default_port} {default_nickname}")
    
    # Apply dark theme to all windows
    irc_client.save_theme_preference('default')
    
    # Run the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()