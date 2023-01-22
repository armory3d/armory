package armory.logicnode;
import armory.network.Connect;
import iron.object.Object;


class NetworkHostNode extends LogicNode {
      public var property0: Bool;
      public var net_Url: String;

      public function new(tree:LogicTree) {
        super(tree);
      }

      override function run(from:Int) {
      #if sys
        if(property0 == false) {
          final net_Object: Object = tree.object;
          var net_Domain: String = inputs[1].get();
          var net_Port: Int = inputs[2].get();
          var max_Conn: Int = inputs[3].get();
          net_Url = "ws://" + net_Domain + ":" + net_Port;
          if (Host.connections[net_Url] != null) return;
          try{
            var server = new Host(net_Domain, net_Port, max_Conn, net_Object);
            if (Host.connections[net_Url] == null) return;
            Host.connections[net_Url].start();
            runOutput(0);
          } catch(err){
            trace("Failed to start server with the following error: " + err + ". Check if there is a system process occupying the port.");
          }
        } else {
          final net_Object: Object = tree.object;
          var net_Domain: String = inputs[1].get();
          var net_Port: Int = inputs[2].get();
          var max_Conn: Int = inputs[3].get();
          var net_Cert: String = inputs[4].get();
          var net_Key: String = inputs[5].get();
          net_Url = "wss://" + net_Domain + ":" + net_Port;
          if (SecureHost.connections[net_Url] != null) return;
          try{
            var server = new SecureHost(net_Domain, net_Port, max_Conn, net_Object, net_Cert, net_Key);
            if (SecureHost.connections[net_Url] == null) return;
            SecureHost.connections[net_Url].start();
            runOutput(0);
          } catch(err){
            trace("Failed to start server with the following error: " + err + ". Check if there is a system process occupying the port.");
          }
        }
        #end
      }

      #if sys
      override function get(from: Int): Dynamic {
        if(property0 == false) { 
          return switch (from) {
              case 1: Host.connections[net_Url];
              case 2: Host.data[net_Url];
              default: throw "Unreachable";
          }
        } else {
          return switch (from) {
              case 1: SecureHost.connections[net_Url];
              case 2: SecureHost.data[net_Url];
              default: throw "Unreachable";
          }
        }
      }
      #end
}

