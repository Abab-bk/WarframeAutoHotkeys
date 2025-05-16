#Requires AutoHotkey v2.0
#SingleInstance Force

; @export
global castQueue := "ice-ice-fire"

; @export
global castQueue2 := "fire-fire-ice"

; @export
global ability1 := "1"
; @export
global ability3 := "3"
; @export
global castDelay := 200
; @export
global checkKeyStateDelay := 200

global _enabledAbility1 := true
global _castQueue2 := false

global _array := StrSplit(castQueue, "-")
global _array2 := StrSplit(castQueue2, "-")

~o:: {
    global _enabledAbility1
    _enabledAbility1 := !_enabledAbility1
    ToolTip("EnabledAbility1: {" _enabledAbility1 "} ", 50, 50)
    SetTimer(ToolTip, 1000)
}

~l:: {
    global _castQueue2
    _castQueue2 := !_castQueue2
    ToolTip("Enabled CastQueue2: {" _castQueue2 "} ", 50, 50)
    SetTimer(ToolTip, 1000)
}

~XButton2:: {
    global ability1, ability3, castDelay, _array, _array2, checkKeyStateDelay, _enabledAbility1

    _castArray := _enabledAbility1 ? _array : _array2

    if (_enabledAbility1) {
        SendEvent "{ " ability1 " down}"        
    }

    while (GetKeyState("XButton2") == 1) {
        for index, element in _castArray {
            if !GetKeyState("XButton2")
                break 2

            if (element == "ice") {
                SendEvent "{ " ability3 " down}"
                Sleep 300
                SendEvent "{ " ability3 " up}"
            }
            else if element == "fire"
                SendEvent ability3

            Sleep castDelay
        }
        Sleep checkKeyStateDelay
    }

    if (_enabledAbility1) {
        SendEvent ability1
    }
}