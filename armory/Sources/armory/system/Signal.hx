package armory.system;

import haxe.Constraints.Function;

class Signal {
    var callbacks: Array<Function> = [];

    public function new() {

    }

    public function connect(callback: Function) {
        if (!callbacks.contains(callback)) callbacks.push(callback);
    }

    public function disconnect(callback: Function) {
        if (callbacks.contains(callback)) callbacks.remove(callback);
    }

    public function emit(...args: Any) {
        var callbacksCopy: Array<Function> = callbacks.copy();
        for (callback in callbacksCopy) {
            if (!callbacks.contains(callback)) continue;
            Reflect.callMethod(this, callback, args);
        }
    }

    public function getConnections(): Array<Function> {
        return callbacks;
    }

    public function isConnected(callBack: Function): Bool {
        return callbacks.contains(callBack);
    }

    public function isNull(): Bool {
        return callbacks.length == 0;
    }
}
