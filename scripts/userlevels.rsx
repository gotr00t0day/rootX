; ============================================
; RootX User Levels Example Script
; ============================================
; This script demonstrates the user levels system
; 
; Level Hierarchy:
;   0     = Normal user (default)
;   50    = Voice (+v)
;   100   = Operator (+o)
;   500   = Admin
;   1000  = Owner/Founder
;
; Commands:
;   !level [nick]     - Check user's level
;   !setlevel <nick> <level> - Set user level (admin+ only)
;   !adminhelp        - Show admin commands (admin+ only)
;   !op <nick>        - Give operator status (operator+ only)
;   !kick <nick>      - Kick user (operator+ only)
; ============================================

; --- Check User Level ---
on TEXT:!level*:#:{
    if ($2) {
        set %target = $2
    }
    else {
        set %target = $nick
    }
    set %userlevel = $level(%target)
    
    if (%userlevel == 0) {
        msg $chan %target is a normal user (level 0)
    }
    else if (%userlevel >= 1000) {
        msg $chan %target is an Owner (level %userlevel) 👑
    }
    else if (%userlevel >= 500) {
        msg $chan %target is an Admin (level %userlevel) ⭐
    }
    else if (%userlevel >= 100) {
        msg $chan %target is an Operator (level %userlevel) 🛡️
    }
    else if (%userlevel >= 50) {
        msg $chan %target has Voice (level %userlevel) 🔊
    }
    else {
        msg $chan %target has level %userlevel
    }
}

; --- Set User Level (Admin+ Only) ---
on TEXT:!setlevel*:#:{
    if ($level >= 500) {
        if ($2 && $3) {
            setlevel $2 $3
            msg $chan $nick set level for $2 to $3
        }
        else {
            msg $chan Usage: !setlevel <nickname> <level>
        }
    }
    else {
        msg $chan $nick: You need admin access (level 500+) to use this command.
    }
}

; --- Remove User Level (Admin+ Only) ---
on TEXT:!remlevel*:#:{
    if ($level >= 500) {
        if ($2) {
            remlevel $2
            msg $chan $nick removed level for $2
        }
        else {
            msg $chan Usage: !remlevel <nickname>
        }
    }
    else {
        msg $chan $nick: You need admin access (level 500+) to use this command.
    }
}

; --- Admin Help (Admin+ Only) ---
on TEXT:!adminhelp*:#:{
    if ($level >= 500) {
        msg $chan === Admin Commands (Level $level) ===
        msg $chan !setlevel <nick> <level> - Set user level
        msg $chan !remlevel <nick> - Remove user level
        msg $chan !level [nick] - Check user level
        msg $chan !adminlist - List all privileged users
    }
    else {
        msg $chan $nick: You need admin access (level 500+) to use this command.
    }
}

; --- List Admin Users (Admin+ Only) ---
on TEXT:!adminlist*:#:{
    if ($level >= 500) {
        msg $chan Listing users with elevated privileges...
        ; Note: We can't easily iterate through user_levels in the script
        ; This would need to be implemented as a built-in command
        msg $chan Use getlevel <nick> to check individual users
    }
    else {
        msg $chan $nick: You need admin access (level 500+) to use this command.
    }
}

; --- Give Operator (Op+ Only) ---
on TEXT:!op*:#:{
    if ($level >= 100) {
        if ($2) {
            mode $chan +o $2
            msg $chan $nick gave operator status to $2
        }
        else {
            msg $chan Usage: !op <nickname>
        }
    }
    else {
        msg $chan $nick: You need operator access (level 100+) to use this command.
    }
}

; --- Kick User (Op+ Only) ---
on TEXT:!kick*:#:{
    if ($level >= 100) {
        if ($2) {
            set %reason = $3-
            if (%reason) {
                kick $chan $2 %reason
            }
            else {
                kick $chan $2 Kicked by $nick
            }
        }
        else {
            msg $chan Usage: !kick <nickname> [reason]
        }
    }
    else {
        msg $chan $nick: You need operator access (level 100+) to use this command.
    }
}

; --- Voice User (Op+ Only) ---
on TEXT:!voice*:#:{
    if ($level >= 100) {
        if ($2) {
            mode $chan +v $2
            msg $chan $nick gave voice to $2
        }
        else {
            msg $chan Usage: !voice <nickname>
        }
    }
    else {
        msg $chan $nick: You need operator access (level 100+) to use this command.
    }
}

; --- Devoice User (Op+ Only) ---
on TEXT:!devoice*:#:{
    if ($level >= 100) {
        if ($2) {
            mode $chan -v $2
            msg $chan $nick removed voice from $2
        }
        else {
            msg $chan Usage: !devoice <nickname>
        }
    }
    else {
        msg $chan $nick: You need operator access (level 100+) to use this command.
    }
}

; --- Protected Kick Prevention ---
; Prevent kicking users with higher or equal level
on KICK:#:{
    set %kicker_level = $level($nick)
    set %kicked_level = $level($knick)
    
    if (%kicked_level >= %kicker_level && %kicked_level > 0) {
        ; Note: We can't prevent the kick, but we can rejoin them
        ; and notify the channel
        msg $chan Warning: $nick (level %kicker_level) kicked $knick (level %kicked_level)
    }
}

; --- Welcome Message with Level ---
on JOIN:*:#:{
    if ($nick != $me) {
        set %userlevel = $level($nick)
        if (%userlevel >= 500) {
            msg $chan Welcome back, Admin $nick! 👑
        }
        else if (%userlevel >= 100) {
            msg $chan Welcome back, Operator $nick! 🛡️
        }
        else if (%userlevel >= 50) {
            msg $chan Welcome, $nick! (+v)
        }
        else {
            msg $chan Welcome to $chan, $nick!
        }
    }
}

; --- Owner Command: Shutdown Bot (Owner Only) ---
on TEXT:!shutdown*:#:{
    if ($level >= 1000) {
        msg $chan Bot shutting down by order of $nick
        quit Shutdown by $nick
    }
    else {
        msg $chan $nick: You need owner access (level 1000) to use this command.
    }
}

; --- Info Command (Shows user their level) ---
alias /myinfo {
    if ($chan) {
        msg $chan Your level: $level | Use !level to check others
    }
    else {
        echo Your current access level: $level
    }
}

; --- Quick Admin Check Alias ---
alias /checkadmin {
    if ($1) {
        if ($islevel($1, 500) == True) {
            echo $1 is an admin (level $level($1))
        }
        else {
            echo $1 is NOT an admin (level $level($1))
        }
    }
}

