; ========================================
; SpyLog PRO v2.0
; ========================================
;
; Description: Advanced IRC logging and monitoring system
; Author: c0d3Ninja
; Features: Chat logs, IP tracking, departures, kicks, nicks,
;           topics, modes, keyword alerts, clone detection
;
; ========================================

; === MAIN LOGGING ===

; Log all channel messages
on TEXT:*:#:{
    if ($nick != $me) {
        %datelog = logs/chat_ $+ $date(yyyy-mm-dd) $+ .txt
        write %datelog [$time] [$chan] $nick ($address): $text
        
        ; Count user activity
        %%msg_count. $+ $nick = $calc(%%msg_count. $+ $nick + 1)
    }
}

; === JOIN/PART TRACKING ===

; Log joins and collect IPs
on JOIN:*:#:{
    if ($nick != $me) {
        write logs/joins.txt [$time] $nick joined $chan ($address)
        
        ; Log IP if available
        if ($ip) {
            ; Check for clones (same IP, different nick)
            if ($read(logs/ips.txt, w, *$ip*)) {
                write logs/clones.txt [$time] CLONE ALERT: $nick from $ip in $chan
            }
            write logs/ips.txt [$time] $nick | IP: $ip | Host: $host | Address: $address
        }
        
        ; Track rapid joins (possible flood/bot)
        %%join_count. $+ $address = $calc(%%join_count. $+ $address + 1)
        if (%%join_count. $+ $address > 5) {
            write logs/suspicious.txt [$time] FLOOD ALERT: $nick ($address) joined $chan (total: %%join_count. $+ $address)
        }
    }
}

; Log parts
on PART:*:#:{
    write logs/parts.txt [$time] $nick left $chan ($address) - $text
}

; Log quits
on QUIT:*:{
    write logs/quits.txt [$time] $nick quit IRC ($address) - $text
}

; === CHANNEL EVENTS ===

; Log kicks
on KICK:#:{
    write logs/kicks.txt [$time] $knick kicked $nick from $chan: $text
    write logs/moderation.txt [$time] KICK: $knick -> $nick in $chan: $text
}

; Log topic changes
on TOPIC:#:{
    write logs/topics.txt [$time] $nick changed topic in $chan to: $text
}

; Log mode changes
on MODE:#:{
    write logs/modes.txt [$time] $nick set mode $mode in $chan
    write logs/moderation.txt [$time] MODE: $nick set $mode in $chan
}

; Track nick changes
on NICK:{
    write logs/nicks.txt [$time] $nick changed nick to $newnick ($address)
}

; === KEYWORD MONITORING ===

; Alert on suspicious keywords
on TEXT:*:#:{
    %keywords = password,hack,admin,root,exploit,ddos,dox,leak
    %found = 0
    %i = 1
    
    while (%i <= $numtok(%keywords, 44)) {
        %keyword = $gettok(%keywords, %i, 44)
        if ($pos($text, %keyword)) {
            write logs/alerts.txt [$time] KEYWORD "$keyword" in $chan - $nick: $text
            %found = 1
        }
        %i = $calc(%i + 1)
    }
}

; === PRIVATE MESSAGE LOGGING ===

; Log incoming PMs
on TEXT:*:?:{
    write logs/pm_received.txt [$time] PM from $nick ($address): $text
}

; === ACTION LOGGING ===

; Log /me actions
on ACTION:*:#:{
    write logs/actions.txt [$time] [$chan] * $nick $text
}

; === COMMANDS ===

; View statistics
alias /spystats {
    echo -a ===================================
    echo -a         SpyLog PRO Stats
    echo -a ===================================
    echo -a Chat messages: $lines(logs/chat_ $+ $date(yyyy-mm-dd) $+ .txt)
    echo -a Unique IPs: $lines(logs/ips.txt)
    echo -a Joins today: $lines(logs/joins.txt)
    echo -a Parts today: $lines(logs/parts.txt)
    echo -a Quits today: $lines(logs/quits.txt)
    echo -a Kicks: $lines(logs/kicks.txt)
    echo -a Nick changes: $lines(logs/nicks.txt)
    echo -a Alerts: $lines(logs/alerts.txt)
    echo -a Clones detected: $lines(logs/clones.txt)
    echo -a ===================================
}

; Search logs for a keyword
alias /spysearch {
    if ($1) {
        echo -a Searching logs for: $1
        ; Note: Basic search - would need to read file line by line
        echo -a Found in chat log: $read(logs/chat_ $+ $date(yyyy-mm-dd) $+ .txt, w, *$1*)
    }
    else {
        echo -a Usage: /spysearch <keyword>
    }
}

; Show recent activity
alias /spyrecent {
    echo -a === Recent Activity (Last 5) ===
    %i = $calc($lines(logs/joins.txt) - 4)
    %end = $lines(logs/joins.txt)
    
    while (%i <= %end && %i > 0) {
        echo -a $read(logs/joins.txt, %i)
        %i = $calc(%i + 1)
    }
}

; Check if user has been seen
alias /spyseen {
    if ($1) {
        %result = $read(logs/ips.txt, w, *$1*)
        if (%result) {
            echo -a User found: %result
        }
        else {
            echo -a User $1 not found in logs.
        }
    }
    else {
        echo -a Usage: /spyseen <nick>
    }
}

; Clear old logs (use with caution!)
alias /spyclean {
    echo -a Are you sure you want to clear logs?
    echo -a Type /spyclean_confirm to proceed.
}

alias /spyclean_confirm {
    remove logs/joins.txt
    remove logs/parts.txt
    remove logs/quits.txt
    remove logs/kicks.txt
    remove logs/nicks.txt
    remove logs/topics.txt
    remove logs/modes.txt
    remove logs/suspicious.txt
    remove logs/alerts.txt
    echo -a Logs cleared! (IPs and chat logs preserved)
}

; === STARTUP ===

on LOAD:{
    echo -a ===================================
    echo -a     SpyLog PRO v2.0 Loaded
    echo -a ===================================
    echo -a Commands:
    echo -a   /spystats  - View statistics
    echo -a   /spysearch <word> - Search logs
    echo -a   /spyrecent - Recent joins
    echo -a   /spyseen <nick> - Check if seen
    echo -a   /spyclean  - Clear old logs
    echo -a ===================================
    echo -a All logs saved to logs/ directory
    echo -a ===================================
}

