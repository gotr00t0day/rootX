; ================================
;
; Functionality Script
;
; Author: c0d3Ninja
;
; ================================

; WHOIS event - triggered when WHOIS data is received
on WHOIS:*:*:{
    set %whois_nick = $whois($nick, nick)
    set %whois_user = $whois($nick, username)
    set %whois_host = $whois($nick, hostname)
    set %whois_real = $whois($nick, realname)
    set %whois_hostmask = $whois($nick, hostmask)
    set %whois_server = $whois($nick, server)
    set %whois_idle = $whois($nick, idle)
    set %whois_channels = $whois($nick, channels)
    
    ; Save WHOIS results to file
    write whois_log.txt [$date $time] WHOIS for %whois_nick:
    write whois_log.txt [$date $time]   Hostmask: %whois_hostmask
    write whois_log.txt [$date $time]   Username: %whois_user
    write whois_log.txt [$date $time]   Hostname: %whois_host
    write whois_log.txt [$date $time]   Realname: %whois_real
    write whois_log.txt [$date $time]   Server: %whois_server
    write whois_log.txt [$date $time]   Idle: %whois_idle seconds
    write whois_log.txt [$date $time]   Channels: %whois_channels
    write whois_log.txt [$date $time] ---
}


; Version
on TEXT:!version*:#:{
    msg $chan RootX IRC Client v2
}

; Display the menu
on TEXT:!menu*:#:{
    msg $chan == RootX Features ==
    msg $chan Version: !version
    msg $chan Spylog: !spylog <nickname>
    msg $chan SuperUsers: !superusers
    msg $chan GetHostname: !gethostname <nickname>
    msg $chan AddSuperUser: !add <nickname>
}

; ================================
;
; RootX User Access
;
; Scripts super users have access to:
; 
; /spylog - spy on IRC channels
;
; ================================


; check for permissions
function checkUsers(file) {
    set %total = $lines($1)
    if (%total == 0) {
        return 
    }
    
    set %i = 1
    set %result = 
    
    while (%i <= %total) {
        set %line = $read($1, %i)
        if (%i == 1) {
            set %result = %line
        }
        else {
            set %result = %result $chr(10) %line
        }
        set %i = $calc(%i + 1)
    }
    return %result
}

; Check SuperUsers
on TEXT:!superusers*:#:{
    set %total = $lines(superusers.txt)
    set %i = 1
    set %found = 0
    listclear @users
    
    while (%i <= %total) {
        set %line = $read(superusers.txt, %i)
        listadd @users %line
        set %i = $calc(%i + 1)
    }
    for (%superusers in @users) {
        msg $chan %superusers
    }
}

; Get a Users hostname
on TEXT:!gethostname*:#:{
    if ($2) {
        set %user = $2
        set %whois_nick = $whois(%user, nick)
        set %whois_host = $whois(%user, hostname)
        if (%whois_nick) {
            msg $chan %whois_host
        }
        else {
            msg $chan You must run !whois %user first
        }
    }
    else {
        msg $chan Usage: !gethostname <nickname>
    }
}

; Add Super Users
on TEXT:!add*:#:{
    if ($2) {
        set %user = $2
        set %whois_nick = $whois(%user, nick)
        set %whois_host = $whois(%user, hostname)
        if (%whois_nick) {
            write superusers.txt %whois_host
        }
    }
}

