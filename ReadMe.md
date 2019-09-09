# Sublime Jensaarai

This plug-in is for livecoding python, glsl, and Tidal Cycles.

## Dependencies
Install Package Control https://packagecontrol.io/installation first, then use it to install the following

Origami for pane/view management: https://packagecontrol.io/packages/Origami

Terminus for terminals in Sublime: https://packagecontrol.io/packages/Terminus


## Installation
1. Clone or unzip this directory to:

OSX
~/Library/Application Support/Sublime Text 3/Packages/

Win
%APPDATA%\Sublime Text 3\Packages

Linux
/opt/sublime_text/Packages

2. Follow the directions in the CopyThese directory.

3. Open the command palette 

OSX <kbd>SHIFT</kbd>+<kbd>COMMAND</kbd>+<kbd>P</kbd>

Win/Linux <kbd>SHIFT</kbd>+<kbd>CTRL</kbd>+<kbd>P</kbd>

start typing "Install" to bring up the option for "Package Control: Install Package", press enter to run this command. Then start typing "Terminus" to install the Terminus package. 

Once that's finished installing, open the command palette again and use package controll to install the "Origami" package. 

4. Probably restart Sublime Text for good measure.

5. If using Tidal and it's not installed, please follow those instructions: https://tidalcycles.org/index.php/Installation


## Using
The settings file sets which options to enable and disable on launch. Each part can also be started/stopped at runtime with a command. Use the menu option "Sublime Text->Preferences->Package Settings->Sublime Jensaarai->Settings - Default" to see settings in json format. Same menu option to with "Settings - User" at the end to override with your settings. 

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

<kbd>SHIFT</kbd>+<kbd>RETURN</kbd> for single line executions

<kbd>CTRL</kbd>+<kbd>RETURN</kbd> or <kbd>COMMAND</kbd>+<kbd>RETURN</kbd> for block executions

GLSL auto executes.

## Saving and Playing Back Text Recordings



## Miscellaneous

The src_files folder includes files needed to create the syntaxes used by this plug-in. Use YAML Macros https://packagecontrol.io/packages/YAMLMacros to change and then build these files. Results found in syntaxes folder. 



