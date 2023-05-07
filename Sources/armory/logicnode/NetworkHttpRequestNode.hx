package armory.logicnode;
import iron.object.Object;


class NetworkHttpRequestNode extends LogicNode {
    public var property0: String;
    public var statusInt: Int;
    public var response: Dynamic;
    public var headers: Map<String,String>;
    public var parameters: Map<String,String>;

    public function new(tree:LogicTree) {
        super(tree);
    }

    override function run(from:Int) {

        var url = inputs[1].get();

        if(url == null){return;}
        if(property0 == "post") {
            headers = inputs[4].get();
            parameters = inputs[5].get();
        }else{
            headers = inputs[2].get();
            parameters = inputs[3].get();
        }

        var request = new haxe.Http(url);

        request.async = true;

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
            statusInt = status;
            runOutput(0);
        }

        request.onBytes = function(data:haxe.io.Bytes) {
            response = data;
            runOutput(0);
        }

        request.onData = function(data:String) {
            response = data;
            runOutput(0);
        }

        request.onError = function(error:String){ 
            trace ("Error: " + error ); 
            runOutput(0);
        }
        
        try {
            if(property0 == "post") {
                var bytes = inputs[2].get();
                if(bytes == true){
                    var data:haxe.io.Bytes = inputs[3].get();
                    request.setPostBytes(data);
                    request.request(true);
                }else{
                    var data:Dynamic = inputs[3].get();
                    request.setPostData(data.toString());
                    request.request(true);
                }
            } else {
                request.request(false);
            }
        } catch( e : Dynamic ) {
            trace("Could not complete request: " + e);
        }

    }

    override function get(from: Int): Dynamic {

        return switch (from) {
            case 1: statusInt;
            case 2: response;
            default: throw "Unreachable";
        }

    }
}
