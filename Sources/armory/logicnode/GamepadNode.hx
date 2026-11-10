package armory.logicnode;

import kravex.input.Gamepad;

/**
 * Gamepad logic node with corrected button mappings.
 * Fixes issue #2886 where PS3/PS4 controller buttons were mapped incorrectly.
 * 
 * SDL Game Controller Button Mapping (standard):
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
class GamepadNode extends LogicNode {

    /**
     * Maps the logic node button index to the correct SDL gamepad button.
     * This fixes the button mapping issues reported in #2886.
     * 
     * Blender UI order -> SDL button mapping:
     * 0: cross (A) -> 0
     * 1: circle (B) -> 1
     * 2: square (X) -> 2
     * 3: triangle (Y) -> 3
     * 4: l1 -> 9
     * 5: r1 -> 10
     * 6: l2 -> axis (not a button)
     * 7: r2 -> axis (not a button)
     * 8: share/select -> 4
     * 9: options/start -> 6
     * 10: l3 -> 7
     * 11: r3 -> 8
     * 12: home/guide -> 5
     * 13: touchpad -> 15 (if available)
     * 14: dpad up -> 11
     * 15: dpad down -> 12
     * 16: dpad left -> 13
     * 17: dpad right -> 14
     */
    public static function mapButton(buttonIndex:Int):Int {
        return switch (buttonIndex) {
            case 0: 0;   // cross/A
            case 1: 1;   // circle/B
            case 2: 2;   // square/X
            case 3: 3;   // triangle/Y
            case 4: 9;   // l1/left shoulder
            case 5: 10;  // r1/right shoulder
            case 6: -1;  // l2 (axis, not button)
            case 7: -1;  // r2 (axis, not button)
            case 8: 4;   // share/select/back
            case 9: 6;   // options/start
            case 10: 7;  // l3/left stick
            case 11: 8;  // r3/right stick
            case 12: 5;  // home/guide/PS button
            case 13: 15; // touchpad (PS4)
            case 14: 11; // dpad up
            case 15: 12; // dpad down
            case 16: 13; // dpad left
            case 17: 14; // dpad right
            default: buttonIndex;
        };
    }

    public function new(tree:LogicTree) {
        super(tree);
    }
}
