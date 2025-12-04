"""
RootX Script Engine - mIRC-like scripting language for the IRC client

Syntax Reference:
================

EVENTS:
    on <EVENT>:<match>:<target>:{ commands }
    
    Events:
        TEXT     - Triggered on text messages (on TEXT:*hello*:#:{ msg $chan Hi! })
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
    
    Match patterns:
        *        - Match anything
        *text*   - Contains text
        text*    - Starts with text
        *text    - Ends with text
        exact    - Exact match

ALIASES:
    alias /commandname { commands }
    alias /greet { msg $chan Hello everyone from $me! }

VARIABLES:
    Local:  %var = value
    Global: %%var = value (persists across script reloads)
    
IDENTIFIERS (read-only):
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
    $rand(N) - Random number 0 to N-1
    $len(text) - Length of text
    $upper(text) - Uppercase
    $lower(text) - Lowercase
    $level(nick) - Get user's level (0 if not set)
    $islevel(nick,level) - Check if user has level >= specified (returns True/False)

COMMANDS:
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
    echo <message>             - Display message locally
    timer <name> <interval> <reps> { commands } - Create a timer
    timer <name> off           - Stop a timer
    halt                       - Stop script execution
    return [value]             - Return from alias
    setlevel <nick> <level>    - Set user's access level (0-1000)
    remlevel <nick>            - Remove user's access level
    getlevel <nick>            - Display user's current level

CONTROL FLOW:
    if (<condition>) { commands }
    if (<condition>) { commands } else { commands }
    while (<condition>) { commands }
    
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

EXAMPLE SCRIPT:
    ; This is a comment
    
    ; Greet users who join
    on JOIN:#mychannel:{
        msg $chan Welcome to the channel, $nick!
    }
    
    ; Respond to !hello command
    on TEXT:!hello*:#:{
        msg $chan Hello $nick! You said: $1-
    }
    
    ; Custom command
    alias /greet {
        if ($1) {
            msg $chan Hello $1!
        }
        else {
            msg $chan Hello everyone!
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
        self.timers: Dict[str, ScriptTimer] = {}
        
        # Variables
        self.local_vars: Dict[str, str] = {}
        self.global_vars: Dict[str, str] = {}
        
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
        
        # Create scripts directory if it doesn't exist
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        
        # Load global variables and user levels
        self._load_global_vars()
        self._load_user_levels()
    
    # ==================== Script Loading ====================
    
    def load_script(self, filename: str) -> Tuple[bool, str]:
        """Load a script file"""
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
            
            # Substitute variables and identifiers
            line = self._substitute_vars(line, context)
            
            # Execute the command
            self._execute_single_command(line, context, server, target)
    
    def _split_commands(self, commands: str) -> List[str]:
        """Split command block into individual commands, handling nested braces"""
        result = []
        current = ""
        brace_depth = 0
        
        for char in commands:
            if char == '{':
                brace_depth += 1
                current += char
            elif char == '}':
                brace_depth -= 1
                current += char
            elif char == '\n' and brace_depth == 0:
                if current.strip():
                    result.append(current.strip())
                current = ""
            else:
                current += char
        
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
            
            # Parse command and arguments
            parts = line.split(None, 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ''
            
            # Execute built-in commands
            if cmd == 'msg':
                self._cmd_msg(args, server)
            elif cmd == 'notice':
                self._cmd_notice(args, server)
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
                self.return_value = args
                self.halt_execution = True
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
            else:
                # Unknown command - might be a /command
                if cmd.startswith('/'):
                    self.irc_client.handle_command(line, target)
                    
        except Exception as e:
            self._log_error(f"Script error executing '{line}': {e}")
    
    # ==================== Built-in Commands ====================
    
    def _cmd_msg(self, args: str, server: str):
        """Send a message"""
        parts = args.split(None, 1)
        if len(parts) >= 2:
            target, message = parts
            self.irc_client.send_command(f"PRIVMSG {target} :{message}", server)
    
    def _cmd_notice(self, args: str, server: str):
        """Send a notice"""
        parts = args.split(None, 1)
        if len(parts) >= 2:
            target, message = parts
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
    
    # ==================== Control Structures ====================
    
    def _handle_if(self, line: str, context: Dict[str, str], server: str, target: str):
        """Handle if/else statements"""
        # Parse: if (condition) { commands } else { commands }
        match = re.match(r'if\s*\(([^)]+)\)\s*{\s*([\s\S]*?)\s*}(?:\s*else\s*{\s*([\s\S]*?)\s*})?', line)
        if match:
            condition, if_commands, else_commands = match.groups()
            
            if self._evaluate_condition(condition, context):
                self.execute_commands(if_commands, context, server, target)
            elif else_commands:
                self.execute_commands(else_commands, context, server, target)
    
    def _handle_while(self, line: str, context: Dict[str, str], server: str, target: str):
        """Handle while loops"""
        match = re.match(r'while\s*\(([^)]+)\)\s*{\s*([\s\S]*?)\s*}', line)
        if match:
            condition, commands = match.groups()
            
            # Safety limit to prevent infinite loops
            max_iterations = 1000
            iterations = 0
            
            while self._evaluate_condition(condition, context) and iterations < max_iterations:
                if self.halt_execution:
                    break
                self.execute_commands(commands, context, server, target)
                iterations += 1
    
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
    
    def _substitute_vars(self, text: str, context: Dict[str, str]) -> str:
        """Substitute variables and identifiers in text"""
        # Handle function-style identifiers first: $func(args)
        text = re.sub(r'\$rand\((\d+)\)', lambda m: str(random.randint(0, int(m.group(1))-1)), text)
        text = re.sub(r'\$len\(([^)]*)\)', lambda m: str(len(self._substitute_vars(m.group(1), context))), text)
        text = re.sub(r'\$upper\(([^)]*)\)', lambda m: self._substitute_vars(m.group(1), context).upper(), text)
        text = re.sub(r'\$lower\(([^)]*)\)', lambda m: self._substitute_vars(m.group(1), context).lower(), text)
        text = re.sub(r'\$left\(([^,]*),(\d+)\)', lambda m: self._substitute_vars(m.group(1), context)[:int(m.group(2))], text)
        text = re.sub(r'\$right\(([^,]*),(\d+)\)', lambda m: self._substitute_vars(m.group(1), context)[-int(m.group(2)):], text)
        text = re.sub(r'\$mid\(([^,]*),(\d+),(\d+)\)', lambda m: self._substitute_vars(m.group(1), context)[int(m.group(2)):int(m.group(2))+int(m.group(3))], text)
        
        # User level functions
        text = re.sub(r'\$level\(([^)]+)\)', lambda m: str(self.user_levels.get(self._substitute_vars(m.group(1), context), 0)), text)
        text = re.sub(r'\$islevel\(([^,]+),(\d+)\)', lambda m: str(self.user_levels.get(self._substitute_vars(m.group(1), context), 0) >= int(m.group(2))), text)
        
        # Handle global variables: %%varname
        for name, value in self.global_vars.items():
            text = text.replace(f'%%{name}', value)
        
        # Handle local variables: %varname
        for name, value in self.local_vars.items():
            text = text.replace(f'%{name}', value)
        
        # Handle context identifiers
        text = text.replace('$nick', context.get('nick', ''))
        text = text.replace('$chan', context.get('chan', ''))
        text = text.replace('$target', context.get('target', ''))
        text = text.replace('$text', context.get('text', ''))
        text = text.replace('$server', context.get('server', ''))
        text = text.replace('$me', context.get('me', ''))
        
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
    
    def _get_my_nick(self, server: str) -> str:
        """Get the current nickname for a server"""
        try:
            if server in self.irc_client.connections:
                return self.irc_client.connections[server].get('nickname', '')
        except:
            pass
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

