; ============================================
; RootX Sample Script
; ============================================
; This script demonstrates the scripting features
; Place .rsx or .txt files in the scripts folder
; to auto-load them when the client starts.
;
; Use /script reload to reload all scripts
; ============================================

; --- Welcome Message on Join ---
; Greets users when they join a channel you're in
on JOIN:*:#:{
    ; Don't greet ourselves
    if ($nick != $me) {
        msg $chan Welcome to $chan, $nick!
    }
}

; --- Auto-Response to Greetings ---
; Responds when someone says hello/hi to the channel
on TEXT:*hello*:#:{
    msg $chan Hello $nick! How are you today?
}

on TEXT:*hi*:#:{
    msg $chan Hey there, $nick!
}

; --- Command: !time ---
; Responds with current time when someone types !time
on TEXT:!time:#:{
    msg $chan Current time is $time on $date
}

; --- Command: !dice ---
; Roll a dice when someone types !dice
on TEXT:!dice:#:{
    set %roll = $rand(6)
    msg $chan $nick rolled a %roll!
}

; --- Custom Alias: /greet ---
; Usage: /greet or /greet nickname
alias /greet {
    if ($1) {
        msg $chan Hello $1! 👋
    }
    else {
        msg $chan Hello everyone! 👋
    }
}

; --- Custom Alias: /slap ---
; Fun /slap command like classic IRC
alias /slap {
    if ($1) {
        me $chan slaps $1 around with a large trout 🐟
    }
    else {
        echo Usage: /slap <nickname>
    }
}

; --- Custom Alias: /info ---
; Shows client info
alias /info {
    msg $chan I'm using $version - Scripting enabled!
}

; --- Private Message Auto-Response ---
; Auto-respond to PMs when away (example - commented out)
; on TEXT:*:?:{
;     msg $nick I'm currently away. I'll get back to you soon!
; }

