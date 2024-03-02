package armory.logicnode;
import iron.object.Object;


class NetworkHttpRequestNode extends LogicNode {
    public var property0: String;
    public var callbackType: Int;
    public var statusInt: Int;
    public var response: Dynamic;
    public var errorOut: String;
    public var headers: Map<String,String>;
    public var parameters: Map<String,String>;

    public function new(tree:LogicTree) {
        super(tree);
    }

    override function run(from:Int) {

        var url = inputs[1].get();

        if(url == null){return;}

        headers = inputs[2].get();
        parameters = inputs[3].get();
        var printErrors: Bool = inputs[4].get();

        var request = new haxe.Http(url);
		#if js
        request.async = true;
		#end
        if(headers != null){
            for (k in headers.keys()) {
                request.addHeader( k, headers[k]);
            }
        }
        if(parameters != null){
            for (k in parameters.keys()) {
                request.addParameter( k, parameters[k]);
            }
        }

        request.onStatus = function(status:Int) { 
            callbackType = 1;
            statusInt = status;
            runOutput(0);
        }

        request.onBytes = function(data:haxe.io.Bytes) {
            callbackType = 2;
            response = data;
            runOutput(0);
        }

        request.onData = function(data:String) {
            callbackType = 3;
            response = data;
            runOutput(0);
        }

        request.onError = function(error:String){ 
            callbackType = 4;
            errorOut = error;
            if(printErrors) {
                trace ("Error: " + error );
            }
            runOutput(0);
        }
        
        try {
            if(property0 == "post") {
                var bytes = inputs[6].get();
                if(bytes == true){
                    var data:haxe.io.Bytes = inputs[5].get();
                    request.setPostBytes(data);
                    request.request(true);
                }else{
                    var data:Dynamic = inputs[5].get();
                    request.setPostData(data.toString());
                    request.request(true);
                }
            } else {
                request.request(false);
            }
        } catch( e : Dynamic ) {
            trace("Could not complete request: " + e);
        }

        callbackType = 0;
        runOutput(0);

    }

    override function get(from: Int): Dynamic {

        return switch (from) {
            case 1: callbackType;
            case 2: statusInt;
            case 3: response;
            case 4: errorOut;
            default: throw "Unreachable";
        }

    }
}
