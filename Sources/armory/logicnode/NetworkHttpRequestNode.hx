package armory.logicnode;
import iron.object.Object;


class NetworkHttpRequestNode extends LogicNode {
    public var property0: String;
    public var statusInt: Int;
    public var response: Dynamic;

    public function new(tree:LogicTree) {
        super(tree);
    }

    override function run(from:Int) {
        var url = inputs[1].get();
        var request = new haxe.Http(url);

        request.onStatus = function(status) { 
            statusInt = status;
        }

        request.onData = function(data:String) {
            response = data;
        }

        request.onError = function(error:String){ 
            trace ("Error: " + error ); 
        }
        
        try {
            if(property0 == "post") {
                request.request(true);
            } else {
                request.request(false);
            }
        } catch( e : Dynamic ) {
            trace("Could not complete request: " + e);
        }

        runOutput(0);
        return;

    }

    override function get(from: Int): Dynamic {

        return switch (from) {
            case 1: statusInt;
            case 2: response;
            default: throw "Unreachable";
        }

    }
}

