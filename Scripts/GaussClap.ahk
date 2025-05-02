#Requires AutoHotkey v2.0
#SingleInstance Force

; @export
global castQueue := "ice-ice-fire"

; @export
global ability1 := "1"
; @export
global ability3 := "3"
; @export
global castDelay := 100
; @export
global checkKeyStateDelay := 100

global _array := StrSplit(castQueue, "-")

~XButton2:: {
    global castQueue, ability1, ability3, castDelay, _array, checkKeyStateDelay

    SendEvent "{ " ability1 " down}"

    while (GetKeyState("XButton2") == 1) {
        for index, element in _array {
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

    SendEvent ability1
}