// Gamepad button mapping fix for issue #2886
// This file contains corrected SDL gamepad button mappings

package armory.system;

/**
 * Gamepad button constants mapped to SDL game controller standard.
 * Fixes button mapping issues with PS3/PS4 controllers.
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
 */
class GamepadButton {
    // Face buttons (Xbox layout / PlayStation equivalent)
    public static inline var A:Int = 0;          // Cross (PS)
    public static inline var B:Int = 1;          // Circle (PS)
    public static inline var X:Int = 2;          // Square (PS)
    public static inline var Y:Int = 3;          // Triangle (PS)
    
    // PlayStation aliases
    public static inline var CROSS:Int = 0;
    public static inline var CIRCLE:Int = 1;
    public static inline var SQUARE:Int = 2;
    public static inline var TRIANGLE:Int = 3;
    
    // Menu buttons
    public static inline var BACK:Int = 4;       // Select/Share (PS)
    public static inline var GUIDE:Int = 5;      // Home/PS button
    public static inline var START:Int = 6;      // Start/Options (PS)
    
    // Stick buttons
    public static inline var LEFT_STICK:Int = 7;  // L3 (PS)
    public static inline var RIGHT_STICK:Int = 8; // R3 (PS)
    public static inline var L3:Int = 7;
    public static inline var R3:Int = 8;
    
    // Shoulder buttons
    public static inline var LEFT_SHOULDER:Int = 9;  // L1 (PS)
    public static inline var RIGHT_SHOULDER:Int = 10; // R1 (PS)
    public static inline var L1:Int = 9;
    public static inline var R1:Int = 10;
    
    // D-Pad
    public static inline var DPAD_UP:Int = 11;
    public static inline var DPAD_DOWN:Int = 12;
    public static inline var DPAD_LEFT:Int = 13;
    public static inline var DPAD_RIGHT:Int = 14;
}
