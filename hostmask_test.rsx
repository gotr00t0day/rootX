; ============================================
; Hostmask Test Script
; ============================================
;
; Test the new $address, $user, and $host identifiers
;
; ============================================

; Show hostmask info
on TEXT:!whoami:#:{
    msg $chan === Your Info ===
    msg $chan Nick: $nick
    msg $chan Address: $address
    msg $chan User: $user
    msg $chan Host: $host
    msg $chan IP: $ip
}

; Log joins with full hostmask
on JOIN:#:{
    write joins.txt [$date $time] $nick ($address) joined $chan
    msg $chan Welcome $nick! (from $host)
}

; Ban by hostmask example (ops only)
on TEXT:!hostban*:#:{
    if ($islevel($nick,100) == True) {
        if ($2) {
            msg $chan Would ban: *!*@$host of $2
            ; In real use: ban $chan *!*@$host
        }
    }
}

; Check for specific ISP and log with IP
on TEXT:*:#:{
    if (comcast isin $host) {
        ; Log comcast users with their IP
        write comcast_users.txt [$time] $nick from $ip ($host)
    }
}

; Block specific IP range (example: block 73.244.*.*)
; DISABLED - This is just an example
; on TEXT:*:#:{
;     if (73.244 isin $ip) {
;         msg $chan $nick Your IP range is blocked!
;         halt
;     }
; }

; Extract IP from any text
on TEXT:!extractip*:#:{
    if ($2-) {
        set %extracted = $ip($2-)
        if (%extracted) {
            msg $chan Extracted IP: %extracted
        }
        else {
            msg $chan No IP found in: $2-
        }
    }
}

