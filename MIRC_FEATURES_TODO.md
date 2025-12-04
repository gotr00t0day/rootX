# mIRC Features Implementation Guide

This document outlines additional mIRC-style features that can be added to RootX.

## 🎯 Priority 1: Essential Features

### 1. File I/O Operations

**Commands to add:**
```python
# In script_engine.py _execute_single_command():

elif cmd == 'write':
    self._cmd_write(args)
elif cmd == 'read':
    self._cmd_read(args)
elif cmd == 'remove':
    self._cmd_remove(args)
```

**Implementation:**
```python
def _cmd_write(self, args: str):
    """Write text to file"""
    parts = args.split(None, 1)
    if len(parts) >= 2:
        filename, text = parts
        filepath = os.path.join(self.scripts_dir, filename)
        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
        except Exception as e:
            self._log_error(f"Error writing to {filename}: {e}")

def _cmd_read(self, args: str):
    """Read from file"""
    parts = args.split()
    filename = parts[0] if parts else ''
    line_num = int(parts[1]) if len(parts) > 1 else None
    
    if filename:
        filepath = os.path.join(self.scripts_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if line_num is not None and 0 < line_num <= len(lines):
                    self._log_error(lines[line_num - 1].strip())
                else:
                    import random
                    self._log_error(random.choice(lines).strip())
        except Exception as e:
            self._log_error(f"Error reading {filename}: {e}")
```

**Identifiers:**
```python
# In _substitute_vars():
text = re.sub(r'\$read\(([^,)]+)\)', 
              lambda m: self._func_read(m.group(1), None), text)
text = re.sub(r'\$read\(([^,)]+),(\d+)\)', 
              lambda m: self._func_read(m.group(1), int(m.group(2))), text)
text = re.sub(r'\$exists\(([^)]+)\)', 
              lambda m: str(os.path.exists(os.path.join(self.scripts_dir, m.group(1)))), text)
```

**Usage Examples:**
```mirc
; Write quotes to file
on TEXT:!addquote*:#:{
    write quotes.txt $2-
    msg $chan Quote added!
}

; Read random quote
on TEXT:!quote:#:{
    msg $chan $read(quotes.txt)
}

; Read specific line
on TEXT:!quote*:#:{
    msg $chan $read(quotes.txt, $2)
}
```

---

### 2. String Tokenization

**Identifiers to add:**
```python
# In _substitute_vars():

# $gettok(text, N, delim)
text = re.sub(r'\$gettok\(([^,]+),(\d+),(\d+)\)', 
              lambda m: self._func_gettok(m.group(1), int(m.group(2)), int(m.group(3))), 
              text)

# $numtok(text, delim)
text = re.sub(r'\$numtok\(([^,]+),(\d+)\)', 
              lambda m: str(len(m.group(1).split(chr(int(m.group(2)))))), 
              text)

# $findtok(text, search, N, delim)
text = re.sub(r'\$findtok\(([^,]+),([^,]+),(\d+),(\d+)\)', 
              lambda m: self._func_findtok(m.group(1), m.group(2), int(m.group(3)), int(m.group(4))), 
              text)
```

**Implementation:**
```python
def _func_gettok(self, text: str, n: int, delim: int) -> str:
    """Get Nth token from text"""
    tokens = text.split(chr(delim))
    if 1 <= n <= len(tokens):
        return tokens[n - 1]
    return ''

def _func_findtok(self, text: str, search: str, n: int, delim: int) -> str:
    """Find token in text"""
    tokens = text.split(chr(delim))
    try:
        return str(tokens.index(search, n - 1) + 1)
    except (ValueError, IndexError):
        return '0'
```

**Usage Examples:**
```mirc
; Parse CSV
on TEXT:!parse*:#:{
    ; Input: !parse apple,banana,orange
    set %fruit = $gettok($2, 2, 44)  ; 44 = comma ASCII
    msg $chan Second fruit: %fruit   ; Output: banana
}

; Count items
on TEXT:!count*:#:{
    set %num = $numtok($2, 44)
    msg $chan Found %num items
}

; Find item position
on TEXT:!find*:#:{
    set %pos = $findtok($2, banana, 1, 44)
    msg $chan Found at position: %pos
}
```

---

### 3. Math Operations

**Identifier to add:**
```python
# $calc(expression)
text = re.sub(r'\$calc\(([^)]+)\)', 
              lambda m: str(self._func_calc(m.group(1))), 
              text)

# $round(N, decimals)
text = re.sub(r'\$round\(([^,]+),(\d+)\)', 
              lambda m: str(round(float(m.group(1)), int(m.group(2)))), 
              text)

# $abs(N)
text = re.sub(r'\$abs\(([^)]+)\)', 
              lambda m: str(abs(float(m.group(1)))), 
              text)
```

**Implementation:**
```python
def _func_calc(self, expr: str) -> float:
    """Calculate mathematical expression"""
    try:
        # Safe eval with limited scope
        return eval(expr, {"__builtins__": {}}, {})
    except Exception as e:
        self._log_error(f"Calc error: {e}")
        return 0
```

**Usage Examples:**
```mirc
; Calculator bot
on TEXT:!calc*:#:{
    set %result = $calc($2-)
    msg $chan Result: %result
}

; Statistics
on TEXT:!average*:#:{
    set %sum = $calc($2 + $3 + $4)
    set %avg = $calc(%sum / 3)
    set %rounded = $round(%avg, 2)
    msg $chan Average: %rounded
}

; Dice with math
on TEXT:!roll*:#:{
    set %dice = $calc($rand(6) + 1)
    msg $chan $nick rolled %dice
}
```

---

## 🎯 Priority 2: Data Management

### 4. Hash Tables

**Commands:**
```python
elif cmd == 'hadd':
    self._cmd_hadd(args)
elif cmd == 'hdel':
    self._cmd_hdel(args)
elif cmd == 'hsave':
    self._cmd_hsave(args)
elif cmd == 'hload':
    self._cmd_hload(args)
```

**Storage:**
```python
# In __init__:
self.hash_tables: Dict[str, Dict[str, str]] = {}
```

**Implementation:**
```python
def _cmd_hadd(self, args: str):
    """Add item to hash table"""
    parts = args.split(None, 2)
    if len(parts) >= 3:
        table, item, value = parts
        if table not in self.hash_tables:
            self.hash_tables[table] = {}
        self.hash_tables[table][item] = value

def _cmd_hdel(self, args: str):
    """Delete item from hash table"""
    parts = args.split(None, 1)
    if len(parts) >= 2:
        table, item = parts
        if table in self.hash_tables and item in self.hash_tables[table]:
            del self.hash_tables[table][item]
```

**Identifiers:**
```python
# $hget(table, item)
text = re.sub(r'\$hget\(([^,]+),([^)]+)\)', 
              lambda m: self.hash_tables.get(m.group(1), {}).get(m.group(2), ''), 
              text)

# $hfind(table, text)
text = re.sub(r'\$hfind\(([^,]+),([^)]+)\)', 
              lambda m: self._func_hfind(m.group(1), m.group(2)), 
              text)
```

**Usage:**
```mirc
; User database
on TEXT:!register:#:{
    hadd users $nick registered
    hadd userdata $nick $+ _email $2
    msg $chan $nick registered with email: $2
}

on TEXT:!checkuser*:#:{
    if ($hget(users, $2)) {
        msg $chan $2 is registered
    }
    else {
        msg $chan $2 is not registered
    }
}

; Quote database with IDs
on TEXT:!addquote*:#:{
    set %id = $calc($hget(quotecount) + 1)
    hadd quotes %id $2-
    hadd quotecount total %id
    msg $chan Quote #%id added
}

on TEXT:!quote*:#:{
    msg $chan Quote #$2: $hget(quotes, $2)
}
```

---

### 5. INI File Handling

**Commands:**
```python
elif cmd == 'writeini':
    self._cmd_writeini(args)
elif cmd == 'remini':
    self._cmd_remini(args)
```

**Implementation:**
```python
import configparser

def _cmd_writeini(self, args: str):
    """Write to INI file"""
    parts = args.split(None, 3)
    if len(parts) >= 4:
        filename, section, key, value = parts
        filepath = os.path.join(self.scripts_dir, filename)
        
        config = configparser.ConfigParser()
        if os.path.exists(filepath):
            config.read(filepath)
        
        if section not in config:
            config[section] = {}
        config[section][key] = value
        
        with open(filepath, 'w') as f:
            config.write(f)

def _func_readini(self, filename: str, section: str, key: str) -> str:
    """Read from INI file"""
    filepath = os.path.join(self.scripts_dir, filename)
    if os.path.exists(filepath):
        config = configparser.ConfigParser()
        config.read(filepath)
        return config.get(section, key, fallback='')
    return ''
```

**Usage:**
```mirc
; Bot configuration
on TEXT:!setconfig*:#:{
    if ($level >= 500) {
        writeini config.ini bot $2 $3-
        msg $chan Config set: $2 = $3-
    }
}

on TEXT:!getconfig*:#:{
    set %value = $readini(config.ini, bot, $2)
    msg $chan Config $2: %value
}

; User preferences
on TEXT:!setpref*:#:{
    writeini prefs.ini $nick timezone $2
    msg $chan Timezone set to $2
}
```

---

## 🎯 Priority 3: Advanced Features

### 6. Raw Events

**Add to event types:**
```python
# In parse_script():
# Already parses: on EVENT:match:target:{ commands }

# For raw events:
# on ^401:*:{ ... }  - ^ prefix means raw numeric

raw_pattern = r'on\s+\^?(\d{3}):([^:]*):([^:]*)\s*:{'
for match in re.finditer(raw_pattern, content, re.IGNORECASE):
    numeric, match_pattern, target, start_pos = ...
    self.register_raw_event(numeric, match_pattern, target, commands)
```

**Usage:**
```mirc
; Handle nickname in use
raw 433:*:{
    nick $me $+ _
    echo Nickname was in use, trying alternate
}

; Custom MOTD handling
raw 372:*:{
    echo MOTD: $2-
}

; Away message
raw 301:*:{
    echo $2 is away: $3-
}
```

---

### 7. Regex Support

**Identifier:**
```python
# $regex(text, /pattern/)
text = re.sub(r'\$regex\(([^,]+),/([^/]+)/\)', 
              lambda m: str(bool(re.search(m.group(2), m.group(1)))), 
              text)
```

**Usage:**
```mirc
; URL detector
on TEXT:*:#:{
    if ($regex($text, /(https?:\/\/[^\s]+)/)) {
        msg $chan URL detected!
    }
}

; Email validator
on TEXT:!email*:#:{
    if ($regex($2, /^[\w\.-]+@[\w\.-]+\.\w+$/)) {
        msg $chan Valid email!
    }
    else {
        msg $chan Invalid email
    }
}
```

---

## 📋 Implementation Checklist

### Phase 1 (High Priority)
- [ ] File I/O (write, read, remove commands)
- [ ] File identifiers ($read, $exists)
- [ ] String tokens ($gettok, $numtok, $findtok)
- [ ] Math operations ($calc, $round, $abs)
- [ ] More string functions ($pos, $replace, $remove)

### Phase 2 (Medium Priority)
- [ ] Hash tables (hadd, hdel, hsave, hload)
- [ ] Hash identifiers ($hget, $hfind)
- [ ] INI file handling (writeini, $readini, remini)
- [ ] Regex support ($regex, $regml, $regsubex)

### Phase 3 (Advanced)
- [ ] Raw events (on ^NNN:*:)
- [ ] CTCP events (ctcp *:VERSION:)
- [ ] Custom windows (window @name, aline, clear)
- [ ] Sockets (sockopen, sockwrite, sockread)
- [ ] DCC support (dcc send, dcc chat)

### Phase 4 (Nice to Have)
- [ ] Sound support (splay, snd)
- [ ] Dialog system (dialog definitions)
- [ ] Picture windows (drawing/graphics)
- [ ] Binary variables (&binvar)

---

## 🎯 Quick Wins

These can be added quickly with high impact:

1. **$pos(text, search)** - Find position in string
2. **$replace(text, old, new)** - Replace text
3. **$remove(text, substring)** - Remove substring
4. **$chr(N)** - Get character from ASCII code
5. **$asc(char)** - Get ASCII code from character
6. **$str(text, N)** - Repeat text N times
7. **$bytes(N)** - Format bytes (1024 → 1KB)
8. **$duration(seconds)** - Format duration (3661 → 1hr 1min 1sec)

---

## 💡 Usage Scenarios

### Scenario 1: Quote Bot with File I/O
```mirc
on TEXT:!addquote*:#:{
    write quotes.txt $2-
    set %count = $lines(quotes.txt)
    msg $chan Quote #%count added
}

on TEXT:!quote:#:{
    set %total = $lines(quotes.txt)
    set %random = $calc($rand(%total) + 1)
    msg $chan $read(quotes.txt, %random)
}
```

### Scenario 2: Statistics with Hash Tables
```mirc
on TEXT:*:#:{
    ; Count words per user
    set %current = $hget(wordcount, $nick)
    if (!%current) { set %current = 0 }
    set %words = $numtok($text, 32)  ; 32 = space
    set %new = $calc(%current + %words)
    hadd wordcount $nick %new
}

on TEXT:!stats:#:{
    msg $chan $nick has said $hget(wordcount, $nick) words
}
```

### Scenario 3: Config Management
```mirc
on CONNECT:*:*:{
    set %autojoin = $readini(config.ini, server, autojoin)
    if (%autojoin) {
        join %autojoin
    }
}
```

---

## 🚀 Next Steps

1. Start with **File I/O** - Most useful and easiest
2. Add **String tokens** - Essential for parsing
3. Implement **$calc()** - Common request
4. Add **Hash tables** - Great for performance
5. Consider **INI files** - Easy persistence

Would you like me to implement any of these features?

