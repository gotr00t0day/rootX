"""
RootX Script Engine - mIRC-like scripting language for the IRC client

Syntax Reference:
================

EVENTS:
    on <EVENT>:<match>:<target>:{ commands }
    
    Events:
        TEXT     - Triggered on channel messages (on TEXT:*hello*:#:{ msg $chan Hi! })
        MSG      - Triggered on private messages (on MSG:*hello*:?:{ msg $nick Hi! })
        ACTION   - Triggered on /me actions
        JOIN     - Triggered when someone joins (on JOIN:#channel:{ msg $chan Welcome $nick! })
        PART     - Triggered when someone leaves
        QUIT     - Triggered when someone quits
        KICK     - Triggered on kicks
        NICK     - Triggered on nick changes
        NOTICE   - Triggered on notices
        MODE     - Triggered on mode changes
        CONNECT  - Triggered when connecting to a server
        DISCONNECT - Triggered when disconnecting
        INPUT    - Triggered on user input (before sending)
        WHOIS    - Triggered when WHOIS data is received (on WHOIS:*:*:{ commands })
    
    Match patterns:
        *        - Match anything
        *text*   - Contains text
        text*    - Starts with text
        *text    - Ends with text
        exact    - Exact match

ALIASES:
    alias /commandname { commands }
    alias /greet { msg $chan Hello everyone from $me! }

FUNCTIONS:
    function name(param1, param2) { return value }
    function add(a, b) { return $calc(a + b) }
    
    Usage:
        set %result = $add(5, 3)  ; Returns "8"
        msg $chan Result: $add(10, 20)  ; Returns "30"
    
    Parameters:
        - Access parameters as $1, $2, $3, etc. or by name
        - Use 'return <value>' to return a result
        - Functions can be called anywhere identifiers are used

VARIABLES:
    Local:  %var = value
    Global: %%var = value (persists across script reloads)

LISTS (arrays):
    Local:  @listname
    Global: @@listname (persists across script reloads)
    
    Commands:
        listadd @listname <value>        - Add item to list
        listdel @listname <index|value>  - Remove item from list
        listclear @listname              - Clear all items from list
        listinsert @listname <index> <value> - Insert item at index
    
    Identifiers:
        $list(@listname,N)              - Get item at index N
        $list(@listname,count)          - Get number of items in list
        $list(@listname,find,value)     - Find index of value (-1 if not found)
        $list(@listname,exists,value)   - Check if value exists (True/False)
    
    For Loop (iterate over list):
        for (%var in @listname) { commands }
        
        Example:
            listadd @names Alice
            listadd @names Bob
            for (%person in @names) {
                echo Hello %person
            }
    
IDENTIFIERS (read-only):
    Basic:
        $nick    - Nick of the person who triggered the event
        $chan    - Current channel
        $me      - Your nickname
        $server  - Current server
        $target  - Target of the message (channel or nick)
        $1-$N    - Word tokens from the message ($1 is first word, etc.)
        $1-      - All words from $1 onwards
        $text    - Full message text
        $time    - Current time (HH:MM:SS)
        $date    - Current date (YYYY-MM-DD)
        $version - Client version
    
    Hostmask:
        $address - Full hostmask (nick!user@host) of the person who triggered the event
        $address(nick) - Get hostmask of a specific user (looks up stored hostmask)
        $user    - Username portion (~username)
        $host    - Hostname/IP address
        $ip      - Extracted IP address from hostname
                   (handles encoded IPs like c-73-244-70-171.isp.net → 73.244.70.171)
    
    String Functions:
        $len(text) - Length of text
        $upper(text) - Uppercase
        $lower(text) - Lowercase
        $left(text,N) - First N characters
        $right(text,N) - Last N characters
        $mid(text,start,len) - Substring
        $pos(text,search) - Find position (1-indexed, 0 if not found)
        $replace(text,old,new) - Replace text
        $remove(text,substring) - Remove substring
        $str(text,N) - Repeat text N times
        $chr(N) - ASCII code to character
        $asc(char) - Character to ASCII code
        $strip(text) - Remove IRC color codes
    
    Tokenization:
        $gettok(text,N,delim) - Get Nth token (delim is ASCII code)
        $numtok(text,delim) - Count tokens
        $findtok(text,search,start,delim) - Find token position
        $addtok(text,token,delim) - Add token if not present
        $remtok(text,token,delim) - Remove token
        $reptok(text,old,new,delim) - Replace token
    
    Math Functions:
        $rand(N) - Random number 0 to N-1
        $calc(expr) - Calculate expression (e.g., 5+3*2)
        $round(N,decimals) - Round number
        $abs(N) - Absolute value
        $sqrt(N) - Square root
        $floor(N) - Round down
        $ceil(N) - Round up
    
    File I/O:
        $read(file) - Read random line from file
        $read(file,N) - Read line N from file
        $exists(file) - Check if file exists (True/False)
        $lines(file) - Count lines in file
    
    User Levels:
        $level - Current user's level
        $level(nick) - Get user's level (0 if not set)
        $islevel(nick,level) - Check if user has level >= specified (returns True/False)
    
    Network Functions:
        $ip(hostname) - Extract IP from hostname or encoded format
                        Examples: $ip(c-73-244-70-171.isp.net) → 73.244.70.171
                                  $ip(73.244.70.171) → 73.244.70.171
        
        $whois(nick,field) - Get WHOIS information for a user
                        First, send a WHOIS command: raw WHOIS nickname
                        Then use $whois() in the WHOIS event handler
                        
                        Available fields:
                            nick      - Nickname
                            username  - Username (~username)
                            hostname  - Hostname/IP
                            realname  - Real name
                            hostmask  - Full hostmask (nick!user@host)
                            server    - IRC server name
                            idle      - Idle time in seconds
                            channels  - List of channels user is in
                        
                        Example:
                            on TEXT:!whois*:#:{
                                raw WHOIS $2
                            }
                            
                            on WHOIS:*:*:{
                                set %whois_nick = $whois($nick, nick)
                                set %whois_host = $whois($nick, hostname)
                                msg $chan WHOIS: %whois_nick is on %whois_host
                            }

COMMANDS:
    IRC Commands:
        msg <target> <message>     - Send a message
        notice <target> <message>  - Send a notice
        me <target> <action>       - Send an action (/me)
        join <channel> [key]       - Join a channel
        part <channel> [message]   - Leave a channel
        quit [message]             - Quit from server
        nick <newnick>             - Change nickname
        kick <channel> <nick> [reason] - Kick a user
        ban <channel> <mask>       - Ban a user
        mode <target> <modes>      - Set modes
    
    Script Control:
        echo <message>             - Display message locally
        halt                       - Stop script execution
        return [value]             - Return from alias
        sleep <seconds>            - Sleep for specified seconds (supports decimals)
        timer <name> <interval> <reps> { commands } - Create a timer
        timer <name> off           - Stop a timer
    
    File I/O:
        write <file> <text>        - Append text to file
        read <file> [line]         - Read and display from file
        remove <file>              - Delete file
    
    User Levels:
        setlevel <nick> <level>    - Set user's access level (0-1000)
        remlevel <nick>            - Remove user's access level
        getlevel <nick>            - Display user's current level

CONTROL FLOW:
    if (<condition>) { commands }
    if (<condition>) { commands } else { commands }
    while (<condition>) { commands }
    for (%var in @listname) { commands }  - Iterate over list items
    
    Conditions:
        $var == value
        $var != value
        $var > value
        $var < value
        $var >= value
        $var <= value
        $var isin text
        $var !isin text
        text iswm pattern  (wildcard match)

EXAMPLE SCRIPTS:
    
    ; ===== Basic Event Handling =====
    ; Greet users who join
    on JOIN:#mychannel:{
        msg $chan Welcome to the channel, $nick!
    }
    
    ; Respond to !hello command in channels
    on TEXT:!hello*:#:{
        msg $chan Hello $nick! You said: $1-
    }
    
    ; Respond to private messages containing "help"
    on MSG:*help*:?:{
        msg $nick Hi! I can help you with that.
    }
    
    ; ===== Custom Commands (Aliases) =====
    alias /greet {
        if ($1) {
            msg $chan Hello $1!
        }
        else {
            msg $chan Hello everyone!
        }
    }
    
    ; ===== User-Defined Functions =====
    ; Simple math function
    function add(a, b) {
        return $calc($1 + $2)
    }
    
    ; Function with conditional logic
    function max(a, b) {
        if ($1 > $2) {
            return $1
        }
        else {
            return $2
        }
    }
    
    ; Usage in event handler
    on TEXT:!calc*:#:{
        set %result = $add($2, $3)
        msg $chan $2 + $3 = %result
    }
    
    ; ===== Lists (Arrays) =====
    ; Add users to a list
    on TEXT:!adduser*:#:{
        if ($2) {
            listadd @users $2
            msg $chan Added $2 to user list
        }
    }
    
    ; Display all users in list
    on TEXT:!listusers:#:{
        set %count = $list(@users, count)
        msg $chan Total users: %count
        for (%user in @users) {
            msg $chan - %user
        }
    }
    
    ; ===== File I/O =====
    ; Save quotes to file
    on TEXT:!addquote*:#:{
        write quotes.txt [$nick] $2-
        msg $chan Quote added!
    }
    
    ; Read random quote
    on TEXT:!quote:#:{
        if ($exists(quotes.txt)) {
            msg $chan $read(quotes.txt)
        }
    }
    
    ; ===== WHOIS Information =====
    ; Request WHOIS for a user
    on TEXT:!whois*:#:{
        if ($2) {
            raw WHOIS $2
            msg $chan Requesting WHOIS information for $2...
        }
    }
    
    ; Handle WHOIS response
    on WHOIS:*:*:{
        set %whois_nick = $whois($nick, nick)
        set %whois_user = $whois($nick, username)
        set %whois_host = $whois($nick, hostname)
        set %whois_real = $whois($nick, realname)
        set %whois_hostmask = $whois($nick, hostmask)
        set %whois_server = $whois($nick, server)
        set %whois_idle = $whois($nick, idle)
        set %whois_channels = $whois($nick, channels)
        
        ; Display WHOIS information
        msg $chan === WHOIS: %whois_nick ===
        msg $chan Hostmask: %whois_hostmask
        msg $chan Server: %whois_server
        if (%whois_idle) {
            msg $chan Idle: %whois_idle seconds
        }
        if (%whois_channels) {
            msg $chan Channels: %whois_channels
        }
    }
    
    ; ===== Hostmask Lookup =====
    ; Get hostmask of a user
    on TEXT:!gethost*:#:{
        if ($2) {
            set %hostmask = $address($2)
            if (%hostmask) {
                msg $chan Hostmask of $2: %hostmask
            }
            else {
                msg $chan No hostmask found for $2. User may not be in channel.
            }
        }
    }
    
    ; ===== User Levels =====
    ; Set user level
    on TEXT:!setlevel*:#:{
        if ($level >= 500) {
            if ($2 && $3) {
                setlevel $2 $3
                msg $chan Set level for $2 to $3
            }
        }
    }
    
    ; Check user level
    on TEXT:!checklevel*:#:{
        if ($2) {
            set %user_level = $level($2)
            msg $chan $2 has level: %user_level
        }
    }
    
    ; ===== String Manipulation =====
    ; Uppercase conversion
    on TEXT:!upper*:#:{
        if ($2) {
            msg $chan $upper($2)
        }
    }
    
    ; String length
    on TEXT:!len*:#:{
        if ($2) {
            set %length = $len($2)
            msg $chan Length of "$2": %length characters
        }
    }
    
    ; ===== Math Operations =====
    ; Calculator
    on TEXT:!calc*:#:{
        if ($2-) {
            set %result = $calc($2-)
            msg $chan $2- = %result
        }
    }
    
    ; ===== Tokenization =====
    ; Parse comma-separated values
    on TEXT:!parse*:#:{
        if ($2) {
            set %count = $numtok($2, 44)  ; 44 = comma ASCII
            msg $chan Found %count items
            set %second = $gettok($2, 2, 44)
            msg $chan Second item: %second
        }
    }
"""

import re
import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Tuple
import traceback


class ScriptEvent:
    """Represents a script event handler"""
    def __init__(self, event_type: str, match_pattern: str, target: str, commands: str):
        self.event_type = event_type.upper()
        self.match_pattern = match_pattern
        self.target = target  # Channel/target pattern
        self.commands = commands
        self.enabled = True
    
    def matches(self, text: str, target: str) -> bool:
        """Check if this event matches the given text and target"""
        # Check target pattern
        if self.target != '*':
            if not self._wildcard_match(target, self.target):
                return False
        
        # Check text pattern
        if self.match_pattern == '*':
            return True
        return self._wildcard_match(text, self.match_pattern)
    
    def _wildcard_match(self, text: str, pattern: str) -> bool:
        """Simple wildcard matching (* matches anything)"""
        if pattern == '*':
            return True
        
        # Special case: # means any channel (starts with #)
        if pattern == '#':
            return text.startswith('#')
        
        # Special case: ? means private message
        if pattern == '?':
            return not text.startswith('#')
        
        text = text.lower()
        pattern = pattern.lower()
        
        if pattern.startswith('*') and pattern.endswith('*'):
            return pattern[1:-1] in text
        elif pattern.startswith('*'):
            return text.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return text.startswith(pattern[:-1])
        else:
            return text == pattern


class ScriptAlias:
    """Represents a script alias (custom command)"""
    def __init__(self, name: str, commands: str):
        self.name = name.lower().lstrip('/')
        self.commands = commands
        self.enabled = True


class ScriptFunction:
    """Represents a user-defined function"""
    def __init__(self, name: str, params: List[str], commands: str):
        self.name = name.lower()
        self.params = params  # List of parameter names
        self.commands = commands
        self.enabled = True


class ScriptTimer:
    """Represents a script timer"""
    def __init__(self, name: str, interval: int, repetitions: int, commands: str):
        self.name = name
        self.interval = interval  # in milliseconds
        self.repetitions = repetitions  # 0 = infinite
        self.commands = commands
        self.current_rep = 0
        self.timer_id = None
        self.enabled = True


class ScriptEngine:
    """Main scripting engine for RootX IRC client"""
    
    def __init__(self, irc_client):
        self.irc_client = irc_client
        
        # Script storage
        self.events: List[ScriptEvent] = []
        self.aliases: Dict[str, ScriptAlias] = {}
        self.functions: Dict[str, ScriptFunction] = {}  # User-defined functions
        self.timers: Dict[str, ScriptTimer] = {}
        
        # Variables
        self.local_vars: Dict[str, str] = {}
        self.global_vars: Dict[str, str] = {}
        
        # Lists (arrays)
        self.local_lists: Dict[str, List[str]] = {}
        self.global_lists: Dict[str, List[str]] = {}
        
        # User levels system
        # Format: {nickname: level} where level is an integer
        # 0 = normal user, 50 = voice, 100 = operator, 500 = admin, 1000 = owner
        self.user_levels: Dict[str, int] = {}
        
        # Script execution state
        self.halt_execution = False
        self.return_value = None
        
        # Script files
        self.scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        self.loaded_scripts: Dict[str, str] = {}  # filename -> content
        self.script_paths: Dict[str, str] = {}  # filename -> full path (for external scripts)
        
        # Create scripts directory if it doesn't exist
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        
        # Load global variables and user levels
        self._load_global_vars()
        self._load_user_levels()
    
    # ==================== Script Loading ====================
    
    def load_script(self, filename: str) -> Tuple[bool, str]:
        """Load a script file from the scripts directory"""
        try:
            filepath = os.path.join(self.scripts_dir, filename)
            if not os.path.exists(filepath):
                return False, f"Script file not found: {filename}"
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the script
            success, msg = self.parse_script(content)
            if success:
                self.loaded_scripts[filename] = content
            return success, msg
            
        except Exception as e:
            return False, f"Error loading script: {e}"
    
    def load_script_from_path(self, filepath: str) -> Tuple[bool, str]:
        """Load a script file from any file path"""
        try:
            if not os.path.exists(filepath):
                return False, f"Script file not found: {filepath}"
            
            # Get just the filename for tracking
            filename = os.path.basename(filepath)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the script
            success, msg = self.parse_script(content)
            if success:
                # Store the filename and content
                self.loaded_scripts[filename] = content
                # Store the full path mapping for external scripts
                self.script_paths[filename] = filepath
            return success, msg
            
        except Exception as e:
            return False, f"Error loading script: {e}"
    
    def load_all_scripts(self) -> List[Tuple[str, bool, str]]:
        """Load all scripts from the scripts directory"""
        results = []
        if os.path.exists(self.scripts_dir):
            for filename in os.listdir(self.scripts_dir):
                if filename.endswith('.rsx') or filename.endswith('.txt'):
                    success, msg = self.load_script(filename)
                    results.append((filename, success, msg))
        return results
    
    def save_script(self, filename: str, content: str) -> Tuple[bool, str]:
        """Save a script to file"""
        try:
            filepath = os.path.join(self.scripts_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Script saved: {filename}"
        except Exception as e:
            return False, f"Error saving script: {e}"
    
    def parse_script(self, content: str) -> Tuple[bool, str]:
        """Parse script content and register events/aliases"""
        try:
            # Remove comments
            lines = []
            for line in content.split('\n'):
                line = line.split(';')[0].strip()  # Remove comments
                if line:
                    lines.append(line)
            
            content = '\n'.join(lines)
            
            # Parse events: on EVENT:match:target:{ commands }
            # Need to handle nested braces properly
            event_starts = []
            for match in re.finditer(r'on\s+(\w+):([^:]*):([^:]*)\s*:{', content, re.IGNORECASE):
                event_type, match_pattern, target = match.groups()
                event_starts.append((event_type, match_pattern, target, match.end()))
            
            for event_type, match_pattern, target, start_pos in event_starts:
                # Find the matching closing brace by counting brace depth
                brace_count = 1
                pos = start_pos
                while pos < len(content) and brace_count > 0:
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                if brace_count == 0:
                    commands = content[start_pos:pos-1].strip()
                    self.register_event(event_type, match_pattern, target, commands)
            
            # Parse aliases: alias /name { commands }
            # Need to handle nested braces properly
            alias_starts = []
            for match in re.finditer(r'alias\s+(/\w+)\s*{', content, re.IGNORECASE):
                alias_starts.append((match.group(1), match.end()))
            
            for name, start_pos in alias_starts:
                # Find the matching closing brace by counting brace depth
                brace_count = 1
                pos = start_pos
                while pos < len(content) and brace_count > 0:
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                if brace_count == 0:
                    commands = content[start_pos:pos-1].strip()
                    self.register_alias(name, commands)
            
            # Parse functions: function name(param1, param2) { commands }
            # Need to handle nested braces properly
            function_starts = []
            for match in re.finditer(r'function\s+(\w+)\s*\(([^)]*)\)\s*{', content, re.IGNORECASE):
                func_name = match.group(1)
                params_str = match.group(2).strip()
                # Parse parameters (comma-separated)
                params = [p.strip() for p in params_str.split(',')] if params_str else []
                function_starts.append((func_name, params, match.end()))
            
            for func_name, params, start_pos in function_starts:
                # Find the matching closing brace by counting brace depth
                brace_count = 1
                pos = start_pos
                while pos < len(content) and brace_count > 0:
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                if brace_count == 0:
                    commands = content[start_pos:pos-1].strip()
                    self.register_function(func_name, params, commands)
            
            return True, "Script parsed successfully"
            
        except Exception as e:
            return False, f"Parse error: {e}"
    
    # ==================== Registration ====================
    
    def register_event(self, event_type: str, match_pattern: str, target: str, commands: str):
        """Register an event handler"""
        event = ScriptEvent(event_type, match_pattern, target, commands)
        self.events.append(event)
    
    def register_alias(self, name: str, commands: str):
        """Register an alias (custom command)"""
        alias = ScriptAlias(name, commands)
        self.aliases[alias.name] = alias
    
    def register_function(self, name: str, params: List[str], commands: str):
        """Register a user-defined function"""
        func = ScriptFunction(name, params, commands)
        self.functions[func.name] = func
    
    def unregister_event(self, index: int) -> bool:
        """Remove an event by index"""
        if 0 <= index < len(self.events):
            del self.events[index]
            return True
        return False
    
    def unregister_alias(self, name: str) -> bool:
        """Remove an alias by name"""
        name = name.lower().lstrip('/')
        if name in self.aliases:
            del self.aliases[name]
            return True
        return False
    
    # ==================== Event Triggering ====================
    
    def trigger_event(self, event_type: str, nick: str, target: str, text: str, 
                      server: str, extra: Dict[str, str] = None):
        """Trigger all matching event handlers"""
        context = {
            'nick': nick,
            'chan': target if target.startswith('#') else '',
            'target': target,
            'text': text,
            'server': server,
            'me': self._get_my_nick(server),
        }
        
        # Add word tokens
        words = text.split()
        for i, word in enumerate(words, 1):
            context[str(i)] = word
        
        # Add $1- (all words from 1)
        if words:
            context['1-'] = text
            for i in range(1, len(words) + 1):
                context[f'{i}-'] = ' '.join(words[i-1:])
        
        # Add extra context
        if extra:
            context.update(extra)
        
        # Find and execute matching events
        for event in self.events:
            if event.enabled and event.event_type == event_type.upper():
                if event.matches(text, target):
                    self.execute_commands(event.commands, context, server, target)
    
    def check_alias(self, command: str, server: str, target: str) -> bool:
        """Check if input matches an alias and execute it"""
        if not command.startswith('/'):
            return False
        
        parts = command.split(None, 1)
        cmd_name = parts[0][1:].lower()  # Remove / and lowercase
        args = parts[1] if len(parts) > 1 else ''
        
        if cmd_name in self.aliases:
            alias = self.aliases[cmd_name]
            if alias.enabled:
                # Build context
                context = {
                    'nick': self._get_my_nick(server),
                    'chan': target if target.startswith('#') else '',
                    'target': target,
                    'text': args,
                    'server': server,
                    'me': self._get_my_nick(server),
                }
                
                # Add word tokens
                words = args.split()
                for i, word in enumerate(words, 1):
                    context[str(i)] = word
                if words:
                    context['1-'] = args
                    for i in range(1, len(words) + 1):
                        context[f'{i}-'] = ' '.join(words[i-1:])
                
                self.execute_commands(alias.commands, context, server, target)
                return True
        
        return False
    
    # ==================== Command Execution ====================
    
    def execute_commands(self, commands: str, context: Dict[str, str], 
                         server: str, target: str):
        """Execute a block of script commands"""
        self.halt_execution = False
        self.return_value = None
        
        # Split into individual commands
        lines = self._split_commands(commands)
        
        for line in lines:
            if self.halt_execution:
                break
            
            line = line.strip()
            if not line:
                continue
            
            # For control structures (if/while/for), don't substitute the entire block yet
            # Let the handlers process them so variables are substituted at execution time
            is_control_structure = (line.startswith('if ') or line.startswith('if(') or
                                   line.startswith('while ') or line.startswith('while(') or
                                   line.startswith('for ') or line.startswith('for('))
            
            if not is_control_structure:
                line = self._substitute_vars(line, context)
            
            # Execute the command
            self._execute_single_command(line, context, server, target)
    
    def _split_commands(self, commands: str) -> List[str]:
        """Split command block into individual commands, handling nested braces"""
        result = []
        current = ""
        brace_depth = 0
        lines = commands.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Count braces in this line
            for char in line:
                if char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
            
            current += line
            
            # If we're at depth 0 after this line, check if next line is 'else'
            if brace_depth == 0:
                # Peek at next line to see if it's an else block
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('else'):
                    # Keep going, don't split yet
                    current += '\n'
                else:
                    # Split here
                    if current.strip():
                        result.append(current.strip())
                    current = ""
            else:
                current += '\n'
            
            i += 1
        
        if current.strip():
            result.append(current.strip())
        
        return result
    
    def _execute_single_command(self, line: str, context: Dict[str, str],
                                server: str, target: str):
        """Execute a single command line"""
        try:
            # Handle control structures
            if line.startswith('if ') or line.startswith('if('):
                self._handle_if(line, context, server, target)
                return
            
            if line.startswith('while ') or line.startswith('while('):
                self._handle_while(line, context, server, target)
                return
            
            if line.startswith('for ') or line.startswith('for('):
                self._handle_for(line, context, server, target)
                return
            
            # Parse command and arguments
            parts = line.split(None, 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ''
            
            # Execute built-in commands
            if cmd == 'msg':
                self._cmd_msg(args, server, context)
            elif cmd == 'notice':
                self._cmd_notice(args, server, context)
            elif cmd == 'me':
                self._cmd_me(args, server)
            elif cmd == 'join':
                self._cmd_join(args, server)
            elif cmd == 'part':
                self._cmd_part(args, server)
            elif cmd == 'quit':
                self._cmd_quit(args, server)
            elif cmd == 'nick':
                self._cmd_nick(args, server)
            elif cmd == 'kick':
                self._cmd_kick(args, server)
            elif cmd == 'ban':
                self._cmd_ban(args, server)
            elif cmd == 'mode':
                self._cmd_mode(args, server)
            elif cmd == 'echo':
                self._cmd_echo(args)
            elif cmd == 'timer':
                self._cmd_timer(args, context, server, target)
            elif cmd == 'halt':
                self.halt_execution = True
            elif cmd == 'return':
                # Substitute variables and functions in the return value
                if args:
                    self.return_value = self._substitute_vars(args, context)
                else:
                    self.return_value = ''
                self.halt_execution = True
            elif cmd == 'sleep':
                self._cmd_sleep(args)
            elif cmd == 'set':
                self._cmd_set(args, context)
            elif cmd == 'unset':
                self._cmd_unset(args)
            elif cmd == 'raw':
                self._cmd_raw(args, server)
            elif cmd == 'setlevel':
                self._cmd_setlevel(args, context)
            elif cmd == 'remlevel':
                self._cmd_remlevel(args)
            elif cmd == 'getlevel':
                self._cmd_getlevel(args)
            elif cmd == 'write':
                self._cmd_write(args, context)
            elif cmd == 'read':
                self._cmd_read(args)
            elif cmd == 'remove':
                self._cmd_remove(args)
            elif cmd == 'listadd':
                self._cmd_listadd(args, context)
            elif cmd == 'listdel':
                self._cmd_listdel(args, context)
            elif cmd == 'listclear':
                self._cmd_listclear(args)
            elif cmd == 'listinsert':
                self._cmd_listinsert(args, context)
            else:
                # Unknown command - might be a /command
                if cmd.startswith('/'):
                    self.irc_client.handle_command(line, target)
                    
        except Exception as e:
            self._log_error(f"Script error executing '{line}': {e}")
    
    # ==================== Built-in Commands ====================
    
    def _cmd_msg(self, args: str, server: str, context: Dict[str, str] = None):
        """Send a message"""
        parts = args.split(None, 1)
        if len(parts) >= 2:
            target, message = parts
            # Substitute variables and identifiers in the message
            if context:
                message = self._substitute_vars(message, context)
            # Also substitute in target (for $chan, etc.)
            if context:
                target = self._substitute_vars(target, context)
            self.irc_client.send_command(f"PRIVMSG {target} :{message}", server)
    
    def _cmd_notice(self, args: str, server: str, context: Dict[str, str] = None):
        """Send a notice"""
        parts = args.split(None, 1)
        if len(parts) >= 2:
            target, message = parts
            # Substitute variables and identifiers in the message
            if context:
                message = self._substitute_vars(message, context)
                target = self._substitute_vars(target, context)
            self.irc_client.send_command(f"NOTICE {target} :{message}", server)
    
    def _cmd_me(self, args: str, server: str):
        """Send an action"""
        parts = args.split(None, 1)
        if len(parts) >= 2:
            target, action = parts
            self.irc_client.send_command(f"PRIVMSG {target} :\x01ACTION {action}\x01", server)
    
    def _cmd_join(self, args: str, server: str):
        """Join a channel"""
        parts = args.split()
        channel = parts[0] if parts else ''
        key = parts[1] if len(parts) > 1 else ''
        if channel:
            cmd = f"JOIN {channel}"
            if key:
                cmd += f" {key}"
            self.irc_client.send_command(cmd, server)
    
    def _cmd_part(self, args: str, server: str):
        """Leave a channel"""
        parts = args.split(None, 1)
        channel = parts[0] if parts else ''
        message = parts[1] if len(parts) > 1 else ''
        if channel:
            cmd = f"PART {channel}"
            if message:
                cmd += f" :{message}"
            self.irc_client.send_command(cmd, server)
    
    def _cmd_quit(self, args: str, server: str):
        """Quit from server"""
        cmd = "QUIT"
        if args:
            cmd += f" :{args}"
        self.irc_client.send_command(cmd, server)
    
    def _cmd_nick(self, args: str, server: str):
        """Change nickname"""
        if args:
            self.irc_client.send_command(f"NICK {args.split()[0]}", server)
    
    def _cmd_kick(self, args: str, server: str):
        """Kick a user"""
        parts = args.split(None, 2)
        if len(parts) >= 2:
            channel, nick = parts[0], parts[1]
            reason = parts[2] if len(parts) > 2 else 'Kicked'
            self.irc_client.send_command(f"KICK {channel} {nick} :{reason}", server)
    
    def _cmd_ban(self, args: str, server: str):
        """Ban a user"""
        parts = args.split(None, 1)
        if len(parts) >= 2:
            channel, mask = parts
            self.irc_client.send_command(f"MODE {channel} +b {mask}", server)
    
    def _cmd_mode(self, args: str, server: str):
        """Set modes"""
        if args:
            self.irc_client.send_command(f"MODE {args}", server)
    
    def _cmd_echo(self, args: str):
        """Display message locally"""
        self.irc_client.add_status_message(f"[Script] {args}")
    
    def _cmd_raw(self, args: str, server: str):
        """Send raw IRC command"""
        if args:
            self.irc_client.send_command(args, server)
    
    def _cmd_set(self, args: str, context: Dict[str, str]):
        """Set a variable"""
        match = re.match(r'(%+)(\w+)\s*=\s*(.*)', args)
        if match:
            prefix, name, value = match.groups()
            # Fully substitute the value including all functions and variables
            value = self._substitute_vars(value, context)
            if prefix == '%%':
                self.global_vars[name] = value
                self._save_global_vars()
            else:
                self.local_vars[name] = value
    
    def _cmd_unset(self, args: str):
        """Unset a variable"""
        match = re.match(r'(%+)(\w+)', args)
        if match:
            prefix, name = match.groups()
            if prefix == '%%':
                self.global_vars.pop(name, None)
                self._save_global_vars()
            else:
                self.local_vars.pop(name, None)
    
    def _cmd_setlevel(self, args: str, context: Dict[str, str]):
        """Set a user's level"""
        parts = args.split()
        if len(parts) >= 2:
            nickname = parts[0]
            try:
                level = int(parts[1])
                self.user_levels[nickname] = level
                self._save_user_levels()
                self._log_error(f"Set level for {nickname} to {level}")
            except ValueError:
                self._log_error(f"Invalid level value: {parts[1]}")
        else:
            self._log_error("Usage: setlevel <nickname> <level>")
    
    def _cmd_remlevel(self, args: str):
        """Remove a user's level"""
        nickname = args.strip()
        if nickname in self.user_levels:
            del self.user_levels[nickname]
            self._save_user_levels()
            self._log_error(f"Removed level for {nickname}")
        else:
            self._log_error(f"No level set for {nickname}")
    
    def _cmd_getlevel(self, args: str):
        """Get a user's level"""
        nickname = args.strip()
        level = self.user_levels.get(nickname, 0)
        self._log_error(f"{nickname} has level: {level}")
    
    def _cmd_write(self, args: str, context: Dict[str, str]):
        """Write text to file"""
        parts = args.split(None, 1)
        if len(parts) >= 2:
            filename, text = parts
            # Substitute variables in text
            text = self._substitute_vars(text, context)
            filepath = os.path.join(self.scripts_dir, filename)
            try:
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(text + '\n')
            except Exception as e:
                self._log_error(f"Error writing to {filename}: {e}")
        else:
            self._log_error("Usage: write <filename> <text>")
    
    def _cmd_read(self, args: str):
        """Read from file and display"""
        parts = args.split()
        if not parts:
            self._log_error("Usage: read <filename> [line_number]")
            return
        
        filename = parts[0]
        line_num = int(parts[1]) if len(parts) > 1 else None
        filepath = os.path.join(self.scripts_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                self._log_error(f"File not found: {filename}")
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n') for line in f.readlines()]
            
            if not lines:
                self._log_error(f"File is empty: {filename}")
                return
            
            if line_num is not None:
                if 1 <= line_num <= len(lines):
                    self._log_error(lines[line_num - 1])
                else:
                    self._log_error(f"Line {line_num} out of range (1-{len(lines)})")
            else:
                # Read random line
                import random
                self._log_error(random.choice(lines))
        except Exception as e:
            self._log_error(f"Error reading {filename}: {e}")
    
    def _cmd_remove(self, args: str):
        """Remove/delete a file"""
        filename = args.strip()
        if not filename:
            self._log_error("Usage: remove <filename>")
            return
        
        filepath = os.path.join(self.scripts_dir, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                self._log_error(f"Removed file: {filename}")
            else:
                self._log_error(f"File not found: {filename}")
        except Exception as e:
            self._log_error(f"Error removing {filename}: {e}")
    
    # ==================== List Commands ====================
    
    def _cmd_listadd(self, args: str, context: Dict[str, str]):
        """Add an item to a list
        Usage: listadd <@listname> <value>
        Examples: 
            listadd @mylist Hello
            listadd @@globallist $nick
        """
        match = re.match(r'(@+)(\w+)\s+(.*)', args)
        if not match:
            self._log_error("Usage: listadd <@listname> <value>")
            return
        
        prefix, name, value = match.groups()
        value = self._substitute_vars(value, context)
        
        # Determine if global or local list
        is_global = len(prefix) == 2  # @@ for global
        
        if is_global:
            if name not in self.global_lists:
                self.global_lists[name] = []
            self.global_lists[name].append(value)
        else:
            if name not in self.local_lists:
                self.local_lists[name] = []
            self.local_lists[name].append(value)
    
    def _cmd_listdel(self, args: str, context: Dict[str, str]):
        """Remove an item from a list by index or value
        Usage: listdel <@listname> <index|value>
        Examples:
            listdel @mylist 0     (remove first item)
            listdel @mylist Hello (remove item with value "Hello")
        """
        match = re.match(r'(@+)(\w+)\s+(.*)', args)
        if not match:
            self._log_error("Usage: listdel <@listname> <index|value>")
            return
        
        prefix, name, item = match.groups()
        item = self._substitute_vars(item, context).strip()
        
        is_global = len(prefix) == 2
        target_lists = self.global_lists if is_global else self.local_lists
        
        if name not in target_lists:
            return
        
        lst = target_lists[name]
        
        # Try to remove by index first
        try:
            index = int(item)
            if 0 <= index < len(lst):
                lst.pop(index)
        except ValueError:
            # Not an integer, try to remove by value
            try:
                lst.remove(item)
            except ValueError:
                pass  # Item not in list, silently ignore
    
    def _cmd_listclear(self, args: str):
        """Clear all items from a list (creates empty list if it doesn't exist)
        Usage: listclear <@listname>
        Examples:
            listclear @mylist
            listclear @@globallist
        """
        match = re.match(r'(@+)(\w+)', args.strip())
        if not match:
            self._log_error("Usage: listclear <@listname>")
            return
        
        prefix, name = match.groups()
        is_global = len(prefix) == 2
        
        if is_global:
            # Create empty list if it doesn't exist, or clear if it does
            self.global_lists[name] = []
        else:
            # Create empty list if it doesn't exist, or clear if it does
            self.local_lists[name] = []
    
    def _cmd_listinsert(self, args: str, context: Dict[str, str]):
        """Insert an item at a specific index in a list
        Usage: listinsert <@listname> <index> <value>
        Examples:
            listinsert @mylist 0 First
            listinsert @mylist 2 $nick
        """
        match = re.match(r'(@+)(\w+)\s+(\d+)\s+(.*)', args)
        if not match:
            self._log_error("Usage: listinsert <@listname> <index> <value>")
            return
        
        prefix, name, index_str, value = match.groups()
        index = int(index_str)
        value = self._substitute_vars(value, context)
        
        is_global = len(prefix) == 2
        target_lists = self.global_lists if is_global else self.local_lists
        
        if name not in target_lists:
            target_lists[name] = []
        
        lst = target_lists[name]
        # Clamp index to valid range
        index = max(0, min(index, len(lst)))
        lst.insert(index, value)
    
    def _cmd_timer(self, args: str, context: Dict[str, str], server: str, target: str):
        """Create or manage a timer"""
        # timer <name> off - stop timer
        match = re.match(r'(\w+)\s+off', args)
        if match:
            name = match.group(1)
            if name in self.timers:
                timer = self.timers[name]
                if timer.timer_id:
                    self.irc_client.window.after_cancel(timer.timer_id)
                del self.timers[name]
            return
        
        # timer <name> <interval> <reps> { commands }
        match = re.match(r'(\w+)\s+(\d+)\s+(\d+)\s*{\s*([\s\S]*?)\s*}', args)
        if match:
            name, interval, reps, commands = match.groups()
            interval = int(interval)
            reps = int(reps)
            
            # Stop existing timer with same name
            if name in self.timers and self.timers[name].timer_id:
                self.irc_client.window.after_cancel(self.timers[name].timer_id)
            
            timer = ScriptTimer(name, interval, reps, commands)
            self.timers[name] = timer
            
            # Start the timer
            self._start_timer(timer, context.copy(), server, target)
    
    def _start_timer(self, timer: ScriptTimer, context: Dict[str, str], 
                     server: str, target: str):
        """Start a timer"""
        def timer_callback():
            if timer.name not in self.timers:
                return
            
            self.execute_commands(timer.commands, context, server, target)
            timer.current_rep += 1
            
            # Schedule next execution
            if timer.repetitions == 0 or timer.current_rep < timer.repetitions:
                timer.timer_id = self.irc_client.window.after(
                    timer.interval, timer_callback
                )
            else:
                del self.timers[timer.name]
        
        timer.timer_id = self.irc_client.window.after(timer.interval, timer_callback)
    
    def _cmd_sleep(self, args: str):
        """Sleep for a specified number of seconds while keeping GUI responsive
        Usage: sleep <seconds>
        Example: sleep 2
        """
        import time
        try:
            seconds = float(args.strip())
            end_time = time.time() + seconds
            
            # Block for the specified time, updating GUI periodically
            # This allows messages to be sent and GUI to stay responsive
            while time.time() < end_time:
                # Process all pending GUI events
                self.irc_client.window.update()
                self.irc_client.window.update_idletasks()
                # Small sleep to avoid 100% CPU usage
                remaining = end_time - time.time()
                if remaining > 0.1:
                    time.sleep(0.1)
                else:
                    if remaining > 0:
                        time.sleep(remaining)
                    break
                
        except ValueError:
            self._log_error(f"Sleep error: invalid duration '{args}'")
    
    # ==================== Control Structures ====================
    
    def _handle_if(self, line: str, context: Dict[str, str], server: str, target: str):
        """Handle if/else statements"""
        # Parse: if (condition) { commands } else { commands }
        # Need to manually find matching braces due to nested structures
        # Note: Don't substitute vars in the line yet - condition and commands will be handled separately
        match = re.match(r'if\s*\(([^)]+)\)\s*{', line)
        if not match:
            return
        
        condition = match.group(1)
        start_pos = match.end()
        
        # Find matching closing brace by counting brace depth
        brace_count = 1
        pos = start_pos
        while pos < len(line) and brace_count > 0:
            if line[pos] == '{':
                brace_count += 1
            elif line[pos] == '}':
                brace_count -= 1
            pos += 1
        
        if_commands = line[start_pos:pos-1].strip()
        
        # Check for else clause
        else_commands = None
        remaining = line[pos:].strip()
        if remaining.startswith('else'):
            else_match = re.match(r'else\s*{', remaining)
            if else_match:
                else_start = else_match.end()
                brace_count = 1
                pos = else_start
                while pos < len(remaining) and brace_count > 0:
                    if remaining[pos] == '{':
                        brace_count += 1
                    elif remaining[pos] == '}':
                        brace_count -= 1
                    pos += 1
                else_commands = remaining[else_start:pos-1].strip()
        
        # Execute appropriate branch
        if self._evaluate_condition(condition, context):
            self.execute_commands(if_commands, context, server, target)
        elif else_commands:
            self.execute_commands(else_commands, context, server, target)
    
    def _handle_while(self, line: str, context: Dict[str, str], server: str, target: str):
        """Handle while loops"""
        # Parse: while (condition) { commands }
        # Need to manually find matching braces due to nested structures
        match = re.match(r'while\s*\(([^)]+)\)\s*{', line)
        if not match:
            return
        
        condition = match.group(1)
        start_pos = match.end()
        
        # Find matching closing brace by counting brace depth
        brace_count = 1
        pos = start_pos
        while pos < len(line) and brace_count > 0:
            if line[pos] == '{':
                brace_count += 1
            elif line[pos] == '}':
                brace_count -= 1
            pos += 1
        
        commands = line[start_pos:pos-1].strip()
        
        # Safety limit to prevent infinite loops
        max_iterations = 1000
        iterations = 0
        
        while self._evaluate_condition(condition, context) and iterations < max_iterations:
            if self.halt_execution:
                break
            self.execute_commands(commands, context, server, target)
            iterations += 1
    
    def _handle_for(self, line: str, context: Dict[str, str], server: str, target: str):
        """Handle for loops to iterate over lists
        Syntax: for (%var in @listname) { commands }
                for (%var in @@globallist) { commands }
        """
        # First, substitute context variables like $text, $nick, but NOT the loop variable
        # The loop variable will be substituted during each iteration
        line_with_context = self._substitute_vars(line, context)
        
        match = re.match(r'for\s*\(\s*(%\w+)\s+in\s+(@+)(\w+)\s*\)\s*{\s*([\s\S]*?)\s*}', line_with_context)
        if match:
            var_name, prefix, list_name, commands = match.groups()
            var_name = var_name[1:]  # Remove the % prefix
            
            # Get the list
            is_global = len(prefix) == 2
            target_lists = self.global_lists if is_global else self.local_lists
            
            if list_name not in target_lists:
                return
            
            lst = target_lists[list_name]
            
            # Safety limit
            max_iterations = min(len(lst), 10000)
            
            # Iterate over the list
            for i, item in enumerate(lst):
                if i >= max_iterations or self.halt_execution:
                    break
                
                # Set the loop variable in local vars
                old_value = self.local_vars.get(var_name)
                self.local_vars[var_name] = item
                
                # Execute commands - loop variable will be substituted from self.local_vars
                self.execute_commands(commands, context, server, target)
                
                # Restore old value if it existed, otherwise remove
                if old_value is not None:
                    self.local_vars[var_name] = old_value
                elif var_name in self.local_vars:
                    del self.local_vars[var_name]
    
    def _evaluate_condition(self, condition: str, context: Dict[str, str]) -> bool:
        """Evaluate a condition expression"""
        condition = self._substitute_vars(condition, context).strip()
        
        # Handle operators
        operators = ['==', '!=', '>=', '<=', '>', '<', ' isin ', ' !isin ', ' iswm ']
        
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    if op == '==':
                        return left == right
                    elif op == '!=':
                        return left != right
                    elif op == '>=':
                        try:
                            return float(left) >= float(right)
                        except:
                            return left >= right
                    elif op == '<=':
                        try:
                            return float(left) <= float(right)
                        except:
                            return left <= right
                    elif op == '>':
                        try:
                            return float(left) > float(right)
                        except:
                            return left > right
                    elif op == '<':
                        try:
                            return float(left) < float(right)
                        except:
                            return left < right
                    elif op == ' isin ':
                        return left.lower() in right.lower()
                    elif op == ' !isin ':
                        return left.lower() not in right.lower()
                    elif op == ' iswm ':
                        return self._wildcard_match(left, right)
        
        # If no operator, check if truthy
        return bool(condition) and condition.lower() not in ('false', '0', '')
    
    def _wildcard_match(self, text: str, pattern: str) -> bool:
        """Wildcard matching for iswm operator"""
        pattern = pattern.replace('*', '.*').replace('?', '.')
        try:
            return bool(re.match(f'^{pattern}$', text, re.IGNORECASE))
        except:
            return False
    
    # ==================== Variable Substitution ====================
    
    def _substitute_vars(self, text: str, context: Dict[str, str], skip_functions: bool = False) -> str:
        """Substitute variables and identifiers in text
        
        Args:
            text: The text to substitute
            context: Context dictionary with identifiers
            skip_functions: If True, only substitute variables, not functions (used internally)
        """
        # Substitute variables FIRST so they're available inside functions like $calc()
        # BUT: Don't substitute variable names in 'set %var = value' patterns
        
        # Check if this is a set command - if so, only substitute the value part
        set_match = re.match(r'^set\s+(%+\w+)\s*=\s*(.*)', text, re.IGNORECASE)
        if set_match:
            var_part = set_match.group(1)  # The %varname part
            value_part = set_match.group(2)  # The value part
            
            # Fully substitute the value part including all variables, identifiers, and functions
            # This is a recursive call but we need to process the value part completely
            value_part = self._substitute_vars(value_part, context)
            
            # Return the fully substituted set command
            return f'set {var_part} = {value_part}'
        else:
            # Not a set command - substitute variables normally
            # Handle global variables: %%varname
            for name, value in self.global_vars.items():
                text = text.replace(f'%%{name}', value)
            
            # Handle local variables: %varname
            for name, value in self.local_vars.items():
                text = text.replace(f'%{name}', value)
        
        # Handle function-style identifiers after variables are substituted
        # Skip if we're in a nested call (skip_functions=True)
        if not skip_functions:
            text = re.sub(r'\$rand\((\d+)\)', lambda m: str(random.randint(0, int(m.group(1))-1)), text)
            text = re.sub(r'\$len\(([^)]*)\)', lambda m: str(len(self._substitute_vars(m.group(1), context, skip_functions=True))), text)
            text = re.sub(r'\$upper\(([^)]*)\)', lambda m: self._substitute_vars(m.group(1), context, skip_functions=True).upper(), text)
            text = re.sub(r'\$lower\(([^)]*)\)', lambda m: self._substitute_vars(m.group(1), context, skip_functions=True).lower(), text)
            text = re.sub(r'\$left\(([^,]*),(\d+)\)', lambda m: self._substitute_vars(m.group(1), context, skip_functions=True)[:int(m.group(2))], text)
            text = re.sub(r'\$right\(([^,]*),(\d+)\)', lambda m: self._substitute_vars(m.group(1), context, skip_functions=True)[-int(m.group(2)):], text)
            text = re.sub(r'\$mid\(([^,]*),(\d+),(\d+)\)', lambda m: self._substitute_vars(m.group(1), context, skip_functions=True)[int(m.group(2)):int(m.group(2))+int(m.group(3))], text)
            
            # User level functions
            text = re.sub(r'\$level\(([^)]+)\)', lambda m: str(self.user_levels.get(self._substitute_vars(m.group(1), context, skip_functions=True), 0)), text)
            text = re.sub(r'\$islevel\(([^,]+),(\d+)\)', lambda m: str(self.user_levels.get(self._substitute_vars(m.group(1), context, skip_functions=True), 0) >= int(m.group(2))), text)
            
            # Hostmask lookup function: $address(nick)
            def sub_address(match):
                param = match.group(1).strip()
                param = self._substitute_vars(param, context, skip_functions=True)
                return self._func_address(param, context)
            text = re.sub(r'\$address\(([^)]+)\)', sub_address, text)
            
            # WHOIS lookup function: $whois(nick,field)
            def sub_whois(match):
                params = match.group(1).strip()
                # Parse parameters (nick, field)
                if ',' in params:
                    parts = params.split(',', 1)
                    nick_param = parts[0].strip()
                    field_param = parts[1].strip()
                else:
                    nick_param = params
                    field_param = ''
                
                # Substitute variables in parameters using recursive substitution
                # This ensures %target and other variables are properly resolved
                nick_param = self._substitute_vars(nick_param, context, skip_functions=True)
                field_param = self._substitute_vars(field_param, context, skip_functions=True) if field_param else ''
                
                result = self._func_whois(nick_param, field_param, context)
                # Always return the result, even if empty - this ensures substitution happens
                return result
            text = re.sub(r'\$whois\(([^)]+)\)', sub_whois, text)
            
            # IP extraction function
            text = re.sub(r'\$ip\(([^)]+)\)', lambda m: self._extract_ip(self._substitute_vars(m.group(1), context, skip_functions=True)), text)
        
        # File I/O functions
        text = re.sub(r'\$read\(([^,)]+)\)', lambda m: self._func_read(m.group(1).strip(), None, context), text)
        text = re.sub(r'\$read\(([^,)]+),\s*(\d+)\)', lambda m: self._func_read(m.group(1).strip(), int(m.group(2)), context), text)
        text = re.sub(r'\$exists\(([^)]+)\)', lambda m: str(self._func_exists(m.group(1).strip(), context)), text)
        text = re.sub(r'\$lines\(([^)]+)\)', lambda m: str(self._func_lines(m.group(1).strip(), context)), text)
        
        # List functions
        # $list(@listname,N) - Get item at index N
        text = re.sub(r'\$list\((@+)(\w+),\s*(\d+)\)', lambda m: self._func_list_get(m.group(1), m.group(2), int(m.group(3))), text)
        # $list(@listname,count) - Get count of items
        text = re.sub(r'\$list\((@+)(\w+),\s*count\)', lambda m: str(self._func_list_count(m.group(1), m.group(2))), text, flags=re.IGNORECASE)
        # $list(@listname,find,value) - Find index of value
        text = re.sub(r'\$list\((@+)(\w+),\s*find,\s*([^)]+)\)', lambda m: str(self._func_list_find(m.group(1), m.group(2), self._substitute_vars(m.group(3), context))), text, flags=re.IGNORECASE)
        # $list(@listname,exists,value) - Check if value exists
        text = re.sub(r'\$list\((@+)(\w+),\s*exists,\s*([^)]+)\)', lambda m: str(self._func_list_exists(m.group(1), m.group(2), self._substitute_vars(m.group(3), context))), text, flags=re.IGNORECASE)
        
        # String tokenization functions
        text = re.sub(r'\$gettok\(([^,]+),\s*(\d+),\s*(\d+)\)', lambda m: self._func_gettok(self._substitute_vars(m.group(1), context), int(m.group(2)), int(m.group(3))), text)
        text = re.sub(r'\$numtok\(([^,]+),\s*(\d+)\)', lambda m: str(self._func_numtok(self._substitute_vars(m.group(1), context), int(m.group(2)))), text)
        text = re.sub(r'\$findtok\(([^,]+),\s*([^,]+),\s*(\d+),\s*(\d+)\)', lambda m: str(self._func_findtok(self._substitute_vars(m.group(1), context), self._substitute_vars(m.group(2), context), int(m.group(3)), int(m.group(4)))), text)
        text = re.sub(r'\$addtok\(([^,]+),\s*([^,]+),\s*(\d+)\)', lambda m: self._func_addtok(self._substitute_vars(m.group(1), context), self._substitute_vars(m.group(2), context), int(m.group(3))), text)
        text = re.sub(r'\$remtok\(([^,]+),\s*([^,]+),\s*(\d+)\)', lambda m: self._func_remtok(self._substitute_vars(m.group(1), context), self._substitute_vars(m.group(2), context), int(m.group(3))), text)
        
        # Math operations
        text = re.sub(r'\$calc\(([^)]+)\)', lambda m: str(self._func_calc(self._substitute_vars(m.group(1), context))), text)
        text = re.sub(r'\$round\(([^,]+),\s*(\d+)\)', lambda m: str(self._func_round(self._substitute_vars(m.group(1), context), int(m.group(2)))), text)
        text = re.sub(r'\$abs\(([^)]+)\)', lambda m: str(self._func_abs(self._substitute_vars(m.group(1), context))), text)
        text = re.sub(r'\$sqrt\(([^)]+)\)', lambda m: str(self._func_sqrt(self._substitute_vars(m.group(1), context))), text)
        text = re.sub(r'\$floor\(([^)]+)\)', lambda m: str(self._func_floor(self._substitute_vars(m.group(1), context))), text)
        text = re.sub(r'\$ceil\(([^)]+)\)', lambda m: str(self._func_ceil(self._substitute_vars(m.group(1), context))), text)
        
        # Additional string functions
        text = re.sub(r'\$pos\(([^,]+),\s*([^)]+)\)', lambda m: str(self._func_pos(self._substitute_vars(m.group(1), context), self._substitute_vars(m.group(2), context))), text)
        text = re.sub(r'\$replace\(([^,]+),\s*([^,]+),\s*([^)]+)\)', lambda m: self._func_replace(self._substitute_vars(m.group(1), context), self._substitute_vars(m.group(2), context), self._substitute_vars(m.group(3), context)), text)
        text = re.sub(r'\$remove\(([^,]+),\s*([^)]+)\)', lambda m: self._func_remove(self._substitute_vars(m.group(1), context), self._substitute_vars(m.group(2), context)), text)
        text = re.sub(r'\$str\(([^,]+),\s*(\d+)\)', lambda m: self._func_str(self._substitute_vars(m.group(1), context), int(m.group(2))), text)
        text = re.sub(r'\$chr\((\d+)\)', lambda m: chr(int(m.group(1))), text)
        text = re.sub(r'\$asc\((.)\)', lambda m: str(ord(m.group(1))), text)
        text = re.sub(r'\$strip\(([^)]+)\)', lambda m: self._func_strip(self._substitute_vars(m.group(1), context)), text)
        text = re.sub(r'\$reptok\(([^,]+),\s*([^,]+),\s*([^,]+),\s*(\d+)\)', lambda m: self._func_reptok(self._substitute_vars(m.group(1), context), self._substitute_vars(m.group(2), context), self._substitute_vars(m.group(3), context), int(m.group(4))), text)
        
        # User-defined functions: $functionname(param1, param2, ...)
        # This must come after built-in functions to avoid conflicts
        # We need to match any $name(...) that isn't a built-in function
        if not skip_functions:
            # List of built-in function names to exclude
            builtin_func_names = {
                'len', 'upper', 'lower', 'left', 'right', 'mid', 'pos', 'replace', 'remove', 
                'str', 'chr', 'asc', 'strip', 'reptok', 'calc', 'round', 'abs', 'sqrt', 
                'floor', 'ceil', 'read', 'exists', 'lines', 'list', 'gettok', 'numtok', 
                'findtok', 'addtok', 'remtok', 'rand', 'level', 'islevel', 'ip', 'address', 
                'whois', 'nick', 'chan', 'me', 'server', 'target', 'text', 'time', 'date', 
                'version', 'user', 'host', 'address'
            }
            
            def sub_user_function(match):
                func_name = match.group(1).strip().lower()
                params_str = match.group(2).strip() if match.group(2) else ''
                
                # Skip if it's a built-in function
                if func_name in builtin_func_names:
                    return match.group(0)  # Return original, let built-in handlers process it
                
                # Check if it's a user-defined function
                if func_name not in self.functions:
                    # Not a user-defined function - return original to preserve it
                    # This might be a variable or something else
                    return match.group(0)
                
                # Parse parameters (comma-separated)
                # First, substitute any nested functions in the parameter string
                # This ensures inner functions are evaluated before outer ones
                params_str = self._substitute_vars(params_str, context, skip_functions=False)
                
                if params_str:
                    # Split by comma, but handle nested function calls and parentheses
                    params = []
                    current_param = ''
                    paren_depth = 0
                    for char in params_str:
                        if char == '(':
                            paren_depth += 1
                            current_param += char
                        elif char == ')':
                            paren_depth -= 1
                            current_param += char
                        elif char == ',' and paren_depth == 0:
                            params.append(current_param.strip())
                            current_param = ''
                        else:
                            current_param += char
                    if current_param.strip():
                        params.append(current_param.strip())
                else:
                    params = []
                
                # Parameters may still have variables that need substitution
                substituted_params = []
                for param in params:
                    # Do final substitution (variables, but functions should already be done)
                    substituted_params.append(self._substitute_vars(param, context, skip_functions=True))
                
                # Execute the function
                result = self._execute_function(func_name, substituted_params, context)
                return result
            
            # Match function calls: $name(params) or $name()
            # We need to handle nested parentheses correctly
            # Use a more sophisticated approach: find the innermost function calls first
            max_iterations = 10  # Prevent infinite loops
            iteration = 0
            while iteration < max_iterations:
                # Find all function calls with proper nested parenthesis handling
                # We'll match from innermost to outermost
                def find_innermost_function(match):
                    # This will be called for each potential match
                    # We need to verify it's actually a complete function call
                    return match.group(0)
                
                # Use a pattern that finds function calls, but we need to handle nesting
                # Strategy: find $name( and then find the matching )
                pattern = r'\$(\w+)\('
                matches = list(re.finditer(pattern, text))
                
                if not matches:
                    break  # No more function calls
                
                # Process from right to left (innermost first)
                matches.reverse()
                new_text = text
                for match in matches:
                    func_name = match.group(1).strip().lower()
                    start_pos = match.end()  # Position after $name(
                    
                    # Skip if it's a built-in function
                    if func_name in builtin_func_names:
                        continue
                    
                    # Skip if it's not a user-defined function
                    if func_name not in self.functions:
                        continue
                    
                    # Find the matching closing parenthesis
                    paren_depth = 1
                    pos = start_pos
                    while pos < len(new_text) and paren_depth > 0:
                        if new_text[pos] == '(':
                            paren_depth += 1
                        elif new_text[pos] == ')':
                            paren_depth -= 1
                        pos += 1
                    
                    if paren_depth == 0:
                        # Found complete function call
                        params_str = new_text[start_pos:pos-1].strip()
                        # Substitute nested functions in parameters first
                        params_str = self._substitute_vars(params_str, context, skip_functions=False)
                        
                        # Parse parameters
                        if params_str:
                            params = []
                            current_param = ''
                            param_paren_depth = 0
                            for char in params_str:
                                if char == '(':
                                    param_paren_depth += 1
                                    current_param += char
                                elif char == ')':
                                    param_paren_depth -= 1
                                    current_param += char
                                elif char == ',' and param_paren_depth == 0:
                                    params.append(current_param.strip())
                                    current_param = ''
                                else:
                                    current_param += char
                            if current_param.strip():
                                params.append(current_param.strip())
                        else:
                            params = []
                        
                        # Substitute variables in parameters
                        substituted_params = []
                        for param in params:
                            substituted_params.append(self._substitute_vars(param, context, skip_functions=True))
                        
                        # Execute the function
                        result = self._execute_function(func_name, substituted_params, context)
                        
                        # Replace the function call with the result
                        func_call = new_text[match.start():pos]
                        new_text = new_text[:match.start()] + result + new_text[pos:]
                        break  # Process one at a time, then restart
                
                if new_text == text:
                    break  # No more substitutions
                text = new_text
                iteration += 1
        
        # Handle context identifiers
        text = text.replace('$nick', context.get('nick', ''))
        text = text.replace('$chan', context.get('chan', ''))
        text = text.replace('$target', context.get('target', ''))
        text = text.replace('$text', context.get('text', ''))
        text = text.replace('$server', context.get('server', ''))
        text = text.replace('$me', context.get('me', ''))
        
        # Handle numbered tokens ($1, $2, $3, etc.) and ranges ($1-, $2-, etc.)
        # These are used in events and functions
        for i in range(1, 100):  # Support up to $99
            token_key = str(i)
            token_range_key = f'{i}-'
            if token_key in context:
                # Replace $N with the value
                text = text.replace(f'${i}', context.get(token_key, ''))
            if token_range_key in context:
                # Replace $N- with the range value
                text = text.replace(f'${i}-', context.get(token_range_key, ''))
        
        # Handle parameter names in function context (for user-defined functions)
        # These are mapped when the function is called, so we can substitute them here
        # But we need to be careful - only substitute if they're not part of a larger identifier
        # For now, we'll substitute parameter names that are in the context
        # This allows functions to use parameter names like 'a', 'b' directly
        # Only do this if we're in a function context (check if context has parameter names)
        # Parameter names are typically short and don't contain special characters
        for key, value in context.items():
            # Only substitute if it's a simple parameter name (not $1, $2, etc. which are already handled)
            # Also skip context identifiers like 'nick', 'chan', etc.
            if (key and not key.isdigit() and not key.endswith('-') and 
                key not in ['nick', 'chan', 'target', 'text', 'server', 'me', 'user', 'host', 'address'] and
                len(key) <= 20):  # Parameter names are typically short
                # Replace standalone parameter names (word boundaries)
                # This is a simple approach - replace 'a' with its value, but be careful with word boundaries
                # Only replace if it's not part of a variable or identifier (not preceded by $ or %)
                pattern = r'(?<![$%])\b' + re.escape(key) + r'\b'
                text = re.sub(pattern, value, text)
        
        # Hostmask identifiers (only if not in a function call - $address() is handled above)
        # Check that $address is not followed by ( to avoid replacing $address(nick) with context address
        import re as re_module
        # Replace $address only if it's not part of $address(...)
        text = re_module.sub(r'\$address(?!\()', context.get('address', ''), text)
        text = text.replace('$user', context.get('user', ''))
        text = text.replace('$host', context.get('host', ''))
        
        # IP extraction from hostmask
        host = context.get('host', '')
        ip_addr = self._extract_ip(host)
        text = text.replace('$ip', ip_addr)
        
        # Special identifier: $level (without args) = level of $nick
        if '$level' in text and '$level(' not in text:
            nick = context.get('nick', '')
            text = text.replace('$level', str(self.user_levels.get(nick, 0)))
        
        # Handle numbered tokens ($1, $2, $1-, etc.)
        # First handle $N- patterns (everything from N onwards)
        for i in range(20, 0, -1):  # Go backwards to handle $10- before $1-
            text = text.replace(f'${i}-', context.get(f'{i}-', ''))
        
        # Then handle simple $N patterns
        for i in range(20, 0, -1):
            text = text.replace(f'${i}', context.get(str(i), ''))
        
        # Handle built-in identifiers
        text = text.replace('$time', datetime.now().strftime('%H:%M:%S'))
        text = text.replace('$date', datetime.now().strftime('%Y-%m-%d'))
        text = text.replace('$version', getattr(self.irc_client, 'version', 'RootX'))
        text = text.replace('$crlf', '\r\n')
        text = text.replace('$cr', '\r')
        text = text.replace('$lf', '\n')
        text = text.replace('$tab', '\t')
        
        return text
    
    # ==================== Utility Methods ====================
    
    def _func_address(self, nick: str, context: Dict[str, str]) -> str:
        """Get hostmask for a specific nickname: $address(nick)"""
        if not nick:
            return ''
        
        # Strip any whitespace
        nick = nick.strip()
        
        server = context.get('server', '')
        if not server and self.irc_client:
            # Try to get server from current connection
            if hasattr(self.irc_client, 'current_server') and self.irc_client.current_server:
                server = self.irc_client.current_server
            elif hasattr(self.irc_client, 'connections') and self.irc_client.connections:
                # Use first available server
                server = list(self.irc_client.connections.keys())[0] if self.irc_client.connections else ''
        
        if server and self.irc_client:
            hostmask_key = f"{server}:{nick.lower()}"
            if hasattr(self.irc_client, 'user_hostmasks'):
                hostmask = self.irc_client.user_hostmasks.get(hostmask_key, '')
                # Only return the hostmask if we found it - don't fall back to context address
                return hostmask
        
        return ''
    
    def _func_whois(self, nick: str, field: str, context: Dict[str, str]) -> str:
        """Get WHOIS data for a specific nickname: $whois(nick,field)"""
        if not nick:
            return ''
        
        nick = nick.strip()
        field = field.strip() if field else ''
        
        if not self.irc_client or not hasattr(self.irc_client, 'whois_data'):
            return ''
        
        # Try to find WHOIS data by matching the nickname (case-insensitive)
        # The server part of the key might vary (e.g., "irc.libera.chat" vs "copper.libera.chat")
        matching_keys = []
        for key in self.irc_client.whois_data.keys():
            if key.lower().endswith(f":{nick.lower()}"):
                matching_keys.append(key)
        
        if not matching_keys:
            return ''
        
        # Use the first matching key (or prefer the one matching the context server if available)
        server = context.get('server', '')
        if not server and self.irc_client:
            if hasattr(self.irc_client, 'current_server') and self.irc_client.current_server:
                server = self.irc_client.current_server
            elif hasattr(self.irc_client, 'connections') and self.irc_client.connections:
                server = list(self.irc_client.connections.keys())[0] if self.irc_client.connections else ''
        
        # Prefer a key that matches the server from context/connections
        whois_key = None
        if server:
            for key in matching_keys:
                if key.startswith(f"{server}:"):
                    whois_key = key
                    break
        
        # If no server match, use the first matching key
        if not whois_key:
            whois_key = matching_keys[0]
        
        whois_info = self.irc_client.whois_data[whois_key]
        field_lower = field.lower() if field else ''
        
        # Map field names to data keys
        field_map = {
            'nick': 'nick',
            'username': 'username',
            'user': 'username',
            'hostname': 'hostname',
            'host': 'hostname',
            'realname': 'realname',
            'real': 'realname',
            'hostmask': 'hostmask',
            'server': 'irc_server',
            'irc_server': 'irc_server',
            'server_info': 'server_info',
            'idle': 'idle_seconds',
            'idle_seconds': 'idle_seconds',
            'signon': 'signon_time',
            'signon_time': 'signon_time',
            'channels': 'channels',
            'operator': 'is_operator',
            'is_operator': 'is_operator'
        }
        
        data_key = field_map.get(field_lower, field_lower)
        value = whois_info.get(data_key, '')
        if isinstance(value, bool):
            return str(value)
        # Return the value, even if empty (empty string means field not found/not available)
        return str(value) if value is not None else ''
    
    def _execute_function(self, func_name: str, params: List[str], context: Dict[str, str]) -> str:
        """Execute a user-defined function and return its result"""
        func_name = func_name.lower()
        
        if func_name not in self.functions:
            # Function not found - return empty string (don't modify the original text)
            # This allows the original $function(...) to remain if it's not a user function
            return ''  # Function not found, return empty string
        
        func = self.functions[func_name]
        if not func.enabled:
            return ''
        
        # Create a new context for the function with parameter values
        func_context = context.copy() if context else {}
        
        # Map parameters to $1, $2, $3, etc. in the function context
        for i, param_value in enumerate(params):
            func_context[str(i + 1)] = param_value
            func_context[f'{i + 1}-'] = ' '.join(params[i:]) if i < len(params) else ''
        
        # Also map named parameters if the function has them
        for i, param_name in enumerate(func.params):
            if i < len(params):
                # Store as both the parameter name and $N
                func_context[param_name] = params[i]
                func_context[str(i + 1)] = params[i]
        
        # Save current return value and halt state
        old_return_value = self.return_value
        old_halt_execution = self.halt_execution
        
        # Reset for function execution
        self.return_value = None
        self.halt_execution = False
        
        # Execute the function commands
        try:
            # Get server and target from context for command execution
            server = func_context.get('server', '')
            target = func_context.get('target', '')
            
            # Execute the function's commands
            self.execute_commands(func.commands, func_context, server, target)
            
            # Get the return value
            result = self.return_value if self.return_value is not None else ''
            
        except Exception as e:
            self._log_error(f"Error executing function {func_name}: {e}")
            result = ''
        finally:
            # Restore previous state
            self.return_value = old_return_value
            self.halt_execution = old_halt_execution
        
        # Return the result as a string
        return str(result) if result is not None else ''
    
    def _get_my_nick(self, server: str) -> str:
        """Get the current nickname for a server"""
        try:
            if server in self.irc_client.connections:
                return self.irc_client.connections[server].get('nickname', '')
        except:
            pass
        return ''
    
    def _extract_ip(self, hostname: str) -> str:
        """Extract IP address from hostname
        Handles various formats:
        - Direct IP: 73.244.70.171
        - Comcast-style: c-73-244-70-171.hsd1.fl.comcast.net
        - Other encoded IPs in hostnames
        """
        if not hostname:
            return ''
        
        # Check if it's already a plain IP address (contains only digits, dots, and possibly colons for IPv6)
        if re.match(r'^[\d.:]+$', hostname):
            return hostname
        
        # Try to extract IP from common ISP hostname patterns
        # Comcast: c-73-244-70-171.hsd1.fl.comcast.net
        # Pattern: dashes separating IP octets
        dash_pattern = re.search(r'(\d+)-(\d+)-(\d+)-(\d+)', hostname)
        if dash_pattern:
            return f"{dash_pattern.group(1)}.{dash_pattern.group(2)}.{dash_pattern.group(3)}.{dash_pattern.group(4)}"
        
        # Some ISPs use underscores: host_73_244_70_171.isp.net
        underscore_pattern = re.search(r'(\d+)_(\d+)_(\d+)_(\d+)', hostname)
        if underscore_pattern:
            return f"{underscore_pattern.group(1)}.{underscore_pattern.group(2)}.{underscore_pattern.group(3)}.{underscore_pattern.group(4)}"
        
        # Look for any IP-like pattern in the hostname (###.###.###.###)
        ip_pattern = re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', hostname)
        if ip_pattern:
            return ip_pattern.group(1)
        
        # No IP found, return empty
        return ''
    
    def _log_error(self, message: str):
        """Log an error message"""
        try:
            self.irc_client.add_status_message(f"[Script Error] {message}", 'error')
        except:
            print(f"Script Error: {message}")
    
    def _load_global_vars(self):
        """Load global variables from file"""
        try:
            vars_file = os.path.join(self.scripts_dir, 'global_vars.json')
            if os.path.exists(vars_file):
                with open(vars_file, 'r') as f:
                    self.global_vars = json.load(f)
        except Exception as e:
            print(f"Error loading global vars: {e}")
    
    def _save_global_vars(self):
        """Save global variables to file"""
        try:
            vars_file = os.path.join(self.scripts_dir, 'global_vars.json')
            with open(vars_file, 'w') as f:
                json.dump(self.global_vars, f, indent=2)
        except Exception as e:
            print(f"Error saving global vars: {e}")
    
    def _load_user_levels(self):
        """Load user levels from file"""
        try:
            levels_file = os.path.join(self.scripts_dir, 'user_levels.json')
            if os.path.exists(levels_file):
                with open(levels_file, 'r') as f:
                    self.user_levels = json.load(f)
        except Exception as e:
            print(f"Error loading user levels: {e}")
    
    def _save_user_levels(self):
        """Save user levels to file"""
        try:
            levels_file = os.path.join(self.scripts_dir, 'user_levels.json')
            with open(levels_file, 'w') as f:
                json.dump(self.user_levels, f, indent=2)
        except Exception as e:
            print(f"Error saving user levels: {e}")
    
    # ==================== File I/O Helper Functions ====================
    
    def _func_read(self, filename: str, line_num: Optional[int], context: Dict[str, str]) -> str:
        """Read from file - used by $read() identifier"""
        filename = self._substitute_vars(filename, context)
        filepath = os.path.join(self.scripts_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return ''
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n') for line in f.readlines()]
            
            if not lines:
                return ''
            
            if line_num is not None:
                if 1 <= line_num <= len(lines):
                    return lines[line_num - 1]
                return ''
            else:
                # Return random line
                import random
                return random.choice(lines)
        except Exception as e:
            return ''
    
    def _func_exists(self, filename: str, context: Dict[str, str]) -> bool:
        """Check if file exists - used by $exists() identifier"""
        filename = self._substitute_vars(filename, context)
        filepath = os.path.join(self.scripts_dir, filename)
        return os.path.exists(filepath)
    
    def _func_lines(self, filename: str, context: Dict[str, str]) -> int:
        """Count lines in file - used by $lines() identifier"""
        filename = self._substitute_vars(filename, context)
        filepath = os.path.join(self.scripts_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return 0
            with open(filepath, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception as e:
            return 0
    
    # ==================== List Helper Functions ====================
    
    def _get_list(self, prefix: str, name: str) -> Optional[List[str]]:
        """Get list by name (helper function)"""
        is_global = len(prefix) == 2
        target_lists = self.global_lists if is_global else self.local_lists
        return target_lists.get(name, None)
    
    def _func_list_get(self, prefix: str, name: str, index: int) -> str:
        """Get item from list at index - used by $list(@listname,N)"""
        lst = self._get_list(prefix, name)
        if lst and 0 <= index < len(lst):
            return lst[index]
        return ''
    
    def _func_list_count(self, prefix: str, name: str) -> int:
        """Get count of items in list - used by $list(@listname,count)"""
        lst = self._get_list(prefix, name)
        return len(lst) if lst else 0
    
    def _func_list_find(self, prefix: str, name: str, value: str) -> int:
        """Find index of value in list - used by $list(@listname,find,value)
        Returns -1 if not found"""
        lst = self._get_list(prefix, name)
        if lst:
            try:
                return lst.index(value)
            except ValueError:
                return -1
        return -1
    
    def _func_list_exists(self, prefix: str, name: str, value: str) -> bool:
        """Check if value exists in list - used by $list(@listname,exists,value)"""
        lst = self._get_list(prefix, name)
        return value in lst if lst else False
    
    # ==================== String Tokenization Functions ====================
    
    def _func_gettok(self, text: str, n: int, delim: int) -> str:
        """Get Nth token from delimited text"""
        try:
            delimiter = chr(delim)
            tokens = text.split(delimiter)
            if 1 <= n <= len(tokens):
                return tokens[n - 1]
        except (ValueError, IndexError):
            pass
        return ''
    
    def _func_numtok(self, text: str, delim: int) -> int:
        """Count tokens in delimited text"""
        try:
            delimiter = chr(delim)
            return len(text.split(delimiter))
        except:
            return 0
    
    def _func_findtok(self, text: str, search: str, start: int, delim: int) -> int:
        """Find token in delimited text, return position"""
        try:
            delimiter = chr(delim)
            tokens = text.split(delimiter)
            # Search from start position (1-indexed)
            for i in range(start - 1 if start > 0 else 0, len(tokens)):
                if tokens[i] == search:
                    return i + 1
        except (ValueError, IndexError):
            pass
        return 0
    
    def _func_addtok(self, text: str, token: str, delim: int) -> str:
        """Add token to delimited text (if not already present)"""
        try:
            delimiter = chr(delim)
            tokens = text.split(delimiter) if text else []
            if token not in tokens:
                tokens.append(token)
            return delimiter.join(tokens)
        except:
            return text
    
    def _func_remtok(self, text: str, token: str, delim: int) -> str:
        """Remove token from delimited text"""
        try:
            delimiter = chr(delim)
            tokens = text.split(delimiter)
            tokens = [t for t in tokens if t != token]
            return delimiter.join(tokens)
        except:
            return text
    
    # ==================== Math Functions ====================
    
    def _func_calc(self, expr: str) -> float:
        """Calculate mathematical expression safely"""
        try:
            # Create safe namespace with basic math functions
            import math
            safe_dict = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'pow': pow, 'sqrt': math.sqrt, 'floor': math.floor, 'ceil': math.ceil,
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'pi': math.pi, 'e': math.e,
                '__builtins__': {}
            }
            result = eval(expr, safe_dict, {})
            return result
        except Exception as e:
            self._log_error(f"Calc error in '{expr}': {e}")
            return 0
    
    def _func_round(self, value: str, decimals: int) -> float:
        """Round number to specified decimal places"""
        try:
            return round(float(value), decimals)
        except:
            return 0.0
    
    def _func_abs(self, value: str) -> float:
        """Get absolute value"""
        try:
            return abs(float(value))
        except:
            return 0.0
    
    def _func_sqrt(self, value: str) -> float:
        """Get square root"""
        try:
            import math
            return math.sqrt(float(value))
        except:
            return 0.0
    
    def _func_floor(self, value: str) -> int:
        """Floor value (round down)"""
        try:
            import math
            return math.floor(float(value))
        except:
            return 0
    
    def _func_ceil(self, value: str) -> int:
        """Ceiling value (round up)"""
        try:
            import math
            return math.ceil(float(value))
        except:
            return 0
    
    # ==================== Additional String Functions ====================
    
    def _func_pos(self, text: str, search: str) -> int:
        """Find position of substring in text (1-indexed, 0 if not found)"""
        try:
            pos = text.find(search)
            return pos + 1 if pos != -1 else 0
        except:
            return 0
    
    def _func_replace(self, text: str, old: str, new: str) -> str:
        """Replace all occurrences of old with new"""
        try:
            return text.replace(old, new)
        except:
            return text
    
    def _func_remove(self, text: str, substring: str) -> str:
        """Remove all occurrences of substring"""
        try:
            return text.replace(substring, '')
        except:
            return text
    
    def _func_str(self, text: str, count: int) -> str:
        """Repeat text N times"""
        try:
            return text * count
        except:
            return text
    
    def _func_strip(self, text: str) -> str:
        """Strip IRC color/control codes from text"""
        try:
            # Remove mIRC color codes (\x03)
            text = re.sub(r'\x03\d{0,2}(,\d{1,2})?', '', text)
            # Remove bold (\x02), underline (\x1f), reverse (\x16), reset (\x0f)
            text = text.replace('\x02', '').replace('\x1f', '').replace('\x16', '').replace('\x0f', '')
            return text
        except:
            return text
    
    def _func_reptok(self, text: str, old_token: str, new_token: str, delim: int) -> str:
        """Replace token in delimited text"""
        try:
            delimiter = chr(delim)
            tokens = text.split(delimiter)
            tokens = [new_token if t == old_token else t for t in tokens]
            return delimiter.join(tokens)
        except:
            return text
    
    # ==================== Utility Methods ====================
    
    # ==================== Script Management ====================
    
    def list_events(self) -> List[Dict]:
        """List all registered events"""
        return [
            {
                'index': i,
                'type': e.event_type,
                'match': e.match_pattern,
                'target': e.target,
                'enabled': e.enabled,
                'commands': e.commands[:50] + '...' if len(e.commands) > 50 else e.commands
            }
            for i, e in enumerate(self.events)
        ]
    
    def list_aliases(self) -> List[Dict]:
        """List all registered aliases"""
        return [
            {
                'name': a.name,
                'enabled': a.enabled,
                'commands': a.commands[:50] + '...' if len(a.commands) > 50 else a.commands
            }
            for a in self.aliases.values()
        ]
    
    def list_timers(self) -> List[Dict]:
        """List all active timers"""
        return [
            {
                'name': t.name,
                'interval': t.interval,
                'repetitions': t.repetitions,
                'current_rep': t.current_rep
            }
            for t in self.timers.values()
        ]
    
    def clear_all(self):
        """Clear all scripts, events, and aliases"""
        # Stop all timers
        for timer in self.timers.values():
            if timer.timer_id:
                try:
                    self.irc_client.window.after_cancel(timer.timer_id)
                except:
                    pass
        
        self.events.clear()
        self.aliases.clear()
        self.timers.clear()
        self.local_vars.clear()
        self.loaded_scripts.clear()
    
    def unload_script(self, filename: str) -> Tuple[bool, str]:
        """Unload a specific script by removing it and reloading all others"""
        if filename not in self.loaded_scripts:
            return False, f"Script not loaded: {filename}"
        
        try:
            # Save the list of scripts to reload before removing the target
            scripts_to_reload = [name for name in self.loaded_scripts.keys() if name != filename]
            
            # Clear all and reload remaining scripts
            
            # Clear everything
            for timer in self.timers.values():
                if timer.timer_id:
                    try:
                        self.irc_client.window.after_cancel(timer.timer_id)
                    except:
                        pass
            
            self.events.clear()
            self.aliases.clear()
            self.timers.clear()
            self.local_vars.clear()
            self.loaded_scripts.clear()
            
            # Reload all remaining scripts
            for script_name in scripts_to_reload:
                self.load_script(script_name)
            
            return True, f"Script unloaded: {filename}"
        except Exception as e:
            return False, f"Error unloading script: {e}"

