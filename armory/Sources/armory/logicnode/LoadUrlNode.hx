// This node does not work with Krom. "Browser compilation only" node.

package armory.logicnode;

import kha.System;

class LoadUrlNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		//System.loadUrl(inputs[1].get());

		#if kha_html5
		if (inputs[2].get()){
			var window = inputs[3].get() ? js.Browser.window.open(inputs[1].get(), "_blank", "width="+inputs[4].get()+",height="+inputs[5].get()+",left="+inputs[6].get()+",top="+inputs[7].get())
			: js.Browser.window.open(inputs[1].get(), "_blank");
			
	    	if(window != null)
	    		runOutput(0);
	    	else
	    		runOutput(1);
		}
	    else	
			js.Browser.window.open(inputs[1].get(), "_self"); 
		#end
	}
}
