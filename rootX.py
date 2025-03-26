import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from colorama import Fore, Style
import time

class ChannelWindow:
    def __init__(self, irc_client, channel_name, server):
        self.irc_client = irc_client
        self.channel_name = channel_name
        self.server = server
        self.users = set()
        
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

        # Add theme settings
        self.current_theme = "default"
        self.themes = {
            "default": {
                'bg': 'black',
                'fg': 'white',
                'timestamp': 'gray',
                'join': 'green',
                'part': 'red',
                'quit': 'red',
                'nick': 'blue',
                'username': 'gray',
                'my_username': 'magenta',
                'message': 'white',
                'kick': 'red',
                'action': 'yellow'
            },
            "dark": {
                'bg': '#1a1a1a',
                'fg': '#e6e6e6',
                'timestamp': '#808080',
                'join': '#00cc00',
                'part': '#ff3333',
                'quit': '#ff3333',
                'nick': '#3399ff',
                'username': '#808080',
                'my_username': '#ff66ff',
                'message': '#e6e6e6',
                'kick': '#ff3333',
                'action': '#ffff66'
            },
            "light": {
                'bg': '#f0f0f0',
                'fg': '#000000',
                'timestamp': '#666666',
                'join': '#008000',
                'part': '#cc0000',
                'quit': '#cc0000',
                'nick': '#0066cc',
                'username': '#666666',
                'my_username': '#cc00cc',
                'message': '#000000',
                'kick': '#cc0000',
                'action': '#808000'
            },
            "matrix": {
                'bg': 'black',
                'fg': '#00ff00',
                'timestamp': '#006600',
                'join': '#00ff00',
                'part': '#008800',
                'quit': '#008800',
                'nick': '#00cc00',
                'username': '#006600',
                'my_username': '#00ff00',
                'message': '#00ff00',
                'kick': '#008800',
                'action': '#00aa00'
            }
        }

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
        for theme_name in self.themes.keys():
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
        self.is_closing = False

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
        theme_var = tk.StringVar(value=self.current_theme)
        
        # Create radio buttons for each theme
        for theme_name in self.themes.keys():
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
            if theme_name in self.themes:
                theme = self.themes[theme_name]
                self.current_theme = theme_name
                
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
                    'devoice': 'devoice'
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
            self.users_listbox.delete(0, tk.END)
            
            # Filter and sort users in a list comprehension for better performance
            valid_users = sorted(
                [user for user in self.users 
                 if (user.startswith(('@', '+')) or user[0].isalnum()) and 
                 not any(x in user.lower() for x in ['366', 'list', 'end', 'names'])],
                key=lambda x: (not x.startswith('@'), not x.startswith('+'), x.lower())
            )

            # Update Users Count
            self.users_label.config(text=f"Users: {len(valid_users)}")
            
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
            
            # Keep the display scrolled to the bottom and update
            self.chat_display.see(tk.END)
            
            # Only update the display after all text is inserted
            self.chat_display.update()
        except Exception as e:
            print(f"Error in _add_message_safe: {e}")


        
    def add_message(self, message, tag=None):

        """Add a message to the chat display safely"""
        """Add a message to the chat display safely"""
        if not self.is_closing:
            try:
                self.window.after(0, self._add_message_safe, message, tag)
            except Exception as e:
                print(f"Error adding message: {e}")
            
    def on_closing(self):
        """Handle window closing properly"""
        try:
            self.is_closing = True
            # Remove channel from network tree
            server_data = self.irc_client.server_nodes.get(self.server)  # Use self.server instead of current_server
            if server_data and self.channel_name in server_data['channels']:
                self.irc_client.network_tree.delete(server_data['channels'][self.channel_name])
                del server_data['channels'][self.channel_name]

            # Clean up channel windows dict
            channel_key = f"{self.server}:{self.channel_name}"
            if channel_key in self.irc_client.channel_windows:
                del self.irc_client.channel_windows[channel_key]
            self.irc_client.send_command(f"PART {self.channel_name}", self.server)
            self.window.destroy()
        except Exception as e:
            print(f"Error in on_closing: {e}")

    def toggle_visibility(self):
        if self.minimized:
            self.window.deiconify()
            self.minimized = False
        else:
            self.window.withdraw()
            self.minimized = True

class PrivateWindow:
    def __init__(self, irc_client, username, server):
        self.irc_client = irc_client
        self.username = username
        self.server = server  # Store server information
        self.pm_key = f"{server}:{username}"  # Create a unique key for this PM window
        
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
        # Remove PM node from correct server's tree section
        server_data = self.irc_client.server_nodes.get(self.server)
        if server_data and self.username in server_data['private_msgs']:
            self.irc_client.network_tree.delete(server_data['private_msgs'][self.username])
            del server_data['private_msgs'][self.username]
                
        # Clean up private windows dict using the PM key
        if self.pm_key in self.irc_client.private_windows:
            del self.irc_client.private_windows[self.pm_key]
            
        # Destroy window
        self.window.destroy()
        
    def send_message(self, event=None):
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
    def __init__(self, master, server=None, port=6667, nickname="PythonUser"):
        # Client version
        self.version = "rootX IRC Client v1.0"
        
        self.master = master
        self.connections = {}  # Dictionary to store connections by server name
        self.current_server = None  # Track which server is currently active
        self.servers = []  # List of servers to connect to
        
        # Initialize status_display to None to prevent exceptions
        self.status_display = None
        
        # Preferences dictionary
        self.preferences = {
            'theme': 'default'
        }
        
        # Thread synchronization
        self.lock = threading.Lock()
        self.running = True
        self.disconnecting = False
        
        # Windows dictionary - keyed by unique identifiers
        self.channel_windows = {}  # Use server:channel as key
        self.private_windows = {}  # Use server:nickname as key
        self.status_window = None
        
        # Pending connection attempts
        self.connection_attempts = {}
        self.reconnect_attempts = {}
        self.max_reconnect_attempts = 3
        
        # Pending operations
        self.pending_bans = {}  # Track pending ban operations by target_nick
        
        # Create main window
        self.window = master
        self.window.title("Multi-Server IRC Client")
        
        # Create paned window
        self.paned_window = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Create network tree frame
        self.network_frame = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(self.network_frame, weight=1)
        
        # Create network tree
        self.network_tree = ttk.Treeview(self.network_frame, selectmode='browse')
        self.network_tree.heading('#0', text='Network', anchor='w')
        self.network_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind event for selecting a node
        self.network_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Create right content frame
        self.content_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.content_frame, weight=4)
        
        # State for node tracking
        self.server_nodes = {}  # Dictionary to track server nodes and their channels
        
        # Create context menu for tree
        self.tree_menu = tk.Menu(self.window, tearoff=0)
        self.tree_menu.add_command(label="Connect", command=self.connect_selected)
        self.tree_menu.add_command(label="Disconnect", command=self.disconnect_selected)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Join Channel", command=self.show_join_dialog)
        self.tree_menu.add_command(label="Close Window", command=self.close_selected)
        
        # Bind context menu
        self.network_tree.bind("<Button-3>", self.show_tree_menu)
        
        # Load icons for tree - Create empty PhotoImage objects as fallbacks
        self.server_icon = tk.PhotoImage(width=1, height=1)
        self.channel_icon = tk.PhotoImage(width=1, height=1)
        self.pm_icon = tk.PhotoImage(width=1, height=1)
        
        try:
            # Load icons if available
            from PIL import Image, ImageTk
            try:
                server_img = Image.open("server.png").resize((16, 16))
                channel_img = Image.open("channel.png").resize((16, 16))
                pm_img = Image.open("pm.png").resize((16, 16))
                
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
        
        # Create status bar
        self.status_bar = ttk.Label(self.window, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Thread for receiving data
        self.receive_threads = {}
        
        # Create status window first so we can show messages
        self.create_status_window()
        
        # Connect to default server if provided
        if server:
            self.connect_to_server(server, port, nickname)

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
                # Set disconnecting flag to signal thread to exit
                self.disconnecting = True
                
                # Send QUIT command to server
                self.send_command(f"QUIT :{quit_message}", server)
                
                # Close socket
                try:
                    self.connections[server]['socket'].shutdown(socket.SHUT_RDWR)
                    self.connections[server]['socket'].close()
                except:
                    pass
                
                # Clean up connections dictionary
                del self.connections[server]
                
                # Remove server node and cleanup windows
                self.remove_server_node(server)
                
                # Wait for receive thread to exit (with timeout)
                if server in self.receive_threads:
                    self.receive_threads[server].join(1.0)  # Wait up to 1 second
                    del self.receive_threads[server]
                
                self.add_status_message(f"Disconnected from {server}")
                
            except Exception as e:
                self.add_status_message(f"Error quitting {server}: {e}")
            finally:
                self.disconnecting = False

    def remove_server_node(self, server):
        """Remove a server node and all its child nodes from the tree"""
        if server in self.server_nodes:
            # Get server data
            server_data = self.server_nodes[server]
            
            # Close all channel windows for this server
            channels_to_close = [
                key for key in list(self.channel_windows.keys())
                if key.startswith(f"{server}:")
            ]
            for channel_key in channels_to_close:
                if channel_key in self.channel_windows:
                    try:
                        self.channel_windows[channel_key].on_closing()
                    except Exception as e:
                        print(f"Error closing channel window {channel_key}: {e}")
            
            # Close all PM windows for this server
            pms_to_close = [
                key for key in list(self.private_windows.keys())
                if key.startswith(f"{server}:")
            ]
            for pm_key in pms_to_close:
                if pm_key in self.private_windows:
                    try:
                        self.private_windows[pm_key].on_closing()
                    except Exception as e:
                        print(f"Error closing PM window {pm_key}: {e}")
            
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
                
                # If there are other servers, set one as current
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
            print(f"Added server node with icon: {server}")  # Debug print
            return server_node

    def add_channel_node(self, channel):
        """Add a channel under the current server"""
        if self.current_server and self.current_server in self.server_nodes:
            server_data = self.server_nodes[self.current_server]
            if channel not in server_data['channels']:
                channel_node = self.network_tree.insert(
                    server_data['node'], 'end',
                    text=channel,
                    tags=('channel',),
                    image=self.channel_icon
                )
                server_data['channels'][channel] = channel_node
                print(f"Added channel node with icon: {channel}")  # Debug print

    def add_pm_node(self, username, server):
        """Add a private message node to the network tree under the correct server"""
        if server not in self.server_nodes:
            # Server node doesn't exist, create it first
            server_node = self.network_tree.insert("", "end", text=server, tags=("server",))
            self.server_nodes[server] = {
                'node': server_node,
                'channels': {},
                'private_msgs': {}
            }
        
        # Get server node data
        server_data = self.server_nodes[server]
        
        # Add to private messages section
        if username not in server_data.get('private_msgs', {}):
            if 'private_msgs_node' not in server_data:
                # Create 'Private Messages' category if it doesn't exist
                server_data['private_msgs_node'] = self.network_tree.insert(
                    server_data['node'], "end", text="Private Messages", tags=("category",)
                )
                # Initialize private_msgs dict if needed
                if 'private_msgs' not in server_data:
                    server_data['private_msgs'] = {}
            
            # Add the PM node
            pm_node = self.network_tree.insert(
                server_data['private_msgs_node'], "end", text=username, tags=("private",)
            )
            server_data['private_msgs'][username] = pm_node
            
            # Store the PM key for reference
            pm_key = f"{server}:{username}"
            self.network_tree.item(pm_node, values=(pm_key,))

    def remove_channel_node(self, channel):
        """Remove a channel node"""
        if self.current_server and self.current_server in self.server_nodes:
            server_data = self.server_nodes[self.current_server]
            if channel in server_data['channels']:
                self.network_tree.delete(server_data['channels'][channel])
                del server_data['channels'][channel]

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

    def send_ctcp_request(self, target, request):
        """Send a CTCP request"""
        self.send_command(f"PRIVMSG {target} :\x01{request}\x01")

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


    def create_private_window(self, username, server=None):
        # If server is not specified, use current server
        if not server:
            server = self.current_server
            
        if not server:
            self.add_status_message("Not connected to any server")
            return None
            
        # Create a unique key for the PM window
        pm_key = f"{server}:{username}"
        
        # Check if PM window already exists
        if pm_key in self.private_windows:
            # Window exists, toggle visibility
            window = self.private_windows[pm_key]
            # Deiconify if minimized
            window.window.deiconify()
            window.window.lift()
            return window
            
        # Create new PM window
        window = PrivateWindow(self, username, server)
        self.private_windows[pm_key] = window
        return window
        
    def send_private_message(self, username, message, server):
        if server not in self.connections:
            self.add_status_message(f"Not connected to server: {server}")
            return
            
        conn = self.connections[server]
        conn['socket'].send(f"PRIVMSG {username} :{message}\r\n".encode())
        
    def create_channel_window(self, channel, server):
        """Create a new channel window"""
        channel_key = f"{server}:{channel}"
        if channel_key not in self.channel_windows:
            self.channel_windows[channel_key] = ChannelWindow(self, channel, server)
            self.add_channel_node(channel)  # Add to tree
            self.send_command(f"NAMES {channel}", server)
            self.add_status_message(f"Joined channel: {channel} on {server}")



    def create_status_window(self):
        """Create the status window in the content frame"""
        # Create status window
        self.status_window = ttk.Frame(self.content_frame)
        self.status_window.pack(fill=tk.BOTH, expand=True)
        
        # Create status display
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
        
        # Welcome message
        self.add_status_message(f"Welcome to {self.version}")
        self.add_status_message("Use /server hostname port nickname to connect to an IRC server")
        self.add_status_message("Example: /server irc.libera.chat 6667 YourNickname")

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
        """Show server settings dialog"""
        if not self.current_server:
            self.add_status_message("Not connected to any server")
            return
            
        self.add_status_message(f"Current server: {self.current_server}")
        if self.current_server in self.connections:
            nickname = self.connections[self.current_server]['nickname']
            self.add_status_message(f"Current nickname: {nickname}")
            self.add_status_message("Use /nick NewNickname to change your nickname")
            self.add_status_message("Use /join #channel to join a channel")
            
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

    def show_channel_list(self):
        """Show channel list dialog"""
        if not self.current_server:
            self.add_status_message("Not connected to any server")
            return
            
        self.add_status_message(f"Requesting channel list from {self.current_server}")
        self.send_command("LIST", self.current_server)
        self.add_status_message("Use /list to get a list of channels")
        
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
                    # Close all channel windows for this server
                    channels_to_close = [
                        key for key in self.channel_windows.keys()
                        if key.startswith(f"{server}:")
                    ]
                    for channel_key in channels_to_close:
                        if channel_key in self.channel_windows:
                            self.channel_windows[channel_key].on_closing()
                    
                    # Close the socket
                    try:
                        self.connections[server]['socket'].shutdown(socket.SHUT_RDWR)
                        self.connections[server]['socket'].close()
                    except:
                        pass
                    del self.connections[server]
                    
                    # Wait for receive thread to terminate
                    if server in self.receive_threads:
                        self.receive_threads[server].join(1.0)  # Wait up to 1 second
                        del self.receive_threads[server]
                    
                    # Use the dedicated method to remove server node and all its children
                    self.remove_server_node(server)
        finally:
            self.disconnecting = False

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

    def handle_status_input(self, event):
        self.handle_status_command()
        
    def handle_status_command(self):
        command = self.command_input.get()
        if command:
            if command.startswith('/'):
                self.handle_command(command, None)
            self.command_input.delete(0, tk.END)
            
    def send_command(self, command, server=None):
        """Send command to specified server or current server"""
        if server is None:
            server = self.current_server
        if server in self.connections:
            self.connections[server]['socket'].send(f"{command}\r\n".encode('utf-8'))

        
    def send_channel_message(self, channel, message):
        self.send_command(f"PRIVMSG {channel} :{message}")
        
    def handle_command(self, command, current_channel):
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
                self.add_status_message(f"Usage: /quit [server] [message] - Current servers: {', '.join(self.connections.keys())}")
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

        if cmd == '/server':
            if len(parts) >= 2:
                server = parts[1]
                port = int(parts[2]) if len(parts) > 2 else 6667
                nickname = parts[3] if len(parts) > 3 else self.default_nickname
                self.connect_to_server(server, port, nickname)
            else:
                self.add_status_message("Usage: /server <server> [port] [nickname]")


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
                
    def add_status_message(self, message, tag='status'):
        """Add a message to the status window"""
        if not hasattr(self, 'status_display') or self.status_display is None:
            print(f"Status: {message}")  # Fallback if GUI not initialized
            return
            
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

    def handle_server_message(self, data, server):
        try:
            if data.startswith('ERROR :') or 'Connection closed' in data:
                error_msg = data.split(':', 1)[1].strip()
                self.add_status_message(f"Server {server} disconnected: {error_msg}")
                self.quit_server(server)
                self.remove_server_node(server)  # Add this line
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
                            window = self.channel_windows[channel_key]
                            
                            if target:
                                # Handle user modes
                                if '+o' in mode:
                                    # Add @ to user in list
                                    window.users.discard(target)
                                    window.users.add(f"@{target}")
                                    window.update_users_list()
                                    window.add_action(setter, f"gives channel operator status to {target}")
                                    
                                elif '-o' in mode:
                                    # Remove @ from user
                                    window.users.discard(f"@{target}")
                                    window.users.add(target)
                                    window.update_users_list()
                                    window.add_action(setter, f"removes channel operator status from {target}")
                                    
                                elif '+v' in mode:
                                    # Add + to user
                                    window.users.discard(target)
                                    window.users.add(f"+{target}")
                                    window.update_users_list()
                                    window.add_action(setter, f"gives voice to {target}")
                                    
                                elif '-v' in mode:
                                    # Remove + from user
                                    window.users.discard(f"+{target}")
                                    window.users.add(target)
                                    window.update_users_list()
                                    window.add_action(setter, f"removes voice from {target}")
                                    
                            print(f"DEBUG - Mode change: {setter} sets {mode} on {channel} for {target}")
                            
                except Exception as e:
                    print(f"Error handling mode: {e}")
                    self.add_status_message(f"Error handling mode: {e}")
                            
                except Exception as e:
                    print(f"Error handling mode: {e}")
                    self.add_status_message(f"Error handling mode: {e}")

            elif data.startswith(':') and ('311' in data or '318' in data):  # WHOIS response
                try:
                    parts = data.split()
                    target_nick = parts[3]
                    
                    if '311' in data:  # WHOIS user info
                        user_host = parts[4] + '@' + parts[5]
                        if target_nick in self.pending_bans:
                            ban_data = self.pending_bans[target_nick]
                            if isinstance(ban_data, dict):  # New format with channel and reason
                                channel = ban_data['channel']
                                reason = ban_data.get('reason', "Banned")
                                kick = ban_data.get('kick', True)
                                
                                # Apply the ban
                                ban_mask = f'*!{user_host}'
                                self.send_command(f'MODE {channel} +b {ban_mask}', server)
                                
                                # Update channel display
                                channel_key = f"{server}:{channel}"
                                if channel_key in self.channel_windows:
                                    window = self.channel_windows[channel_key]
                                    timestamp = datetime.now().strftime("[%H:%M:%S]")
                                    window.chat_display.insert(tk.END,
                                        f"{timestamp} * Set ban on {ban_mask}\n",
                                        'ban')
                                    window.chat_display.see(tk.END)
                                
                                # Kick if requested
                                if kick:
                                    self.send_command(f'KICK {channel} {target_nick} :{reason}', server)
                            else:  # Old format with just channel name
                                channel = ban_data
                                self.send_command(f'MODE {channel} +b *!{user_host}', server)
                                self.send_command(f'KICK {channel} {target_nick} :Banned', server)
                            
                            # Clean up after applying ban
                            del self.pending_bans[target_nick]
                            
                    elif '318' in data:  # End of WHOIS
                        # Clean up if we got end of WHOIS but no user info 
                        # (e.g., if user doesn't exist)
                        if target_nick in self.pending_bans:
                            ban_data = self.pending_bans[target_nick]
                            # Log the failed ban attempt
                            if isinstance(ban_data, dict):
                                channel = ban_data['channel']
                                channel_key = f"{server}:{channel}"
                                if channel_key in self.channel_windows:
                                    window = self.channel_windows[channel_key]
                                    window.chat_display.insert(tk.END,
                                        f"Could not ban {target_nick}: User info not available\n",
                                        'error')
                                    window.chat_display.see(tk.END)
                            
                            # Clean up
                            del self.pending_bans[target_nick]
                            
                except Exception as e:
                    self.add_status_message(f"Error handling WHOIS for ban: {e}")
                    # Clean up any pending bans to prevent memory leaks
                    if target_nick in self.pending_bans:
                        del self.pending_bans[target_nick]

            
            # Handle LIST response (322)
            elif '322' in data:  # RPL_LIST
                try:
                    parts = data.split()
                    channel = parts[3]
                    users = parts[4]
                    topic = ' '.join(parts[5:]).lstrip(':')
                    if hasattr(self, 'channel_list_callback'):
                        self.channel_list_callback({
                            'channel': channel,
                            'users': users,
                            'topic': topic
                        })
                except Exception as e:
                    self.add_status_message(f"Error handling channel list: {e}")
                return
            
            # Handle TOPIC messages
            if 'TOPIC' in data:
                try:
                    parts = data.split()
                    channel = parts[2]
                    topic = data.split(':', 2)[-1].strip()
                    channel_key = f"{server}:{channel}"
                    
                    if channel_key in self.channel_windows:
                        self.channel_windows[channel_key].update_topic(topic)
                        self.channel_windows[channel_key].add_message(f"* Topic changed to: {topic}")
                except Exception as e:
                    self.add_status_message(f"Error handling topic: {e}")
                    
            # Handle 332 (topic on join) messages
            elif ' 332 ' in data:  # RPL_TOPIC
                try:
                    parts = data.split()
                    channel = parts[3]
                    topic = data.split(':', 2)[-1].strip()
                    channel_key = f"{server}:{channel}"
                    
                    if channel_key in self.channel_windows:
                        self.channel_windows[channel_key].update_topic(topic)
                except Exception as e:
                    self.add_status_message(f"Error handling topic on join: {e}")
            
            # Handle end of LIST (323)
            if ' 323 ' in data:  # End of channel list
                self.add_status_message("End of channel list")
                return

            if 'JOIN' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        user = parts[0].lstrip(':')
                        channel = data.split('JOIN')[1].strip().lstrip(':')
                        channel_key = f"{server}:{channel}"
                        print(f"DEBUG - JOIN: {user} to {channel_key}")  # Debug print
                        
                        if channel_key in self.channel_windows:
                            window = self.channel_windows[channel_key]
                            window.users.add(user)
                            window.update_users_list()
                            timestamp = datetime.now().strftime("[%H:%M:%S]")
                            window.chat_display.insert(tk.END, f"{timestamp} * {user} has joined {channel}\n", 'join')
                            window.chat_display.see(tk.END)
                            
                            # Request NAMES list if we joined
                            if user == self.connections[server]['nickname']:
                                self.send_command(f"NAMES {channel}", server)
                                
                except Exception as e:
                    print(f"Error handling JOIN: {e}")  # Debug print
                    self.add_status_message(f"Error handling join: {e}")
                    
            if '353' in data:  # NAMES reply
                try:
                    # Parse channel name
                    channel = None
                    channel_type = None
                    
                    # Split the message parts
                    parts = data.split()
                    for i, part in enumerate(parts):
                        if part in ['=', '*', '@']:  # Channel type indicators
                            channel_type = part
                            if i + 1 < len(parts):
                                channel = parts[i + 1]
                                break
                        elif part.startswith('#'):
                            channel = part
                            break
                    
                    if channel:
                        channel_key = f"{server}:{channel}"
                        print(f"DEBUG - Processing NAMES for {channel_key}")  # Debug print
                        
                        if channel_key in self.channel_windows:
                            window = self.channel_windows[channel_key]
                            
                            # Get the users part (after the last ':')
                            users_part = data.split(':', 2)[-1].strip()
                            users = users_part.split()
                            
                            print(f"DEBUG - Users found: {users}")  # Debug print
                            
                            # Start batch update if not already started
                            if not window.batch_updating:
                                window.begin_batch_update()
                            
                            # Add users to buffer
                            window.names_buffer.update(users)
                            
                except Exception as e:
                    print(f"Error processing NAMES: {e}")  # Debug print
                    self.add_status_message(f"Error processing NAMES: {e}")
                    
            # Handle end of NAMES list (366)
            elif '366' in data:  # End of NAMES
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
                        print(f"DEBUG - End of NAMES for {channel_key}")  # Debug print
                        
                        if channel_key in self.channel_windows:
                            window = self.channel_windows[channel_key]
                            # End batch update and process
                            window.end_batch_update()
                            print(f"DEBUG - Final user list: {window.users}")  # Debug print
                            
                except Exception as e:
                    print(f"Error handling end of NAMES: {e}")  # Debug print
                    self.add_status_message(f"Error handling end of NAMES: {e}")

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
                            channel_key = f"{server}:{target}"
                            if channel_key in self.channel_windows:
                                self.channel_windows[channel_key].add_action(sender, action_text)
                            elif sender in self.private_windows:
                                self.private_windows[sender].add_action(sender, action_text)
                        else:
                            # Handle regular messages
                            if target.startswith('#'):  # Channel message
                                channel_key = f"{server}:{target}"
                                if channel_key in self.channel_windows:
                                    self.channel_windows[channel_key].add_message(f"{sender}: {message}")
                            else:  # Private message
                                if sender not in self.private_windows:
                                    self.create_private_window(sender, server)
                                self.private_windows[sender].add_message(f"{sender}: {message}")
                                
                except Exception as e:
                    self.add_status_message(f"Error handling message: {e}")


            elif 'PART' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        user = parts[0].lstrip(':')
                        channel = data.split('PART')[1].split()[0].strip()
                        channel_key = f"{server}:{channel}"
                        if channel_key in self.channel_windows:
                            self.channel_windows[channel_key].users.discard(user)
                            self.channel_windows[channel_key].update_users_list()
                            self.channel_windows[channel_key].add_message(f"* {user} has left {channel}")
                except Exception as e:
                    self.add_status_message(f"Error handling part: {e}")



            if 'KICK' in data:
                try:
                    parts = data.split()
                    if len(parts) >= 4:
                        kicker = parts[0].split('!')[0].lstrip(':')
                        channel = parts[2]
                        kicked_user = parts[3]
                        reason = data.split(':', 2)[-1].strip() if ':' in data else "No reason given"
                        
                        channel_key = f"{server}:{channel}"
                        if channel_key in self.channel_windows:
                            window = self.channel_windows[channel_key]
                            
                            # Add kick message to channel
                            timestamp = datetime.now().strftime("[%H:%M:%S]")
                            window.chat_display.insert(tk.END, 
                                f"{timestamp} * {kicked_user} was kicked by {kicker} ({reason})\n", 
                                'kick')
                            window.chat_display.see(tk.END)
                            
                            # If we're the one who got kicked
                            if kicked_user == self.connections[server]['nickname']:
                                # Remove from network tree
                                self.remove_channel_node(channel)
                                
                                # Remove from channel windows dict and destroy window
                                window.window.destroy()
                                del self.channel_windows[channel_key]
                                
                                self.add_status_message(f"You were kicked from {channel} by {kicker} ({reason})")
                            else:
                                # Someone else was kicked, update the user list
                                window.remove_user(kicked_user)
                                
                            print(f"DEBUG - Kick processed: {kicked_user} from {channel} by {kicker}")
                            
                except Exception as e:
                    print(f"Error handling kick: {e}")
                    self.add_status_message(f"Error handling kick: {e}")

            elif 'QUIT' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        user = parts[0].lstrip(':')
                        quit_message = data.split(':', 2)[-1].strip()
                        # Remove user from all channels they were in
                        for channel_window in self.channel_windows.values():
                            if user in channel_window.users:
                                channel_window.users.discard(user)
                                channel_window.update_users_list()
                                channel_window.add_message(f"* {user} has quit ({quit_message})")
                except Exception as e:
                    self.add_status_message(f"Error handling quit: {e}")

            elif 'NICK' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        old_nick = parts[0].lstrip(':')
                        new_nick = data.split(':', 2)[-1].strip()
                        
                        # Update nickname in server connections if it's our nick
                        if old_nick == self.connections[server]['nickname']:
                            self.connections[server]['nickname'] = new_nick
                        
                        # Update nickname in all channels
                        for channel_window in self.channel_windows.values():
                            if old_nick in channel_window.users:
                                channel_window.users.discard(old_nick)
                                channel_window.users.add(new_nick)
                                channel_window.update_users_list()
                                channel_window.add_message(f"* {old_nick} is now known as {new_nick}")
                except Exception as e:
                    self.add_status_message(f"Error handling nick: {e}")

            # Handle PRIVMSG (including channel messages and private messages)
            elif ' PRIVMSG ' in data:
                try:
                    # Parse sender and target
                    parts = data.split(' PRIVMSG ', 1)
                    sender_part = parts[0].lstrip(':')
                    sender_nick = sender_part.split('!', 1)[0]
                    
                    # Get target and message
                    target_msg = parts[1].split(' :', 1)
                    target = target_msg[0]
                    message = target_msg[1] if len(target_msg) > 1 else ""
                    
                    # Check if it's a CTCP message
                    if message.startswith('\x01') and message.endswith('\x01'):
                        # Handle CTCP
                        ctcp_content = message.strip('\x01')
                        ctcp_parts = ctcp_content.split(' ', 1)
                        ctcp_cmd = ctcp_parts[0].upper()
                        ctcp_args = ctcp_parts[1] if len(ctcp_parts) > 1 else ""
                        
                        if ctcp_cmd == 'ACTION':
                            # Handle actions (/me commands)
                            if target.startswith('#'):
                                # Channel action
                                channel_key = f"{server}:{target}"
                                if channel_key in self.channel_windows:
                                    self.channel_windows[channel_key].add_action(sender_nick, ctcp_args)
                            else:
                                # Private message action
                                pm_key = f"{server}:{sender_nick}"
                                if pm_key in self.private_windows:
                                    self.private_windows[pm_key].add_action(sender_nick, ctcp_args)
                                else:
                                    # Create PM window
                                    pm_window = self.create_private_window(sender_nick, server)
                                    if pm_window:
                                        pm_window.add_action(sender_nick, ctcp_args)
                            return
                        elif ctcp_cmd == 'VERSION':
                            # Reply with client version
                            self.send_command(f"NOTICE {sender_nick} :\x01VERSION Python IRC Client 1.0\x01", server)
                            return
                        elif ctcp_cmd == 'PING':
                            # Reply with ping response
                            self.send_command(f"NOTICE {sender_nick} :\x01PING {ctcp_args}\x01", server)
                            return
                        elif ctcp_cmd == 'TIME':
                            # Reply with local time
                            local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            self.send_command(f"NOTICE {sender_nick} :\x01TIME {local_time}\x01", server)
                            return
                        else:
                            # Other CTCP commands - ignore for now
                            print(f"Unhandled CTCP: {ctcp_cmd} from {sender_nick}")
                            return
                    
                    # Handle regular messages
                    if target.startswith('#'):
                        # Channel message
                        channel_key = f"{server}:{target}"
                        if channel_key in self.channel_windows:
                            self.channel_windows[channel_key].add_message(f"{sender_nick}: {message}")
                    else:
                        # Private message
                        pm_key = f"{server}:{sender_nick}"
                        if pm_key in self.private_windows:
                            self.private_windows[pm_key].add_message(f"{sender_nick}: {message}")
                        else:
                            # Create new PM window for this message
                            pm_window = self.create_private_window(sender_nick, server)
                            if pm_window:
                                pm_window.add_message(f"{sender_nick}: {message}")
                except Exception as e:
                    self.add_status_message(f"Error handling PRIVMSG: {e}")

        except Exception as e:
            self.add_status_message(f"Error parsing server message: {e}")
            
    def create_channel_window(self, channel, server):
        """Create a new channel window"""
        channel_key = f"{server}:{channel}"
        if channel_key not in self.channel_windows:
            self.channel_windows[channel_key] = ChannelWindow(self, channel, server)
            self.add_channel_node(channel)  # Add to tree
            self.send_command(f"NAMES {channel}", server)
            self.add_status_message(f"Joined channel: {channel} on {server}")



    def connect_to_server(self, server, port, nickname):
        """Connect to an IRC server and set up the connection"""
        try:
            # Check if already connected to this server
            if server in self.connections:
                self.add_status_message(f"Already connected to {server}")
                # Set as current server
                self.current_server = server
                return
                
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server, int(port)))
            
            # Store connection info
            self.connections[server] = {
                'socket': sock,
                'nickname': nickname,
                'channels': set(),
                'users': {}  # Track users per server
            }
            
            # Set as current server
            self.current_server = server
            
            # Add server node to tree if it doesn't exist
            if server not in self.server_nodes:
                # Create server node in tree
                server_node = self.network_tree.insert("", "end", text=server, tags=("server",))
                self.server_nodes[server] = {
                    'node': server_node,
                    'channels': {},
                    'private_msgs': {}
                }
            
            # Send registration commands
            sock.send(f"NICK {nickname}\r\n".encode())
            sock.send(f"USER {nickname} 0 * :{nickname}\r\n".encode())
            
            # Start receive thread
            receive_thread = threading.Thread(
                target=self.receive_data,
                args=(server,),
                daemon=True
            )
            self.receive_threads[server] = receive_thread
            receive_thread.start()
            
            # Update status
            self.add_status_message(f"Connected to {server}:{port} as {nickname}")
            
        except Exception as e:
            self.add_status_message(f"Error connecting to {server}: {e}")
            # Clean up failed connection
            if server in self.connections:
                del self.connections[server]
                
            # Try to clean up socket
            try:
                sock.close()
            except:
                pass

    def run(self):
        """Start the IRC client"""
        try:
            # Start the GUI main loop
            self.status_window.mainloop()
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
            
            while server in self.connections:
                try:
                    data = sock.recv(4096).decode('utf-8', errors='replace')
                    if not data:  # Connection closed
                        self.add_status_message(f"Connection to {server} closed")
                        self.disconnect_from_server(server)
                        break
                        
                    # Add data to buffer and process complete lines
                    buffer += data
                    lines = buffer.split('\r\n')
                    buffer = lines.pop()  # Keep incomplete line in buffer
                    
                    for line in lines:
                        print(f"RECV {server}: {line}")
                        self.handle_server_message(line, server)
                        
                except socket.timeout:
                    # Just continue on timeout
                    continue
                except socket.error as e:
                    self.add_status_message(f"Socket error for {server}: {e}")
                    self.disconnect_from_server(server)
                    break
                    
        except Exception as e:
            self.add_status_message(f"Error in receive thread for {server}: {e}")
        finally:
            # Clean up
            if server in self.connections:
                self.disconnect_from_server(server)

    def on_tree_select(self, event):
        """Handle when a node is selected in the network tree"""
        selection = self.network_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_text = self.network_tree.item(item)['text']
        item_tags = self.network_tree.item(item)['tags']
        item_values = self.network_tree.item(item)['values']
        
        if 'server' in item_tags:
            # Server node selected - set as current server
            self.current_server = item_text
            self.add_status_message(f"Selected server: {item_text}")
            
        elif 'channel' in item_tags:
            # Channel node selected
            # Get the server from the parent item
            parent = self.network_tree.parent(item)
            server = self.network_tree.item(parent)['text']
            
            # Create channel key and focus the window if it exists
            channel_key = f"{server}:{item_text}"
            if channel_key in self.channel_windows:
                self.channel_windows[channel_key].window.deiconify()
                self.channel_windows[channel_key].window.lift()
                
        elif 'private' in item_tags:
            # Private message node selected
            # Get the PM key from the item values
            if item_values and len(item_values) > 0:
                pm_key = item_values[0]
                if pm_key in self.private_windows:
                    self.private_windows[pm_key].window.deiconify()
                    self.private_windows[pm_key].window.lift()
            else:
                # Backward compatibility - try to get the server from the parent's parent
                username = item_text
                parent = self.network_tree.parent(item)  # Get PM category
                server_node = self.network_tree.parent(parent)  # Get server node
                server = self.network_tree.item(server_node)['text']
                
                # Try both with the new format and old format
                pm_key = f"{server}:{username}"
                if pm_key in self.private_windows:
                    self.private_windows[pm_key].window.deiconify()
                    self.private_windows[pm_key].window.lift()

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
            self.tree_menu.entryconfig("Close Window", state="disabled")
        elif 'channel' in item_tags:
            # Channel context menu
            self.tree_menu.entryconfig("Connect", state="disabled")
            self.tree_menu.entryconfig("Disconnect", state="disabled")
            self.tree_menu.entryconfig("Join Channel", state="disabled")
            self.tree_menu.entryconfig("Close Window", state="normal")
        elif 'private' in item_tags:
            # PM context menu
            self.tree_menu.entryconfig("Connect", state="disabled")
            self.tree_menu.entryconfig("Disconnect", state="disabled")
            self.tree_menu.entryconfig("Join Channel", state="disabled")
            self.tree_menu.entryconfig("Close Window", state="normal")
        else:
            # Other item or no item - disable all
            self.tree_menu.entryconfig("Connect", state="disabled")
            self.tree_menu.entryconfig("Disconnect", state="disabled")
            self.tree_menu.entryconfig("Join Channel", state="disabled")
            self.tree_menu.entryconfig("Close Window", state="disabled")
            
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
        """Close the selected window"""
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
                # Close the window
                self.channel_windows[channel_key].on_closing()
                
        elif 'private' in item_tags:
            # Get values which should contain the PM key
            item_values = self.network_tree.item(item)['values']
            if item_values and len(item_values) > 0:
                pm_key = item_values[0]
                if pm_key in self.private_windows:
                    self.private_windows[pm_key].on_closing()
            else:
                # Backward compatibility
                username = item_text
                # Try to get server from parent's parent
                parent = self.network_tree.parent(item)
                server_node = self.network_tree.parent(parent)
                server = self.network_tree.item(server_node)['text']
                
                # Try with both formats
                pm_key = f"{server}:{username}"
                if pm_key in self.private_windows:
                    self.private_windows[pm_key].on_closing()

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

def main():
    # Configuration info - but don't connect automatically
    server = "irc.libera.chat"  # Default server
    port = 6667  # Default port
    nickname = "PythonUser"  # Default nickname
    
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
    
    # Initialize the client with the root window but don't connect yet
    irc_client = IRCClient(root, None, port, nickname)
    
    # Display connection instructions
    irc_client.add_status_message("Welcome to rootX IRC Client!")
    irc_client.add_status_message(f"To connect, use: /server {server} {port} {nickname}")
    
    # Run the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()