# 🎯 RootX User Levels System

A comprehensive access control system for managing permissions in your IRC bot.

## 📊 Level Hierarchy

```
1000  👑  Owner/Founder      - Complete control
500   ⭐  Admin              - Manage users, full bot access
100   🛡️  Operator/Moderator - Channel management
50    🔊  Voice              - Trusted user
0     👤  Normal User        - Default level
```

## 🔧 Script Commands

### Setting Levels

```mirc
setlevel <nickname> <level>
```
Sets a user's access level. The level persists across sessions.

**Example:**
```mirc
on TEXT:!promote*:#:{
    if ($level >= 500) {
        setlevel $2 100
        msg $chan $2 has been promoted to Operator!
    }
}
```

### Removing Levels

```mirc
remlevel <nickname>
```
Removes a user's custom level (reverts to 0).

### Getting Levels

```mirc
getlevel <nickname>
```
Displays a user's level in the status window.

## 🆔 Identifiers

### `$level` - Current User's Level
Returns the level of `$nick` (the person who triggered the event).

```mirc
on TEXT:!mystatus:#:{
    msg $chan Your level is: $level
}
```

### `$level(nickname)` - Specific User's Level
Returns the level of any user.

```mirc
on TEXT:!checklevel*:#:{
    set %userlevel = $level($2)
    msg $chan $2 has level %userlevel
}
```

### `$islevel(nickname, level)` - Level Check
Returns "True" or "False" if user has >= specified level.

```mirc
alias /checkaccess {
    if ($islevel($1, 500) == True) {
        echo $1 is an admin!
    }
}
```

## ✅ Conditional Access Control

### Simple Level Check

```mirc
on TEXT:!admincommand:#:{
    if ($level >= 500) {
        ; Admin-only code here
        msg $chan Executing admin command...
    }
    else {
        msg $chan Access denied. Admin level required.
    }
}
```

### Multi-Level Access

```mirc
on TEXT:!manage*:#:{
    if ($level >= 1000) {
        msg $chan Owner command executed
    }
    else if ($level >= 500) {
        msg $chan Admin command executed  
    }
    else if ($level >= 100) {
        msg $chan Operator command executed
    }
    else {
        msg $chan Insufficient access
    }
}
```

### Checking Other Users

```mirc
on TEXT:!demote*:#:{
    if ($level >= 500) {
        set %target_level = $level($2)
        if (%target_level < $level) {
            setlevel $2 0
            msg $chan $2 has been demoted
        }
        else {
            msg $chan Cannot demote user with equal/higher level
        }
    }
}
```

## 📝 Practical Examples

### Example 1: Protected Admin Command

```mirc
on TEXT:!reload*:#:{
    if ($level >= 500) {
        ; Reload scripts
        msg $chan Reloading scripts...
        echo Reload initiated by $nick (level $level)
    }
    else {
        msg $chan $nick: Admin access required (level 500+)
    }
}
```

### Example 2: Tiered Help System

```mirc
on TEXT:!help:#:{
    msg $chan === Help Commands ===
    msg $chan !level - Check your access level
    msg $chan !info - Bot information
    
    if ($level >= 100) {
        msg $chan === Operator Commands ===
        msg $chan !kick <nick> - Kick a user
        msg $chan !op <nick> - Give operator
    }
    
    if ($level >= 500) {
        msg $chan === Admin Commands ===
        msg $chan !setlevel <nick> <level> - Set user level
        msg $chan !reload - Reload scripts
    }
}
```

### Example 3: Auto-Op on Join

```mirc
on JOIN:*:#:{
    set %userlevel = $level($nick)
    
    if (%userlevel >= 100) {
        ; Auto-op users with operator level
        mode $chan +o $nick
        notice $nick Welcome! You have been auto-opped.
    }
    else if (%userlevel >= 50) {
        ; Auto-voice trusted users
        mode $chan +v $nick
    }
}
```

### Example 4: Kick Protection

```mirc
on TEXT:!kick*:#:{
    if ($level >= 100) {
        set %target_level = $level($2)
        
        if (%target_level >= $level) {
            msg $chan Cannot kick user with equal or higher level!
        }
        else {
            kick $chan $2 $3-
        }
    }
    else {
        msg $chan Operator access required
    }
}
```

### Example 5: Dynamic Permissions

```mirc
; Owner can change anything
on TEXT:!config*:#:{
    if ($level >= 1000) {
        ; Full config access
        msg $chan Owner: Full configuration access granted
    }
    else if ($level >= 500) {
        ; Limited config access
        msg $chan Admin: Limited configuration access
    }
    else {
        msg $chan Config access denied
    }
}
```

## 💾 Data Storage

User levels are stored in `scripts/user_levels.json`:

```json
{
  "Alice": 1000,
  "Bob": 500,
  "Charlie": 100,
  "Dave": 50
}
```

This file is automatically:
- **Loaded** when the bot starts
- **Saved** when levels are modified with `setlevel`
- **Persists** across bot restarts

## 🚀 Getting Started

### Step 1: Set Your Own Level

When you first start using the system, set yourself as owner:

```
/script eval setlevel YourNickname 1000
```

Or create a simple setup script:

```mirc
; scripts/setup.rsx
alias /makeowner {
    setlevel $me 1000
    echo You are now the owner!
}
```

Then run: `/makeowner`

### Step 2: Load the User Levels Script

The `userlevels.rsx` script is automatically loaded from the `scripts/` folder.

Verify it loaded:
```
/script list
```

### Step 3: Set Admin/Mod Levels

```
!setlevel Alice 500     ; Make Alice an admin
!setlevel Bob 100       ; Make Bob an operator
!setlevel Charlie 50    ; Give Charlie voice
```

### Step 4: Test Commands

```
!level              ; Check your own level
!level Alice        ; Check Alice's level
!adminhelp          ; Show admin commands (if you're admin)
```

## 🔐 Security Best Practices

1. **Protect Owner Status**
   - Keep owner level (1000) for yourself only
   - Never give owner to untrusted users

2. **Use Progressive Levels**
   - Don't jump from 0 to 1000
   - Use intermediate levels for specific permissions

3. **Regular Audits**
   - Periodically check `user_levels.json`
   - Remove inactive users

4. **Backup Your Data**
   ```bash
   cp scripts/user_levels.json scripts/user_levels.json.backup
   ```

5. **Level Checks in Scripts**
   - Always validate user levels before dangerous operations
   - Check target level vs. executor level for management commands

## 🎨 Custom Level Names

Define custom levels in your scripts:

```mirc
alias /getlevelname {
    set %lvl = $level($1)
    
    if (%lvl >= 1000) {
        return Owner
    }
    else if (%lvl >= 500) {
        return Admin
    }
    else if (%lvl >= 100) {
        return Moderator
    }
    else if (%lvl >= 50) {
        return VIP
    }
    else {
        return User
    }
}
```

## 📚 Advanced Usage

### Custom Permission Ranges

```mirc
; Define custom permission ranges
; 600-699: Special admin roles
; 200-299: Channel moderators
; 150-199: Trial moderators

on TEXT:!special:#:{
    if ($level >= 600 && $level < 700) {
        msg $chan Special admin access granted
    }
}
```

### Temporary Elevation

```mirc
; Grant temporary operator for specific task
on TEXT:!tempop*:#:{
    if ($level >= 500) {
        set %original_level = $level($2)
        setlevel $2 100
        msg $chan $2 temporarily elevated to operator
        
        ; Use a timer to revert (5 minutes)
        timer tempop_$2 300000 1 { setlevel $2 %original_level }
    }
}
```

## 🛠️ Troubleshooting

**Problem:** User levels not persisting
- Check if `scripts/user_levels.json` exists and is writable
- Verify script engine loaded: `/script list`

**Problem:** Level checks not working
- Make sure you're using `$level` not `%level` (identifier vs variable)
- Verify script syntax: reload with `/script reload`

**Problem:** Can't set levels
- Ensure you have admin access (500+) to use setlevel
- Check if script is running: `/script list`

## 📖 Complete Reference

| Function | Description | Example |
|----------|-------------|---------|
| `setlevel <nick> <lvl>` | Set user level | `setlevel Alice 500` |
| `remlevel <nick>` | Remove level | `remlevel Alice` |
| `getlevel <nick>` | Get level | `getlevel Alice` |
| `$level` | Current user's level | `if ($level >= 500)` |
| `$level(nick)` | Specific user's level | `$level(Alice)` |
| `$islevel(nick,lvl)` | Check if has level | `$islevel(Alice,500)` |

---

**Happy scripting! 🚀**

For more examples, see `scripts/userlevels.rsx`

