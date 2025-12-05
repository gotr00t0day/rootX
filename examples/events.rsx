; ============================================
; Custom events 
; ============================================
;
; Description: This script customizes server events
; Author: c0d3Ninja
;
; ============================================

on TEXT:*:#:{
    if ($nick != $me) {
        ; Initialize bad words list once
        if ($list(@badwords,count) == 0) {
            listadd @badwords fuck
            listadd @badwords pussy
            listadd @badwords bitch
            listadd @badwords fag
        }
        
        ; Check for bad words
        for (%badword in @badwords) {
            if (%badword isin $text) {
                msg $chan $nick You cant say that word!
                halt
            }
        }
    }
}