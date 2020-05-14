package armory.logicnode;

import armory.trait.internal.CanvasScript;
import iron.Scene;

#if arm_ui
import zui.Canvas.Anchor;
#end

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
		if(canvas.getElement(element).visible == false) return;
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
			var canvasElem = canvas.getElement(element);
			var left = canvasElem.x;
			var top = canvasElem.y;
			var right = left + canvasElem.width;
			var bottom = top + canvasElem.height;

			var anchor = canvasElem.anchor;
			var cx = canvas.getCanvas().width;
			var cy = canvas.getCanvas().height;
			var mouseX = mouse.x;
			var mouseY = mouse.y;

			switch(anchor)
			{
				case Top:
					mouseX -= cx/2 - canvasElem.width/2;
				case TopRight:
					mouseX -= cx - canvasElem.width;
				case CenterLeft:
					mouseY -= cy/2 - canvasElem.height/2;
				case Anchor.Center:
					mouseX -= cx/2 - canvasElem.width/2;
					mouseY -= cy/2 - canvasElem.height/2;
				case CenterRight:
					mouseX -= cx - canvasElem.width;
					mouseY -= cy/2 - canvasElem.height/2;
				case BottomLeft:
					mouseY -= cy - canvasElem.height;
				case Bottom:
					mouseX -= cx/2 - canvasElem.width/2;
					mouseY -= cy - canvasElem.height;
				case BottomRight:
					mouseX -= cx - canvasElem.width;
					mouseY -= cy - canvasElem.height;
			}

			if((mouseX >= left) && (mouseX <= right))
			{
				if((mouseY >= top) && (mouseY <= bottom))
				{
					runOutput(0);
				}
			}
		}
	}
	#else
	function update() {}
	#end
}
