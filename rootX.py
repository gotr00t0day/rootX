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
                    self.irc_client.send_command(f"PART {self.channel_name}", self.server)
                except:
                    pass
                
            # Finally destroy the window
            try:
                self.window.destroy()
            except tk.TclError:
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
                users = sorted(list(channel_info['users']), 
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
                if batch_state['current_index'] >= len(batch_state['users']):
                    # Done - update the count with the ACTUAL number of users in the listbox
                    if 'users_label' in channel_info:
                        actual_count = users_listbox.size()
                        channel_info['users_label'].config(text=f"Users: {actual_count}")
                    return
                
                # Process next batch
                start_idx = batch_state['current_index']
                end_idx = min(start_idx + batch_state['batch_size'], len(batch_state['users']))
                
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
                
                # Update the label with current count while processing
                if 'users_label' in channel_info:
                    channel_info['users_label'].config(text=f"Users: {batch_state['total_inserted']}")
                
                # Update index for next batch
                batch_state['current_index'] = end_idx
                
                # Schedule next batch - use short delay to allow UI to breathe
                self.window.after(10, process_batch)
            
            # Start batch processing
            self.window.after(0, process_batch)
            
        except Exception as e:
            print(f"Error in batched user update: {e}")
            import traceback
            traceback.print_exc()

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
            
            # Remove PM node from correct server's tree section
            server_data = self.irc_client.server_nodes.get(self.server)
            if server_data and self.username in server_data['private_msgs']:
                try:
                    self.irc_client.network_tree.delete(server_data['private_msgs'][self.username])
                except tk.TclError:
                    pass
                del server_data['private_msgs'][self.username]
                    
            # Clean up private windows dict using the PM key
            if self.pm_key in self.irc_client.private_windows:
                del self.irc_client.private_windows[self.pm_key]
                
            # Safely destroy widgets
            try:
                if hasattr(self, 'chat_display'):
                    self.chat_display.destroy()
            except tk.TclError:
                pass
                
            try:
                if hasattr(self, 'message_input'):
                    self.message_input.destroy()
            except tk.TclError:
                pass
                
            try:
                if hasattr(self, 'send_button'):
                    self.send_button.destroy()
            except tk.TclError:
                pass
                
            # Finally destroy window
            try:
                self.window.destroy()
            except tk.TclError:
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
    def __init__(self, master, server=None, port=6667, nickname="PythonUser"):
        # Client version
        self.version = "rootX IRC Client v1.0"
        
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
        
        # Load icons for tree - Create empty PhotoImage objects as fallbacks
        self.server_icon = tk.PhotoImage(width=1, height=1)
        self.channel_icon = tk.PhotoImage(width=1, height=1)
        self.pm_icon = tk.PhotoImage(width=1, height=1)
        
        try:
            # Try to load icons if available
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
        
        # View menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Show/Hide Tabs", command=self.toggle_tabs)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        
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
            self.add_status_message("Not connected to any server")
            return
            
        self.add_status_message(f"Requesting channel list from {self.current_server}")
        
        # Use run_in_thread to request channel list without freezing GUI
        def request_channel_list(server):
            try:
                self.send_command("LIST", server)
                return True
            except Exception as e:
                return e
                
        def on_list_requested(result):
            if result is True:
                self.add_status_message("Channel list request sent. Results will appear as they arrive.")
            else:
                self.add_status_message(f"Error requesting channel list: {result}", 'error')
        
        # Execute in background thread
        self.run_in_thread(
            request_channel_list, 
            callback=on_list_requested,
            server=self.current_server
        )

    def on_tree_double_click(self, event):
        """Handle double-click on tree items to switch to the corresponding tab"""
        item = self.network_tree.selection()[0]
        item_tags = self.network_tree.item(item)['tags']
        item_text = self.network_tree.item(item)['text']
        
        if 'server' in item_tags:
            # For server nodes, we'll select the status tab
            self.select_tab('status')
            self.current_server = item_text
        elif 'channel' in item_tags:
            # For channel nodes, we'll select its tab
            parent = self.network_tree.parent(item)
            server = self.network_tree.item(parent)['text']
            tab_id = f"{server}:{item_text}"
            self.select_tab(tab_id)
        elif 'private' in item_tags:
            # For PM nodes, we'll select its tab
            item_values = self.network_tree.item(item)['values']
            if item_values and len(item_values) > 0:
                tab_id = item_values[0]
                self.select_tab(tab_id)
            else:
                # Backward compatibility for older versions
                username = item_text
                parent = self.network_tree.parent(item)  # Get PM category
                server_node = self.network_tree.parent(parent)  # Get server node
                server = self.network_tree.item(server_node)['text']
                tab_id = f"{server}:{username}"
                self.select_tab(tab_id)
                
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
        """Close a channel tab and remove it from the tree view."""
        try:
            # Remove from channel_windows
            channel_key = f"{server}:{channel}"
            if channel_key in self.channel_windows:
                # Get the tab and tab_id
                channel_tab = self.channel_windows[channel_key]['tab']
                
                # Remove from notebook by finding the tab's index
                tab_index = self.notebook.index(channel_tab)
                if tab_index is not None:
                    self.notebook.forget(tab_index)
                
                # Clean up channel_windows entry
                del self.channel_windows[channel_key]
                
                # Remove from tabs dictionary
                if channel_key in self.tabs:
                    del self.tabs[channel_key]
                
                # Remove from treeview
                self.remove_channel_node(channel, server)
                
                # Switch to status tab if this was the active tab
                current_tab = self.notebook.select()
                if not current_tab or current_tab == str(channel_tab):
                    self.select_tab("status")
                    
                self.add_status_message(f"Closed channel {channel} on {server}", "info")
        except Exception as e:
            self.add_status_message(f"Error closing channel tab: {e}", "error")
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

    def create_channel_window(self, channel, server):
        """Create a new channel window as a tab in the notebook"""
        channel_key = f"{server}:{channel}"
        if channel_key not in self.channel_windows:
            # Create a new tab frame in the notebook
            channel_tab = ttk.Frame(self.notebook)
            
            # Create a paned window to separate chat and users
            channel_paned = ttk.PanedWindow(channel_tab, orient=tk.HORIZONTAL)
            channel_paned.pack(fill=tk.BOTH, expand=True)
            
            # Set up the channel tab with a vertical layout
            channel_display_frame = ttk.Frame(channel_paned)
            channel_paned.add(channel_display_frame, weight=3)  # Give chat area more space
            
            # Create topic label
            topic_frame = ttk.Frame(channel_display_frame)
            topic_frame.pack(fill=tk.X)
            topic_label = ttk.Label(topic_frame, text="No topic set", wraplength=600)
            topic_label.pack(fill=tk.X, padx=5, pady=5)
            
            # Create chat display with scrolled text
            chat_display = scrolledtext.ScrolledText(channel_display_frame, wrap=tk.WORD)
            chat_display.pack(fill=tk.BOTH, expand=True)
            
            # Configure text tags for different message types
            chat_display.tag_configure('timestamp', foreground='gray')
            chat_display.tag_configure('join', foreground='green')
            chat_display.tag_configure('part', foreground='red')
            chat_display.tag_configure('quit', foreground='red')
            chat_display.tag_configure('nick', foreground='blue')
            chat_display.tag_configure('username', foreground='gray')
            chat_display.tag_configure('my_username', foreground='magenta')
            chat_display.tag_configure('message', foreground='white')
            chat_display.tag_configure('action', foreground='purple')
            
            # Create input frame
            input_frame = ttk.Frame(channel_display_frame)
            input_frame.pack(fill=tk.X, pady=5)
            
            # Create message input
            message_input = ttk.Entry(input_frame)
            message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            setattr(self, f'input_{channel_key.replace(":", "_")}', message_input)
            
            # Create send button
            send_button = ttk.Button(
                input_frame, 
                text="Send", 
                command=lambda: self.send_channel_message(channel, message_input.get(), server)
            )
            send_button.pack(side=tk.RIGHT, padx=5)
            
            # Bind Enter key to send message
            message_input.bind('<Return>', lambda event: self.send_channel_message(channel, message_input.get(), server))
            
            # Create users panel on the right
            users_frame = ttk.Frame(channel_paned)
            channel_paned.add(users_frame, weight=1)  # Take up less space
            
            # Create users label
            users_label = ttk.Label(users_frame, text="Users")
            users_label.pack(pady=5)
            
            # Create users listbox with scrollbars
            users_list_frame = ttk.Frame(users_frame)
            users_list_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create scrollbars
            users_scrollbar = ttk.Scrollbar(users_list_frame)
            users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            users_horizontal_scrollbar = ttk.Scrollbar(users_list_frame, orient=tk.HORIZONTAL)
            users_horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Create listbox
            users_listbox = tk.Listbox(
                users_list_frame,
                yscrollcommand=users_scrollbar.set,
                xscrollcommand=users_horizontal_scrollbar.set
            )
            users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Configure scrollbars
            users_scrollbar.config(command=users_listbox.yview)
            users_horizontal_scrollbar.config(command=users_listbox.xview)
            
            # Create right-click menu for users
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
            users_listbox.bind("<Button-3>", lambda event, ck=channel_key: self.show_user_context_menu(event, ck))
            
            # Add the tab to the notebook
            self.notebook.add(channel_tab, text=channel)
            self.tabs[channel_key] = channel_tab
            
            # Create a ChannelInfo object to store channel data
            channel_info = {
                'tab': channel_tab,
                'chat_display': chat_display,
                'message_input': message_input,
                'topic_label': topic_label,
                'users': set(),
                'users_listbox': users_listbox,
                'user_menu': user_menu,
                'batch_updating': False,
                'names_buffer': set()
            }
            
            # Store in channel_windows dictionary
            self.channel_windows[channel_key] = channel_info
            
            # Add to tree view
            self.add_channel_node(channel, server)
            
            # Request NAMES list for the channel
            self.send_command(f"NAMES {channel}", server)
            
            # Add join message
            self.add_channel_message(channel_key, f"* Joined channel {channel}", 'join')
            
            # Select the new tab
            self.select_tab(channel_key)
            
            # Update status
            self.add_status_message(f"Joined channel: {channel} on {server}")
        else:
            # If already exists, just select the tab
            self.select_tab(channel_key)



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
            # Set disconnecting flag to signal threads to exit
            self.disconnecting = True
            
            with self.lock:
                if server in self.connections:
                    self.add_status_message(f"Disconnecting from {server}...")
                    
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
                    
                    # Wait for receive thread to terminate - only if called from a different thread
                    if server in self.receive_threads:
                        current_thread = threading.current_thread()
                        if current_thread != self.receive_threads[server]:
                            try:
                                self.receive_threads[server].join(2.0)  # Increased timeout to 2 seconds
                            except RuntimeError:
                                pass  # Ignore "cannot join current thread" error
                            
                        # Always remove the thread reference whether we waited or not
                        del self.receive_threads[server]
                    
                    # Remove server node and all its children from the tree view
                    self.remove_server_node(server)
                    
                    # Update status
                    self.add_status_message(f"Disconnected from {server}")
                    
        except Exception as e:
            self.add_status_message(f"Error during disconnect from {server}: {e}", 'error')
        finally:
            # Reset disconnecting flag
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
                            else:  # Private message action
                                pm_key = f"{server}:{sender}"
                                if pm_key not in self.private_windows:
                                    self.create_private_window(sender, server)
                                self.add_pm_action(pm_key, sender, action_text)
                        else:
                            # Handle regular messages
                            if target.startswith('#'):  # Channel message
                                channel_key = f"{server}:{target}"
                                if channel_key in self.channel_windows:
                                    self.add_channel_message(channel_key, f"{sender}: {message}")
                            else:  # Private message
                                pm_key = f"{server}:{sender}"
                                if pm_key not in self.private_windows:
                                    self.create_private_window(sender, server)
                                self.add_pm_message(pm_key, f"{sender}: {message}")
                                
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
                                self.send_command(f"NAMES {channel}", server)
                except Exception as e:
                    self.add_status_message(f"Error handling join: {e}")

            # Handle NAMES reply (numeric 353)
            elif ' 353 ' in data:  # NAMES reply
                try:
                    # Parse channel name
                    channel = None
                    
                    # Split the message parts
                    parts = data.split()
                    for i, part in enumerate(parts):
                        if part in ['=', '*', '@'] and i + 1 < len(parts):  # Channel type indicators
                            channel = parts[i + 1]
                            break
                        elif part.startswith('#'):
                            channel = part
                            break
                    
                    if channel:
                        channel_key = f"{server}:{channel}"
                        
                        if channel_key in self.channel_windows:
                            channel_info = self.channel_windows[channel_key]
                            
                            # Get the users part (after the last ':')
                            users_part = data.split(':', 2)[-1].strip()
                            users = users_part.split()
                            
                            # Start batch update if not already started
                            if not channel_info['batch_updating']:
                                channel_info['batch_updating'] = True
                                channel_info['names_buffer'] = set()
                            
                            # Add users to buffer
                            channel_info['names_buffer'].update(users)
                except Exception as e:
                    self.add_status_message(f"Error processing NAMES: {e}")
                    
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
                            
                            # End batch update and process
                            if channel_info['batch_updating']:
                                channel_info['users'] = channel_info['names_buffer']
                                channel_info['batch_updating'] = False
                                self.update_channel_users(channel_key)
                except Exception as e:
                    self.add_status_message(f"Error handling end of NAMES: {e}")

            # Handle PART messages
            elif 'PART' in data:
                try:
                    parts = data.split('!')
                    if len(parts) > 1:
                        user = parts[0].lstrip(':')
                        channel = data.split('PART')[1].split()[0].strip()
                        channel_key = f"{server}:{channel}"
                        
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
                            # Update the topic label
                            channel_info = self.channel_windows[channel_key]
                            channel_info['topic_label'].config(text=topic if topic else "No topic set")
                            
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
                        # Update the topic label
                        channel_info = self.channel_windows[channel_key]
                        channel_info['topic_label'].config(text=topic)
                except Exception as e:
                    self.add_status_message(f"Error handling topic reply: {e}")
                
        except Exception as e:
            self.add_status_message(f"Error processing message: {e}")

    def create_channel_window(self, channel, server):
        """Create a new channel window as a tab in the notebook"""
        channel_key = f"{server}:{channel}"
        if channel_key not in self.channel_windows:
            # Create a new tab frame in the notebook
            channel_tab = ttk.Frame(self.notebook)
            
            # Create a paned window to separate chat and users
            channel_paned = ttk.PanedWindow(channel_tab, orient=tk.HORIZONTAL)
            channel_paned.pack(fill=tk.BOTH, expand=True)
            
            # Set up the channel tab with a vertical layout
            channel_display_frame = ttk.Frame(channel_paned)
            channel_paned.add(channel_display_frame, weight=3)  # Give chat area more space
            
            # Create topic label
            topic_frame = ttk.Frame(channel_display_frame)
            topic_frame.pack(fill=tk.X)
            topic_label = ttk.Label(topic_frame, text="No topic set", wraplength=600)
            topic_label.pack(fill=tk.X, padx=5, pady=5)
            
            # Create chat display with scrolled text
            chat_display = scrolledtext.ScrolledText(channel_display_frame, wrap=tk.WORD)
            chat_display.pack(fill=tk.BOTH, expand=True)
            
            # Configure text tags for different message types
            chat_display.tag_configure('timestamp', foreground='gray')
            chat_display.tag_configure('join', foreground='green')
            chat_display.tag_configure('part', foreground='red')
            chat_display.tag_configure('quit', foreground='red')
            chat_display.tag_configure('nick', foreground='blue')
            chat_display.tag_configure('username', foreground='gray')
            chat_display.tag_configure('my_username', foreground='magenta')
            chat_display.tag_configure('message', foreground='white')
            chat_display.tag_configure('action', foreground='purple')
            
            # Create input frame
            input_frame = ttk.Frame(channel_display_frame)
            input_frame.pack(fill=tk.X, pady=5)
            
            # Create message input
            message_input = ttk.Entry(input_frame)
            message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            setattr(self, f'input_{channel_key.replace(":", "_")}', message_input)
            
            # Create send button
            send_button = ttk.Button(
                input_frame, 
                text="Send", 
                command=lambda: self.send_channel_message(channel, message_input.get(), server)
            )
            send_button.pack(side=tk.RIGHT, padx=5)
            
            # Bind Enter key to send message
            message_input.bind('<Return>', lambda event: self.send_channel_message(channel, message_input.get(), server))
            
            # Create users panel on the right
            users_frame = ttk.Frame(channel_paned)
            channel_paned.add(users_frame, weight=1)  # Take up less space
            
            # Create users label
            users_label = ttk.Label(users_frame, text="Users")
            users_label.pack(pady=5)
            
            # Create users listbox with scrollbars
            users_list_frame = ttk.Frame(users_frame)
            users_list_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create scrollbars
            users_scrollbar = ttk.Scrollbar(users_list_frame)
            users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            users_horizontal_scrollbar = ttk.Scrollbar(users_list_frame, orient=tk.HORIZONTAL)
            users_horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Create listbox
            users_listbox = tk.Listbox(
                users_list_frame,
                yscrollcommand=users_scrollbar.set,
                xscrollcommand=users_horizontal_scrollbar.set
            )
            users_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Configure scrollbars
            users_scrollbar.config(command=users_listbox.yview)
            users_horizontal_scrollbar.config(command=users_listbox.xview)
            
            # Create right-click menu for users
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
            users_listbox.bind("<Button-3>", lambda event, ck=channel_key: self.show_user_context_menu(event, ck))
            
            # Add the tab to the notebook
            self.notebook.add(channel_tab, text=channel)
            self.tabs[channel_key] = channel_tab
            
            # Create a ChannelInfo object to store channel data
            channel_info = {
                'tab': channel_tab,
                'chat_display': chat_display,
                'message_input': message_input,
                'topic_label': topic_label,
                'users': set(),
                'users_listbox': users_listbox,
                'user_menu': user_menu,
                'batch_updating': False,
                'names_buffer': set()
            }
            
            # Store in channel_windows dictionary
            self.channel_windows[channel_key] = channel_info
            
            # Add to tree view
            self.add_channel_node(channel, server)
            
            # Request NAMES list for the channel
            self.send_command(f"NAMES {channel}", server)
            
            # Add join message
            self.add_channel_message(channel_key, f"* Joined channel {channel}", 'join')
            
            # Select the new tab
            self.select_tab(channel_key)
            
            # Update status
            self.add_status_message(f"Joined channel: {channel} on {server}")
        else:
            # If already exists, just select the tab
            self.select_tab(channel_key)



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
                # Close the tab
                self.close_channel_tab(channel_key)
                
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
    
    def add_channel_message(self, channel_key, message, tag=None):
        """Add a message to a channel tab
        
        Args:
            channel_key: The channel key in format server:channel
            message: The message to add
            tag: Optional tag for styling
        """
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
            
    def add_channel_action(self, channel_key, sender, action_text):
        """Add an action message to a channel tab
        
        Args:
            channel_key: The channel key in format server:channel
            sender: The username performing the action
            action_text: The action text
        """
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
            
    def add_pm_message(self, pm_key, message, tag=None):
        """Add a message to a private message tab
        
        Args:
            pm_key: The PM key in format server:username
            message: The message to add
            tag: Optional tag for styling
        """
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
            
    def add_pm_action(self, pm_key, sender, action_text):
        """Add an action message to a private message tab
        
        Args:
            pm_key: The PM key in format server:username
            sender: The username performing the action
            action_text: The action text
        """
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
                users = sorted(list(channel_info['users']), 
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
                if batch_state['current_index'] >= len(batch_state['users']):
                    # Done - update the count with the ACTUAL number of users in the listbox
                    if 'users_label' in channel_info:
                        actual_count = users_listbox.size()
                        channel_info['users_label'].config(text=f"Users: {actual_count}")
                    return
                
                # Process next batch
                start_idx = batch_state['current_index']
                end_idx = min(start_idx + batch_state['batch_size'], len(batch_state['users']))
                
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
                
                # Update the label with current count while processing
                if 'users_label' in channel_info:
                    channel_info['users_label'].config(text=f"Users: {batch_state['total_inserted']}")
                
                # Update index for next batch
                batch_state['current_index'] = end_idx
                
                # Schedule next batch - use short delay to allow UI to breathe
                self.window.after(10, process_batch)
            
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
    
    # Initialize the client with the root window but don't connect yet
    irc_client = IRCClient(root, None, default_port, default_nickname)
    
    # Display connection instructions
    irc_client.add_status_message("Welcome to rootX IRC Client!")
    irc_client.add_status_message(f"To connect, use: /server {default_server} {default_port} {default_nickname}")
    
    # Run the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()