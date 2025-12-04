
; Test script with new features
on TEXT:!test*:#:{
    ; File I/O test
    write test_output.txt Test line from script
    
    ; Math test
    set %result = $calc(5 + 3)
    msg $chan Math result: %result
    
    ; String test
    set %upper = $upper(hello)
    msg $chan Uppercase: %upper
    
    ; Token test
    set %token = $gettok(a,b,c, 2, 44)
    msg $chan Middle token: %token
}
