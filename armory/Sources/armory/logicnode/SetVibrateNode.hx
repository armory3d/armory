// Pulses the vibration hardware on the device for time in milliseconds, if such hardware exists.

package armory.logicnode;
import kha.System;

class SetVibrateNode extends LogicNode {

    public function new(tree: LogicTree) {
        super(tree);
    }

    override function run(from: Int) {
        if (inputs[1].get() > 0) System.vibrate(inputs[1].get());
        runOutput(0);
    }
}
