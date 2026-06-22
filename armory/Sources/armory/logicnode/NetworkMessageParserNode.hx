package armory.logicnode;
import armory.network.Connect;
import armory.network.Buffer;
import haxe.io.Bytes;
import iron.object.Object;
import iron.math.Vec4;
import iron.math.Quat;
import iron.math.Mat4;


class NetworkMessageParserNode extends LogicNode {
    public var property0: String;
    public var api: String;
    public var parsed: Dynamic;

    public function new(tree:LogicTree) {
        super(tree);
    }

    override function run(from:Int) {
        var data: Dynamic = inputs[2].get();
        if (data == null) return;

        var buffer = cast(data, Buffer);
        api = inputs[1].get();
        if(buffer.endsWith(api) == false){
            return;
        }

        switch (property0) {
            case "string":   
                var bytes = buffer.readAllAvailableBytes();
                parsed = bytes.toString().substr(0, bytes.length - api.length);
                runOutput(0);
            case "vector":   
                var bytes = new haxe.io.BytesInput(buffer.readUntil(api));
                var vec = new Vec4();
                for (f in Reflect.fields(vec)) {
                    Reflect.setField(vec, f, bytes.readFloat());
                }
                parsed = vec;
                runOutput(0);
            case "float":    
                var bytes = new haxe.io.BytesInput(buffer.readUntil(api));
                var float: Float = bytes.readFloat();
                parsed = float;
                runOutput(0);
            case "integer":  
                var bytes = new haxe.io.BytesInput(buffer.readUntil(api));
                var integer: Int = bytes.readInt32();
                parsed = integer;
                runOutput(0);
            case "boolean":  
                var bytes = buffer.readAllAvailableBytes();
                var boolean = bytes.toString().substr(0, bytes.length - api.length);
                if(boolean == "true"){
                    parsed = true;
                } else {
                    parsed = false;
                }
                runOutput(0);
            case "transform":
                var bytes = new haxe.io.BytesInput(buffer.readUntil(api));
                var loc: Vec4 = new Vec4();
                var rot: Quat = new Quat();
                var scl: Vec4 = new Vec4();
                for (f in Reflect.fields(loc)) {
                    Reflect.setField(loc, f, bytes.readFloat());
                }
                for (f in Reflect.fields(rot)) {
                    Reflect.setField(rot, f, bytes.readFloat());
                }
                for (f in Reflect.fields(scl)) {
                    Reflect.setField(scl, f, bytes.readFloat());
                }
                var transform = Mat4.identity();   
                parsed = transform.compose(loc, rot, scl);
                runOutput(0);
            case "rotation": 
                var bytes = new haxe.io.BytesInput(buffer.readUntil(api));
                var rot = new Quat();
                for (f in Reflect.fields(rot)) {
                    Reflect.setField(rot, f, bytes.readFloat());
                }
                parsed = rot;
                runOutput(0);
            default: throw "Failed to parse data.";
        }

    }

    override function get(from: Int): Dynamic {
        return switch (from) {
          case 1: api;
          case 2: parsed;
          default: throw "Unreachable";
        }
    }

}
