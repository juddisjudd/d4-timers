# D4 Timers
Small tool to display Helltide and World Boss timers (data from helltides.com).

## How to use
- [Download latest version](https://github.com/juddisjudd/d4-timers/releases/download/1.0/D4TimersOverlay.exe)
- Double click on **D4TimersOverlay.exe**
- Drag anywhere on your screen.
- **ctrl + q to close** (must click on it first however)

## PREVIEW
![](https://i.imgur.com/lWtmSDk.jpeg)

## Requirements
- [PT Serif](https://fonts.google.com/specimen/PT+Serif) font (*will not display like it does in screenshot without the font*)
- [pytz](https://pypi.org/project/pytz/)
- [tkinter](https://docs.python.org/3/library/tkinter.html)
- [requests](https://pypi.org/project/requests/)

## OBS version for streamers
[Youtube Video](https://www.youtube.com/watch?v=n3WDgsLDjLY)

**URL for Browser Source in OBS:**
> https://d4-timers.juddisjudd.repl.co/

**Example Custom CSS for Browser Source:**
```
body {
    background-color: rgba(0, 0, 0, 0.8);
    font-size: 24px;
}

#bossName {
    color: #f1c40f;
}
```
## Disclaimer
Some Anti-Virus software may detect this as malicious, this is a false positive. (you can check the code yourself)

## Credit
Timers provided by helltides.com
