# RootX Scripting Quick Reference

## 📋 Event Syntax

```mirc
on EVENT:pattern:target:{
    commands
}
```

| Event | Triggered When |
|-------|---------------|
| `TEXT` | Message sent |
| `JOIN` | User joins |
| `PART` | User leaves |
| `QUIT` | User disconnects |
| `KICK` | User kicked |
| `NICK` | Nickname changes |
| `ACTION` | /me action |
| `MODE` | Mode changes |

## 🎯 Patterns

| Pattern | Matches |
|---------|---------|
| `*` | Everything |
| `*hello*` | Contains "hello" |
| `!cmd` | Exact "!cmd" |
| `!cmd*` | Starts with "!cmd" |

## 🎪 Aliases

```mirc
alias /name {
    commands
}
```

**Parameters:** `$1` `$2` `$3` ... `$N`  
**All from N:** `$N-`

## 📦 Variables

```mirc
set %local = value      ; Temporary
set %%global = value    ; Permanent
```

## 🔍 Identifiers

### People & Places
- `$nick` - Who triggered event
- `$chan` - Current channel
- `$me` - Your nickname
- `$server` - Current server
- `$target` - Message target

### Message Parts
- `$text` - Full message
- `$1` `$2` `$3` - Words 1, 2, 3
- `$1-` - All words from 1
- `$2-` - All words from 2

### Time & Date
- `$time` - HH:MM:SS
- `$date` - YYYY-MM-DD
- `$version` - Client version

### String Functions
- `$len(text)` - Text length
- `$upper(text)` - UPPERCASE
- `$lower(text)` - lowercase
- `$left(text,N)` - First N chars
- `$right(text,N)` - Last N chars
- `$mid(text,S,L)` - Substring
- `$pos(text,search)` - Find position
- `$replace(text,old,new)` - Replace text
- `$remove(text,sub)` - Remove substring
- `$str(text,N)` - Repeat N times
- `$chr(N)` - ASCII to char
- `$asc(char)` - Char to ASCII
- `$strip(text)` - Remove IRC codes

### Math Functions
- `$rand(N)` - Random 0 to N-1
- `$calc(expr)` - Calculate (e.g., `$calc(5+3*2)`)
- `$round(N,decimals)` - Round number
- `$abs(N)` - Absolute value
- `$sqrt(N)` - Square root
- `$floor(N)` - Round down
- `$ceil(N)` - Round up

### Tokenization (delim: comma=44, space=32, pipe=124)
- `$gettok(text,N,delim)` - Get Nth token
- `$numtok(text,delim)` - Count tokens
- `$findtok(text,search,start,delim)` - Find token
- `$addtok(text,token,delim)` - Add token
- `$remtok(text,token,delim)` - Remove token
- `$reptok(text,old,new,delim)` - Replace token

### File I/O
- `$read(file)` - Read random line
- `$read(file,N)` - Read line N
- `$exists(file)` - Check if file exists
- `$lines(file)` - Count lines in file

### User Levels
- `$level` - Current user's level
- `$level(nick)` - Specific user's level
- `$islevel(nick,N)` - Check if level >= N

## 🔀 Control Flow

```mirc
if (condition) {
    do this
}
else {
    do that
}
```

### Conditions
- `==` Equals
- `!=` Not equals
- `>` Greater
- `<` Less
- `>=` Greater or equal
- `<=` Less or equal
- `isin` Contains
- `!isin` Not contains
- `iswm` Wildcard match

## 💬 Commands

```mirc
msg <target> <message>          ; Send message
notice <target> <message>       ; Send notice
me <target> <action>            ; Send /me action
echo <message>                  ; Display locally
halt                            ; Stop execution
return [value]                  ; Exit alias

; Channel Management
join <channel> [key]            ; Join channel
part <channel> [message]        ; Leave channel
kick <channel> <nick> [reason]  ; Kick user
ban <channel> <mask>            ; Ban user
mode <target> <modes>           ; Set modes

; User Levels
setlevel <nick> <level>         ; Set user level
remlevel <nick>                 ; Remove level
getlevel <nick>                 ; Show level

; File I/O
write <file> <text>             ; Append to file
read <file> [line]              ; Read from file
remove <file>                   ; Delete file

; Timers
timer <name> <ms> <reps> {...}  ; Create timer
timer <name> off                ; Stop timer
```

## 📝 Examples

### Auto-Greet
```mirc
on JOIN:*:#:{
    if ($nick != $me) {
        msg $chan Welcome, $nick!
    }
}
```

### Command with Parameter
```mirc
on TEXT:!greet*:#:{
    msg $chan Hello $2!
}
```

### Dice Roll
```mirc
on TEXT:!dice:#:{
    set %roll = $rand(6)
    msg $chan $nick rolled: %roll
}
```

### Admin Check
```mirc
on TEXT:!admin:#:{
    if ($level >= 500) {
        msg $chan Admin command OK
    }
    else {
        msg $chan Access denied
    }
}
```

### Time Command
```mirc
on TEXT:!time:#:{
    msg $chan Time: $time Date: $date
}
```

### Echo Alias
```mirc
alias /say {
    msg $chan $1-
}
```

## 🔧 Management

```
/script load <file>      ; Load script
/script unload           ; Unload all
/script reload           ; Reload all
/script list             ; Show loaded
```

## 🐛 Debugging

```mirc
echo Debug message              ; Print to status
```

```
/script list                    ; Check if loaded
```

## 📚 More Info

- Full Tutorial: `SCRIPTING_TUTORIAL.md`
- User Levels: `USER_LEVELS_GUIDE.md`
- Examples: `scripts/sample.rsx`

---

*RootX IRC Client v2*

