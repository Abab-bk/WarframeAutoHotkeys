#Requires AutoHotkey v2.0
#SingleInstance Force

; @export
global ability1 := "1"
; @export
global ability2 := "2"
; @export
global castDelay := 900

XButton2:: {
    global ability1, ability2, castDelay
    SendEvent ability2
    Sleep castDelay
    SendEvent ability1
}