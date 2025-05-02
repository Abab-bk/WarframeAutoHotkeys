#Requires AutoHotkey v2.0
#SingleInstance Force

; need invert protea control.

SetKeyDelay 100, 100

; protea 4 ability duration
; @export
global duration := 9500
; @export
global useDoubleAbility2 := false
; @export
global ability2Duration := 3200

; @export
global castInterval := 900

; @export
global ability4 := "4"
; @export
global ability2 := "2"

global _isRunning := false

#UseHook true

XButton2::
{
    global _isRunning, duration

    if (_isRunning) {
        Close()
        _isRunning := false
        ToolTip ""
        return
    }

    _isRunning := true
    Cast()
    SetTimer(OnTimeOut, -duration)
}

Close() {
    global ability4
    SendEvent ability4
    ToolTip "Close!", 50, 50
}

Cast() {
    global ability4, ability2, ability2Duration, useDoubleAbility2, castInterval
    SendEvent ability4
    Sleep castInterval
    SendEvent ability2

    if (useDoubleAbility2) {
        Sleep ability2Duration
        SendEvent ability2
        ToolTip "Double Cast!", 50, 50
    } else {
        ToolTip "Cast!", 50, 50
    }
}

OnTimeOut() {
    global _isRunning
    Close()
    _isRunning := false
    ToolTip ""
}