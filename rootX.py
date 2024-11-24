import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from colorama import Fore, Style

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

        # Create server menu
        self.server_menu = tk.Menu(self.window, tearoff=0)
        self.server_menu.add_command(label="NickServ...", command=self.show_nickserv_dialog)
        self.server_menu.add_command(label="ChanServ...", command=self.show_chanserv_dialog)
        
        # Add server menu to the menu bar
        self.menu_bar = tk.Menu(self.window)
        self.menu_bar.add_cascade(label="Server", menu=self.server_menu)
        self.window.config(menu=self.menu_bar)


        self.minimized = False
        self.window.withdraw()  # Start minimized

        # Add batch update variables
        self.batch_updating = False
        self.names_buffer = set()
        self.is_closing = False

        # Add action color
        self.chat_display.tag_configure('action', foreground='yellow')

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
        
        # Create theme menu
        self.theme_menu = tk.Menu(self.window, tearoff=0)
        for theme_name in self.themes.keys():
            self.theme_menu.add_command(
                label=theme_name.capitalize(),
                command=lambda t=theme_name: self.apply_theme(t)
            )
            
        # Add theme menu to window menu bar
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)
        self.menu_bar.add_cascade(label="Theme", menu=self.theme_menu)
        
        # Apply default theme
        self.apply_theme("default")

        # Create menu bar (add this after window creation)
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)
        
        # Create Settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        
        # Add Theme Settings option
        self.settings_menu.add_command(label="Theme Settings", command=self.show_theme_settings)


        # Create server menu
        self.server_menu = tk.Menu(self.window, tearoff=0)
        self.server_menu.add_command(label="NickServ...", command=self.show_nickserv_dialog)
        self.server_menu.add_command(label="ChanServ...", command=self.show_chanserv_dialog)
        
        # Add server menu to the menu bar
        self.menu_bar = tk.Menu(self.window)
        self.menu_bar.add_cascade(label="Server", menu=self.server_menu)
        self.window.config(menu=self.menu_bar)

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
                
                # Configure text tags with theme colors
                self.chat_display.tag_configure('timestamp', foreground=theme['timestamp'])
                self.chat_display.tag_configure('join', foreground=theme['join'])
                self.chat_display.tag_configure('part', foreground=theme['part'])
                self.chat_display.tag_configure('quit', foreground=theme['quit'])
                self.chat_display.tag_configure('nick', foreground=theme['nick'])
                self.chat_display.tag_configure('username', foreground=theme['username'])
                self.chat_display.tag_configure('my_username', foreground=theme['my_username'])
                self.chat_display.tag_configure('message', foreground=theme['message'])
                self.chat_display.tag_configure('kick', foreground=theme['kick'])
                self.chat_display.tag_configure('action', foreground=theme['action'])
                
                # Save theme preference (optional)
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
                # Remove @ or + if present
                if user.startswith(('@', '+')):
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
                # Store the pending ban
                self.irc_client.pending_bans[user] = self.channel_name
                # Request WHOIS to get user's host
                self.irc_client.send_command(f'WHOIS {user}', self.server)
                # Remove @ or + if present
                if user.startswith(('@', '+')):
                    user = user[1:]
                    
                # Create dialog for ban options
                ban_dialog = tk.Toplevel(self.window)
                ban_dialog.title("Ban Options")
                ban_dialog.geometry("300x200")
                
                # Add ban type selection
                ttk.Label(ban_dialog, text="Ban Type:").pack(pady=5)
                ban_type = tk.StringVar(value="nick")
                ttk.Radiobutton(ban_dialog, text="Nick Ban", variable=ban_type, value="nick").pack()
                ttk.Radiobutton(ban_dialog, text="Host Ban", variable=ban_type, value="host").pack()
                
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
                        self.irc_client.send_command(f"WHOIS {user}", self.server)
                        # Note: The actual ban will be handled in the WHOIS response
                        self.irc_client.pending_bans[user] = {
                            'channel': self.channel_name,
                            'reason': reason,
                            'kick': kick_after.get()
                        }
                    else:
                        # Simple nick ban
                        self.irc_client.send_command(
                            f"MODE {self.channel_name} +b {user}!*@*",
                            self.server
                        )
                        if kick_after.get():
                            self.irc_client.send_command(
                                f"KICK {self.channel_name} {user} :{reason}",
                                self.server
                            )
                    
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
                # Remove @ or + if present
                if user.startswith(('@', '+')):
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
                # Remove @ or + if present
                if user.startswith(('@', '+')):
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
                # Remove @ or + if present
                if user.startswith(('@', '+')):
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
                # Remove @ or + if present
                if user.startswith(('@', '+')):
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

    def _update_users_list_safe(self):
        """Internal method to safely update users list in the GUI thread"""
        try:
            self.users_listbox.delete(0, tk.END)
            for user in sorted(self.users):
                self.users_listbox.insert(tk.END, user)
        except Exception as e:
            print(f"Error in _update_users_list_safe: {e}")
            
    def update_users_list(self):

        """Update the users listbox safely"""
        if not self.is_closing:
            try:
                self.window.after(0, self._update_users_list_safe)
            except Exception as e:
                print(f"Error updating users list: {e}")

        """Update the users listbox with current users"""
        try:
            if not self.window.winfo_exists():
                return
                
            print(f"DEBUG - Updating users list for {self.channel_name}")  # Debug print
            print(f"DEBUG - Current users: {self.users}")  # Debug print
            
            self.users_listbox.delete(0, tk.END)
            
            # Sort users with ops (@) first, then voice (+), then regular users
            sorted_users = sorted(self.users, key=lambda x: (
                (0 if x.startswith('@') else 1 if x.startswith('+') else 2),
                x.lstrip('@+').lower()
            ))
            
            for user in sorted_users:
                self.users_listbox.insert(tk.END, user)
                
            # Update users count
            self.users_label.config(text=f"Users ({len(self.users)})")
            print(f"DEBUG - Updated users list with {len(self.users)} users")  # Debug print
            
        except Exception as e:
            print(f"Error updating users list: {e}")
            
    def end_batch_update(self):
        """End a batch update and process pending updates"""
        if self.batch_updating:
            self.batch_updating = False
            if self.names_buffer:
                print(f"DEBUG - Processing batch update for {self.channel_name}")  # Debug print
                print(f"DEBUG - Names buffer: {self.names_buffer}")  # Debug print
                self.users = self.names_buffer.copy()
                self.update_users_list()
    
    def _do_update_users_list(self):
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
            
            # Insert timestamp with gray color
            self.chat_display.insert(tk.END, timestamp + " ", 'timestamp')
            
            # Handle different types of messages
            if message.startswith('* '):  # System messages
                if 'has joined' in message:
                    self.chat_display.insert(tk.END, message + '\n', 'join')
                elif 'has left' in message:
                    self.chat_display.insert(tk.END, message + '\n', 'part')
                elif 'has quit' in message:
                    self.chat_display.insert(tk.END, message + '\n', 'quit')
                elif 'is now known as' in message:
                    self.chat_display.insert(tk.END, message + '\n', 'nick')
            else:
                # Regular chat messages
                if ': ' in message:
                    username, text = message.split(': ', 1)
                    # Check if the message is from the current user
                    current_nick = self.irc_client.connections[self.server]['nickname']
                    if username == current_nick:
                        self.chat_display.insert(tk.END, username + ': ', 'my_username')
                    else:
                        self.chat_display.insert(tk.END, username + ': ', 'username')
                    self.chat_display.insert(tk.END, text + '\n', tag or 'message')
                else:
                    self.chat_display.insert(tk.END, message + '\n', tag or 'message')
            
            self.chat_display.see(tk.END)
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
        self.server = server  # Add server attribute
        
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
        server_data = self.irc_client.server_nodes.get(self.server)  # Use self.server instead
        if server_data and self.username in server_data['private_msgs']:
            self.irc_client.network_tree.delete(server_data['private_msgs'][self.username])
            del server_data['private_msgs'][self.username]
                
        # Clean up private windows dict
        if self.username in self.irc_client.private_windows:
            del self.irc_client.private_windows[self.username]
            
        # Destroy window
        self.window.destroy()
        
    def send_message(self, event=None):
        message = self.message_input.get()
        if message:
            self.irc_client.send_private_message(self.username, message, self.server)
            self.add_message(f"{self.irc_client.connections[self.server]['nickname']}: {message}")
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
    def __init__(self, default_server, default_port, default_nickname):
        self.connections = {}  # Dictionary to store server connections
        self.default_nickname = default_nickname
        self.channel_windows = {}
        self.private_windows = {}
        self.server_nodes = {}
        self.lock = threading.Lock()
        self.running = True
        self.current_server = None
        self.disconnecting = False
        
        # Create GUI
        self.create_status_window()
        
        self.preferences = {
            'theme': 'default'
        }
        #self.connect_to_server(default_server, default_port, default_nickname)
        
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
                # Send QUIT command to server
                self.send_command(f"QUIT :{quit_message}", server)
                
                # Close socket
                try:
                    self.connections[server]['socket'].shutdown(socket.SHUT_RDWR)
                    self.connections[server]['socket'].close()
                except:
                    pass
                del self.connections[server]
                
                # Remove server node and cleanup windows
                self.remove_server_node(server)
                
                self.add_status_message(f"Disconnected from {server}")
                
            except Exception as e:
                self.add_status_message(f"Error quitting {server}: {e}")

    def remove_server_node(self, server):
        """Remove a server node and all its children from the tree"""
        if server in self.server_nodes:
            # Delete all channel windows for this server
            channels_to_remove = []
            for channel_key in self.channel_windows.keys():
                if channel_key.startswith(f"{server}:"):
                    channels_to_remove.append(channel_key)
            
            for channel_key in channels_to_remove:
                self.channel_windows[channel_key].window.destroy()
                del self.channel_windows[channel_key]

            # Delete all PM windows for this server
            pms_to_remove = []
            for username, window in self.private_windows.items():
                if window.server == server:
                    pms_to_remove.append(username)
            
            for username in pms_to_remove:
                self.private_windows[username].window.destroy()
                del self.private_windows[username]

            # Remove from tree and clean up server_nodes
            self.network_tree.delete(self.server_nodes[server]['node'])
            del self.server_nodes[server]
            
            if server == self.current_server:
                self.current_server = None
            
            print(f"Removed server node: {server}")  # Debug print



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
        """Add a private message node to the correct server in the tree"""
        if server in self.server_nodes:
            server_data = self.server_nodes[server]
            if 'private_msgs' not in server_data:
                server_data['private_msgs'] = {}
            
            pm_text = f" PM: {username}"
            pm_id = self.network_tree.insert(
                server_data['node'], 
                'end', 
                text=pm_text, 
                tags=('pm',),
                image=self.pm_icon
            )
            server_data['private_msgs'][username] = pm_id
            print(f"Added PM node with icon: {username}")  # Debug print

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
        """Create a new private message window"""
        if server is None:
            server = self.current_server
            
        # Create a unique key for the private window
        pm_key = f"{server}:{username}"
        
        if username not in self.private_windows:
            self.private_windows[username] = PrivateWindow(self, username, server)
            # Only add to tree if it doesn't exist
            server_data = self.server_nodes.get(server)
            if server_data and username not in server_data.get('private_msgs', {}):
                self.add_pm_node(username, server)
            self.add_status_message(f"Started private chat with {username} on {server}")
        else:
            # If window exists, just show it
            self.private_windows[username].window.deiconify()
            self.private_windows[username].window.lift()



    def send_private_message(self, username, message, server):
        self.send_command(f"PRIVMSG {username} :{message}", server)
        
        
    def create_channel_window(self, channel, server):
        """Create a new channel window"""
        channel_key = f"{server}:{channel}"
        if channel_key not in self.channel_windows:
            self.channel_windows[channel_key] = ChannelWindow(self, channel, server)
            self.add_channel_node(channel)  # Add to tree
            self.send_command(f"NAMES {channel}", server)
            self.add_status_message(f"Joined channel: {channel} on {server}")



    def create_status_window(self):
        self.status_window = tk.Tk()
        self.status_window.title("rootX - Status")
        self.status_window.geometry("1000x600")

        # Create menu bar
        self.menubar = tk.Menu(self.status_window)
        self.status_window.config(menu=self.menubar)
        
        # rootX menu with updated commands
        self.rootx_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="rootX", menu=self.rootx_menu)
        self.rootx_menu.add_command(label="Connect to Server...", command=self.show_connect_dialog)
        self.rootx_menu.add_command(label="Disconnect from Server...", command=self.show_disconnect_dialog)
        self.rootx_menu.add_separator()
        self.rootx_menu.add_command(label="Exit", command=self.status_window.quit)
        
        # View menu
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Network Tree")
        self.view_menu.add_command(label="Status Window")
        
        # Server menu with updated commands
        self.server_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Server", menu=self.server_menu)
        self.server_menu.add_command(label="Join Channel...", command=self.show_join_dialog)
        self.server_menu.add_command(label="List Channels", command=self.show_channel_list)
        self.server_menu.add_separator()
        self.server_menu.add_command(label="Server Settings...", command=self.show_server_settings)

        # Settings menu
        self.settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Preferences...")
        self.settings_menu.add_command(label="Theme Settings...")
        
        # Help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Documentation")
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About rootX", command=self.show_about_dialog)

        # Create main frame to hold everything
        main_frame = ttk.Frame(self.status_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create main container with paned window
        self.main_container = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left frame for network tree
        self.left_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.left_frame, weight=1)



        # Load icons from files with error checking
        import os
        icons_dir = "icons"
        
        # Create icons directory if it doesn't exist
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
            print(f"Created icons directory: {icons_dir}")
        
        # Define icon paths
        server_icon_path = os.path.join(icons_dir, "server.png")
        channel_icon_path = os.path.join(icons_dir, "channel.png")
        pm_icon_path = os.path.join(icons_dir, "pm.png")

        try:
            # Check if icons exist
            if not all(os.path.exists(p) for p in [server_icon_path, channel_icon_path, pm_icon_path]):
                print("Some icons are missing. Downloading icons...")
                import urllib.request
                
                # Download icons
                icons = {
                    server_icon_path: "https://raw.githubusercontent.com/feathericons/feather/master/icons/server.png",
                    channel_icon_path: "https://raw.githubusercontent.com/feathericons/feather/master/icons/hash.png",
                    pm_icon_path: "https://raw.githubusercontent.com/feathericons/feather/master/icons/message-circle.png"
                }
                
                for path, url in icons.items():
                    if not os.path.exists(path):
                        print(f"Downloading {path}...")
                        urllib.request.urlretrieve(url, path)
            
            # Load icons
            self.server_icon = tk.PhotoImage(file=server_icon_path).subsample(2, 2)  # Adjusted scale
            self.channel_icon = tk.PhotoImage(file=channel_icon_path).subsample(2, 2)
            self.pm_icon = tk.PhotoImage(file=pm_icon_path).subsample(2, 2)
            print("Icons loaded successfully")
            
        except Exception as e:
            print(f"Error loading icons: {e}")
            # Fallback to simple colored dots if icon loading fails
            self.server_icon = tk.PhotoImage(data='R0lGODlhDQANAIAAAP/////gaAAAACH5BAEAAAEALAAAAAANABAAAAIZjI+py+0Po5y02ouz3rz7D4biSJbmiabqUQAAOw==')
            self.channel_icon = tk.PhotoImage(data='R0lGODlhDQANAIAAAP//AAAAACH5BAEAAAEALAAAAAANABAAAAIZjI+py+0Po5y02ouz3rz7D4biSJbmiabqUQAAOw==')
            self.pm_icon = tk.PhotoImage(data='R0lGODlhDQANAIAAAP//AP//ACH5BAEAAAEALAAAAAANABAAAAIZjI+py+0Po5y02ouz3rz7D4biSJbmiabqUQAAOw==')
            print("Using fallback icons")
        try:
            # Load icons with larger subsample values to make them smaller
            self.server_icon = tk.PhotoImage(file=server_icon_path).subsample(8, 8)  # Changed from 2,2 to 4,4
            self.channel_icon = tk.PhotoImage(file=channel_icon_path).subsample(8, 8)
            self.pm_icon = tk.PhotoImage(file=pm_icon_path).subsample(8, 8)
            print("Icons loaded successfully")
            
        except Exception as e:
            print(f"Error loading icons: {e}")
            # Fallback icons remain the same...

        # Create network tree with smaller row height
        style = ttk.Style()
        style.configure("Treeview", rowheight=20)  # Changed from 25 to 20

        self.network_tree = ttk.Treeview(self.left_frame, show='tree', style="Treeview")
        self.network_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar for network tree
        tree_scroll = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.network_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.network_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Bind double-click event
        self.network_tree.bind('<Double-Button-1>', self.toggle_window_from_tree)
        
        # Create right frame for status messages and input
        self.right_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.right_frame, weight=2)
        
        # Create status display
        self.status_display = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD)
        self.status_display.pack(fill=tk.BOTH, expand=True)
        
        # Create input frame
        self.input_frame = ttk.Frame(self.right_frame)
        self.input_frame.pack(fill=tk.X, pady=5)
        
        # Create command input
        self.command_input = ttk.Entry(self.input_frame)
        self.command_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.command_input.bind('<Return>', self.handle_status_input)
        
        # Create send button
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.handle_status_command)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # Configure text tags
        self.status_display.tag_configure('timestamp', foreground='gray')
        self.status_display.tag_configure('message', foreground='white')
        
        # Add initial instructions
        self.add_status_message("Welcome to rootX IRC Client!")
        self.add_status_message("Use /server <server> [port] - Connect to a new server")
        self.add_status_message("Use /join #channel to join a channel")
        self.add_status_message("Use /list to list channels (Be careful with this command)")
        self.add_status_message("Use /quit to exit")
        self.add_status_message("Use /help for help")


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

        settings_window = tk.Toplevel(self.status_window)
        settings_window.title(f"Server Settings - {self.current_server}")
        settings_window.geometry("500x500")
        settings_window.transient(self.status_window)
        settings_window.grab_set()

        # Create notebook for tabs
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # General Settings Tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")

        # Current connection info
        ttk.Label(general_frame, text="Current Connection", font=("", 10, "bold")).pack(pady=10)
        ttk.Label(general_frame, text=f"Server: {self.current_server}").pack(pady=2)
        ttk.Label(general_frame, text=f"Nickname: {self.connections[self.current_server]['nickname']}").pack(pady=2)

        # Nickname change frame
        nick_frame = ttk.LabelFrame(general_frame, text="Change Nickname")
        nick_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(nick_frame, text="New Nickname:").pack(pady=5)
        new_nick_entry = ttk.Entry(nick_frame)
        new_nick_entry.pack(padx=20, fill=tk.X, pady=5)

        def change_nickname():
            new_nick = new_nick_entry.get().strip()
            if new_nick:
                self.send_command(f"NICK {new_nick}", self.current_server)
                new_nick_entry.delete(0, tk.END)

        ttk.Button(nick_frame, text="Change Nickname", command=change_nickname).pack(pady=5)

        # Away Status frame
        away_frame = ttk.LabelFrame(general_frame, text="Away Status")
        away_frame.pack(fill=tk.X, padx=10, pady=10)
        
        away_message = ttk.Entry(away_frame)
        away_message.pack(padx=20, fill=tk.X, pady=5)

        def set_away():
            message = away_message.get().strip()
            if message:
                self.send_command(f"AWAY :{message}", self.current_server)
            else:
                self.send_command("AWAY", self.current_server)  # Remove away status

        ttk.Button(away_frame, text="Set Away", command=set_away).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(away_frame, text="Return", 
                command=lambda: self.send_command("AWAY", self.current_server)).pack(side=tk.LEFT, pady=5)

        # Channel Settings Tab
        channel_frame = ttk.Frame(notebook)
        notebook.add(channel_frame, text="Channels")

        # Auto-join channels
        ttk.Label(channel_frame, text="Auto-join Channels", font=("", 10, "bold")).pack(pady=10)
        channels_list = tk.Listbox(channel_frame, height=6)
        channels_list.pack(fill=tk.X, padx=10)

        # Add current channels
        if self.current_server in self.server_nodes:
            for channel in self.server_nodes[self.current_server]['channels'].keys():
                channels_list.insert(tk.END, channel)

        # Buttons frame
        buttons_frame = ttk.Frame(channel_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)

        def add_channel():
            channel = channel_entry.get().strip()
            if channel:
                if not channel.startswith('#'):
                    channel = '#' + channel
                if channel not in channels_list.get(0, tk.END):
                    channels_list.insert(tk.END, channel)
                channel_entry.delete(0, tk.END)

        def remove_channel():
            selection = channels_list.curselection()
            if selection:
                channels_list.delete(selection)

        channel_entry = ttk.Entry(buttons_frame)
        channel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(buttons_frame, text="Add", command=add_channel).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Remove", command=remove_channel).pack(side=tk.LEFT, padx=2)

        # Update the menu command to show settings
        self.server_menu.entryconfig("Server Settings...", command=self.show_server_settings)


    def show_join_dialog(self):
        """Show dialog for joining a channel"""
        if not self.connections:
            self.add_status_message("Not connected to any server")
            return
            
        join_window = tk.Toplevel(self.status_window)
        join_window.title("Join Channel")
        join_window.geometry("300x200")
        join_window.transient(self.status_window)
        join_window.grab_set()
        
        # Server selection
        ttk.Label(join_window, text="Server:").pack(pady=5)
        server_var = tk.StringVar(value=self.current_server)
        server_combo = ttk.Combobox(join_window, textvariable=server_var)
        server_combo['values'] = list(self.connections.keys())
        server_combo.pack(padx=20, fill=tk.X)
        
        # Channel input
        ttk.Label(join_window, text="Channel:").pack(pady=5)
        channel_entry = ttk.Entry(join_window)
        channel_entry.pack(padx=20, fill=tk.X)
        channel_entry.insert(0, "#")
        
        def join():
            server = server_var.get()
            channel = channel_entry.get().strip()
            if server and channel:
                if channel[0] != '#':
                    channel = '#' + channel
                join_window.destroy()
                # Set current server before joining
                self.current_server = server
                # Create channel window and add to tree
                channel_key = f"{server}:{channel}"
                if channel_key not in self.channel_windows:
                    self.channel_windows[channel_key] = ChannelWindow(self, channel, server)
                    self.add_channel_node(channel)  # Add to tree
                # Send join command
                self.send_command(f"JOIN {channel}", server)
            else:
                self.add_status_message("Please enter a channel name")
        
        ttk.Button(join_window, text="Join", command=join).pack(pady=20)

    def show_channel_list(self):
        """Show list of channels on current server"""
        if not self.current_server:
            self.add_status_message("Not connected to any server")
            return
            
        # Create channel list window
        list_window = tk.Toplevel(self.status_window)
        list_window.title(f"Channel List - {self.current_server}")
        list_window.geometry("600x400")
        
        frame = ttk.Frame(list_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add search entry
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        channels_frame = ttk.Frame(frame)
        channels_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create listbox and scrollbars with buffer updates
        scrollbar_y = ttk.Scrollbar(channels_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(channels_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        channels_list = tk.Listbox(
            channels_frame,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        channels_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=channels_list.yview)
        scrollbar_x.config(command=channels_list.xview)
        
        status_label = ttk.Label(frame, text="Requesting channel list...")
        status_label.pack(pady=5)
        
        # Store channels and implement batch updates
        all_channels = []
        channel_buffer = []
        BUFFER_SIZE = 50
        update_after_id = None
    
        
        def update_list(search_term=""):
            channels_list.delete(0, tk.END)
            filtered_channels = [ch for ch in all_channels if search_term.lower() in ch.lower()]
            for channel in filtered_channels:
                channels_list.insert(tk.END, channel)
        
        def delayed_search(*args):
            nonlocal update_after_id
            if update_after_id:
                list_window.after_cancel(update_after_id)
            update_after_id = list_window.after(300, lambda: update_list(search_entry.get()))
        
        search_entry.bind('<KeyRelease>', delayed_search)
        
        # Store channels and implement batch updates
        all_channels = []  # Clear the list at the start
        seen_channels = set()
        channel_buffer = []
        BUFFER_SIZE = 50
        update_after_id = None

        def handle_list_response(channel_info):
            nonlocal channel_buffer
            channel_text = f"{channel_info['channel']} ({channel_info['users']}) {channel_info['topic']}"
            
            # Use set to check for duplicates
            if channel_info['channel'] not in seen_channels:
                seen_channels.add(channel_info['channel'])
                channel_buffer.append(channel_text)
                
                # Update in batches
                if len(channel_buffer) >= BUFFER_SIZE:
                    all_channels.extend(channel_buffer)
                    if not search_entry.get():  # Only update display if no search filter
                        for channel in channel_buffer:
                            channels_list.insert(tk.END, channel)
                    channel_buffer = []
                    status_label.config(text=f"Found {len(all_channels)} channels")
                    list_window.update_idletasks()
        
        # Set the callback for this instance
        self.channel_list_callback = handle_list_response
        
        def join_selected(event):
            selection = channels_list.curselection()
            if selection:
                channel = channels_list.get(selection[0]).split()[0]  # Get just the channel name
                # Set current server before joining
                self.current_server = self.current_server
                # Create channel window and add to tree
                channel_key = f"{self.current_server}:{channel}"
                if channel_key not in self.channel_windows:
                    self.channel_windows[channel_key] = ChannelWindow(self, channel, self.current_server)
                    self.add_channel_node(channel)  # Add to tree
                # Send join command
                self.send_command(f"JOIN {channel}", self.current_server)
        
        channels_list.bind('<Double-Button-1>', join_selected)
        
        # Request channel list
        self.send_command("LIST", self.current_server)

    def show_connect_dialog(self):
        """Show dialog for connecting to a new server"""
        connect_window = tk.Toplevel(self.status_window)
        connect_window.title("Connect to Server")
        connect_window.geometry("300x250")
        connect_window.transient(self.status_window)
        connect_window.grab_set()  # Make window modal
        
        # Create and pack widgets
        ttk.Label(connect_window, text="Server:").pack(pady=5)
        server_entry = ttk.Entry(connect_window)
        server_entry.pack(padx=20, fill=tk.X)
        server_entry.insert(0, "irc.libera.chat")
        
        ttk.Label(connect_window, text="Port:").pack(pady=5)
        port_entry = ttk.Entry(connect_window)
        port_entry.pack(padx=20, fill=tk.X)
        port_entry.insert(0, "6667")
        
        ttk.Label(connect_window, text="Nickname:").pack(pady=5)
        nick_entry = ttk.Entry(connect_window)
        nick_entry.pack(padx=20, fill=tk.X)
        nick_entry.insert(0, "PythonUser")
        
        def connect():
            server = server_entry.get().strip()
            try:
                port = int(port_entry.get().strip())
                nickname = nick_entry.get().strip()
                
                if server and port and nickname:
                    connect_window.destroy()
                    self.connect_to_server(server, port, nickname)
                else:
                    self.add_status_message("Please fill in all fields")
            except ValueError:
                self.add_status_message("Port must be a number")
        
        ttk.Button(connect_window, text="Connect", command=connect).pack(pady=20)

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
                        self.connections[server]['socket'].close()
                    except:
                        pass
                    del self.connections[server]
                    
                    # Use the dedicated method to remove server node and all its children
                    self.remove_server_node(server)
        finally:
            self.disconnecting = False

    def show_disconnect_dialog(self):
        """Show dialog for disconnecting from a server"""
        if not self.connections:
            self.add_status_message("No active connections")
            return
            
        disconnect_window = tk.Toplevel(self.status_window)
        disconnect_window.title("Disconnect from Server")
        disconnect_window.geometry("300x200")
        disconnect_window.transient(self.status_window)
        disconnect_window.grab_set()  # Make window modal
        
        ttk.Label(disconnect_window, text="Select Server:").pack(pady=5)
        
        # Create listbox for servers
        server_listbox = tk.Listbox(disconnect_window, height=5)
        server_listbox.pack(padx=20, fill=tk.BOTH, expand=True)
        
        # Add connected servers to listbox
        for server in self.connections.keys():
            server_listbox.insert(tk.END, server)
        
        def disconnect():
            selection = server_listbox.curselection()
            if selection:
                server = server_listbox.get(selection[0])
                disconnect_window.destroy()
                self.quit_server(server, "Disconnecting...")
            else:
                self.add_status_message("Please select a server")
        
        ttk.Button(disconnect_window, text="Disconnect", command=disconnect).pack(pady=20)

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
                
    def add_status_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.status_display.insert(tk.END, f"{timestamp} {message}\n")
        self.status_display.see(tk.END)
        
    
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
            
            if data.startswith('PING') or data.startswith('PONG'):
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
                            channel = self.pending_bans[target_nick]
                            ban_mask = f'*!{user_host}'
                            self.send_command(f'MODE {channel} +b {ban_mask}', server)
                            self.send_command(f'KICK {channel} {target_nick} Banned', server)
                            del self.pending_bans[target_nick]
                            
                    elif '318' in data:  # End of WHOIS
                        if target_nick in self.pending_bans:
                            del self.pending_bans[target_nick]
                            
                except Exception as e:
                    self.add_status_message(f"Error handling WHOIS for ban: {e}")

            
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



    def receive_messages(self, server):
        """Receive messages from a specific server"""
        while self.running:
            try:
                with self.lock:
                    if server not in self.connections:
                        break
                    
                    conn = self.connections[server]
                    try:
                        # Set a timeout on the socket
                        conn['socket'].settimeout(180)  # 3 minutes timeout
                        data = conn['socket'].recv(4096).decode('utf-8')
                        if not data:
                            raise ConnectionError("Server closed connection")
                    except (socket.timeout, TimeoutError):
                        raise ConnectionError("Connection timed out")
                    except UnicodeDecodeError:
                        try:
                            data = conn['socket'].recv(4096).decode('latin-1')
                        except:
                            data = conn['socket'].recv(4096).decode('iso-8859-1')
                    
                    if not data:
                        break
                    
                    # Process received data
                    conn['buffer'] += data
                    lines = conn['buffer'].split('\r\n')
                    conn['buffer'] = lines.pop()
                    
                    for line in lines:
                        if line:  # Only process non-empty lines
                            self.handle_server_message(line, server)
                        
            except Exception as e:
                self.add_status_message(f"Error receiving from {server}: {e}")
                # Clean up the connection
                with self.lock:
                    if server in self.connections:
                        try:
                            self.connections[server]['socket'].close()
                        except:
                            pass
                        del self.connections[server]
                        self.remove_server_node(server)
                break
                
    def connect_to_server(self, server, port, nickname):
        """Connect to a new server"""
        try:
            # Check if already connected
            if server in self.connections:
                self.add_status_message(f"Already connected to {server}")
                return False

            # Create new socket connection (simplified)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server, port))
            
            # Store connection info
            self.connections[server] = {
                'socket': sock,
                'nickname': nickname,
                'channels': {},
                'buffer': ""
            }
            
            # Add server to tree
            self.add_server_node(server)
            self.current_server = server
            
            # Send initial commands
            self.send_command(f"NICK {nickname}", server)
            self.send_command(f"USER {nickname} 0 * :{nickname}", server)
            
            # Start receive thread
            receive_thread = threading.Thread(target=self.receive_messages, args=(server,))
            receive_thread.daemon = True
            receive_thread.start()
            
            self.add_status_message(f"Connected to {server}")
            return True
            
        except Exception as e:
            self.add_status_message(f"Failed to connect to {server}: {e}")
            if server in self.connections:
                del self.connections[server]
            if server in self.server_nodes:
                self.remove_server_node(server)
            return False
                
    def run(self):
        """Start the IRC client"""
        try:
            # Start the GUI main loop
            self.status_window.mainloop()
        finally:
            # Cleanup when the program exits
            self.running = False
            with self.lock:
                for server, conn in self.connections.items():
                    try:
                        conn['socket'].close()
                    except:
                        pass

def main():
    server = "irc.libera.chat"
    port = 6667
    nickname = "c0d3Ninja"
    
    client = IRCClient(server, port, nickname)
    # Connect to default server after initialization
    client.connect_to_server(server, port, nickname)
    client.run()


if __name__ == "__main__":
    main()