package armory.logicnode;

import kravex.input.Gamepad;

/**
 * Maps button string names from Blender UI to SDL gamepad button indices.
 * Fixes issue #2886 with incorrect PS3/PS4 controller button mappings.
 */
class GamepadCoordsNode {

    /**
     * Converts button name string to SDL gamepad button index.
     * 
     * SDL Game Controller Button Mapping:
     * - A (cross) = 0
     * - B (circle) = 1
     * - X (square) = 2
     * - Y (triangle) = 3
     * - Back/Select = 4
     * - Guide/Home = 5
     * - Start = 6
     * - Left Stick (L3) = 7
     * - Right Stick (R3) = 8
     * - Left Shoulder (L1) = 9
     * - Right Shoulder (R1) = 10
     * - D-Pad Up = 11
     * - D-Pad Down = 12
     * - D-Pad Left = 13
     * - D-Pad Right = 14
     * - Touchpad = 15
     */
    public static function buttonIndex(button:String):Int {
        return switch (button) {
            case "cross": 0;
            case "circle": 1;
            case "square": 2;
            case "triangle": 3;
            case "l1": 9;
            case "r1": 10;
            case "l2": -1;  // Trigger axis, not a button
            case "r2": -1;  // Trigger axis, not a button
            case "share": 4;
            case "options": 6;
            case "l3": 7;
            case "r3": 8;
            case "home": 5;
            case "touchpad": 15;
            case "dpad_up": 11;
            case "dpad_down": 12;
            case "dpad_left": 13;
            case "dpad_right": 14;
            default: -1;
        };
    }
}
