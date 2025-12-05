; Sleep Function Demo
; Shows how to use the sleep command to add delays between actions

; !countdown - counts down from 5 with delays
on TEXT:!countdown:#:{
    msg $chan Starting countdown...
    sleep 5
    msg $chan 5...
    sleep 1
    msg $chan 4...
    sleep 1
    msg $chan 3...
    sleep 1
    msg $chan 2...
    sleep 1
    msg $chan 1...
    sleep 1
    msg $chan GO! 🚀
}

; !slowecho - echoes words one at a time with delays
on TEXT:!slowecho*:#:{
    msg $chan Echoing slowly: $2-
    sleep 0.5
    msg $chan Word 1: $2
    sleep 0.5
    msg $chan Word 2: $3
    sleep 0.5
    msg $chan Word 3: $4
    sleep 0.5
    msg $chan Done!
}

; !spam - shows how to delay between messages (anti-flood)
on TEXT:!spam:#:{
    msg $chan Message 1
    sleep 2
    msg $chan Message 2
    sleep 2
    msg $chan Message 3
}

