#Requires AutoHotkey v2.0
#SingleInstance Force

global interruptKey := "{Shift}"
global slamKey := "{XButton1}"
global jumpKey := "{Space}"

; @export
global jumpPressDuration := 100
; @export
global slamDelayDuration := 500

XButton2:: {
    global interruptKey, slamKey, jumpKey, jumpPressDuration, slamDelayDuration
    Send jumpKey
    Sleep jumpPressDuration
    SendEvent slamKey
    Sleep slamDelayDuration
    SendEvent interruptKey
}