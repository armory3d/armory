# Fix for Issue #2886: [$100 Bounty] perfectly ( normal ) working gamepad logic nodes on pc and android phone

CONFIDENCE: 0.75

SOLUTION_SUMMARY: Implement a comprehensive gamepad input abstraction layer that normalizes controller input across PC and Android platforms, fixing button mapping inconsistencies, standardizing axis handling, and ensuring consistent behavior for PS3/PS4/generic controllers through a unified SDL-based mapping system.

FILES_CHANGED:
- Sources/armory/logicnode/GamepadNode.hx
- Sources/armory/logicnode/GamepadCoordsNode.hx
- Sources/armory/system/InputMap.hx
- Sources/armory/system/GamepadInput.hx
- Sources/armory/logicnode/OnGamepadNode.hx
- Sources/armory/logicnode/GamepadStateNode.hx
- blender/arm/logicnode/input/LN_gamepad.py
- blender/arm/logicnode/input/LN_on_gamepad.py
- blender/arm/logicnode/input/LN_gamepad_coords.py
- blender/arm/logicnode/input/LN_gamepad_state.py

CODE:
```haxe
// Sources/armory/system/GamepadInput.hx
package armory.system;

import kha.input.Gamepad;

/**
 * Cross-platform gamepad input handler that normalizes controller input
 * across PC (Windows/Linux/macOS) and Android platforms.
 * 
 * Supports:
 * - PlayStation 3/4/5 controllers
 * - Xbox 360/One/Series controllers
 * - Generic USB/Bluetooth gamepads
 * - Android native gamepad API
 */
class GamepadInput {
    
    // Standardized button indices (SDL GameController mapping)
    public static inline var BUTTON_A:Int = 0;
    public static inline var BUTTON_B:Int = 1;
    public static inline var BUTTON_X:Int = 2;
    public static inline var BUTTON_Y:Int = 3;
    public static inline var BUTTON_LB:Int = 4;  // Left bumper
    public static inline var BUTTON_RB:Int = 5;  // Right bumper
    public static inline var BUTTON_BACK:Int = 6;
    public static inline var BUTTON_START:Int = 7;
    public static inline var BUTTON_GUIDE:Int = 8;  // PS/Xbox button
    public static inline var BUTTON_LS:Int = 9;  // Left stick press
    public static inline var BUTTON_RS:Int = 10; // Right stick press
    public static inline var BUTTON_DPAD_UP:Int = 11;
    public static inline var BUTTON_DPAD_DOWN:Int = 12;
    public static inline var BUTTON_DPAD_LEFT:Int = 13;
    public static inline var BUTTON_DPAD_RIGHT:Int = 14;
    public static inline var BUTTON_LT:Int = 15; // Left trigger as button
    public static inline var BUTTON_RT:Int = 16; // Right trigger as button
    
    // Standardized axis indices
    public static inline var AXIS_LEFT_X:Int = 0;
    public static inline var AXIS_LEFT_Y:Int = 1;
    public static inline var AXIS_RIGHT_X:Int = 2;
    public stat