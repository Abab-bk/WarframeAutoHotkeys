#Requires AutoHotkey v2.0

; @export
global pressKey := "2"

; @export
global interval := 5000

toggle := false

~o:: {
    global toggle
    global interval
    toggle := !toggle
    
    if toggle {
        SetTimer(Press, interval)
        ToolTip "AutoShoot was started, press O to stop."
    } else {
        SetTimer(Press, 0)
        ToolTip "AutoShoot was stopped."
    }
    
    SetTimer(() => ToolTip(), -1000)
}

Press() {
    global pressKey
    SendEvent pressKey
}

ToolTip "Press O to auto press."
SetTimer(() => ToolTip(), -2000)  ; 2秒后自动消失