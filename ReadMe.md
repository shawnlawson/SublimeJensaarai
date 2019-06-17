# Sublime Jensaarai

This plugin is for livecoding python, glsl, and Tidal Cycles.

## Dependencies
Install Package Control https://packagecontrol.io/installation first, then use it to install the following

Origami for pane/view management: https://packagecontrol.io/packages/Origami

Terminus for terminals in Sublime: https://packagecontrol.io/packages/Terminus


## Installation
1. Clone this directory to:

OSX
~/Library/Application Support/Sublime Text 3/Packages/

Win

Linux

2. Follow the directions in the CopyThese directory.

3. Probably restart Sublime Text for good measure.

4. If using Tidal, please follow those instructions: https://tidalcycles.org/index.php/Installation

## Using
The settings file sets which options to enable and disable on launch. Each part can also be started/stopped at runtime with a command. Edit this to set your tidal ghci path. 

## Running Code
Start each block of code with an identifier tag.

```python
//python
print('hello world')

//tidal
d1 $ sound "bd"

//glsl
out vec4 fragColor;
void main(){
    fragColor = vec4(1, 0, 0, 1);
}
```

Python/Tidal

Shift+Enter for single line executions

Command+Enter for block executions

GLSL auto executes.



