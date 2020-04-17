package armory.logicnode;

import zui.Canvas.Anchor;
import iron.Scene;
import armory.trait.internal.CanvasScript;

class OnCanvasElementNode extends LogicNode {

	var canvas: CanvasScript;
	var element: String;
	
	public var property0: String;
	public var property1: String;

	public function new(tree: LogicTree) {
		super(tree);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
	}

#if arm_ui
	function update() {

		element = inputs[0].get();		

		if(!Scene.active.ready) return;
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);
		if(canvas == null) return;
		if (!canvas.ready) return;
		if(canvas.getElement(element) == null) return;

		var mouse = iron.system.Input.getMouse();
		var b = false;
		switch (property0) {
		case "Down":
			b = mouse.down(property1);
		case "Started":
			b = mouse.started(property1);
		case "Released":
			b = mouse.released(property1);
		}
		if (b) 
		{
			
			var x1 = canvas.getElement(element).x;
			var y1 = canvas.getElement(element).y;
			var anchor = canvas.getElement(element).anchor;
			var cx = canvas.getCanvas().width;
			var cy = canvas.getCanvas().height;
			var mouseX = mouse.x;
			var mouseY = mouse.y;
			var x2 = x1 + canvas.getElement(element).width;
			var y2 = y1 + canvas.getElement(element).height;

			switch(anchor)
			{
				case Top:
					mouseX -= cx/2 - canvas.getElement(element).width/2;
				case TopRight:
					mouseX -= cx - canvas.getElement(element).width;
				case CenterLeft:
					mouseY -= cy/2 - canvas.getElement(element).height/2;
				case Anchor.Center:
					mouseX -= cx/2 - canvas.getElement(element).width/2;
					mouseY -= cy/2 - canvas.getElement(element).height/2;
				case CenterRight:
					mouseX -= cx - canvas.getElement(element).width;
					mouseY -= cy/2 - canvas.getElement(element).height/2;
				case BottomLeft:
					mouseY -= cy - canvas.getElement(element).height;
				case Bottom:
					mouseX -= cx/2 - canvas.getElement(element).width/2;
					mouseY -= cy - canvas.getElement(element).height;
				case BottomRight:
					mouseX -= cx - canvas.getElement(element).width;
					mouseY -= cy - canvas.getElement(element).height;
			}
			
			if((mouseX >= x1) && (mouseX <= x2))
			{
				if((mouseY >= y1) && (mouseY <= y2))
				{
					runOutput(0);
				}
			}
		}
	}
#end
}
