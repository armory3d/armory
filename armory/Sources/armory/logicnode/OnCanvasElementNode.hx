package armory.logicnode;

import armory.trait.internal.CanvasScript;
import iron.Scene;

#if arm_ui
import armory.ui.Canvas.Anchor;
#end

class OnCanvasElementNode extends LogicNode {

	var canvas: CanvasScript;
	var element: String;

	/**
	 * The event type this node should react to, can be "click" or "hover".
	 */
	public var property0: String;
	/**
	 * If the event type is click, this property states whether to check for
	 * "down", "started" or "released" events.
	 */
	public var property1: String;
	/**
	 * The mouse button that this node should react to. Only used when listening
	 * for mouse clicks.
	 */
	public var property2: String;

	public function new(tree: LogicTree) {
		super(tree);

		tree.notifyOnUpdate(update);
	}

	#if arm_ui
	function update() {
		element = inputs[0].get();

		// Ensure canvas is ready
		if(!Scene.active.ready) return;
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);
		if(canvas == null) return;
		if (!canvas.ready) return;
		if(canvas.getElement(element) == null) return;
		if(canvas.getElement(element).visible == false) return;
		var mouse = iron.system.Input.getMouse();
		var isEvent = false;

		if (property0 == "click") {
			switch (property1) {
			case "started":
				isEvent = mouse.started(property2);
			case "down":
				isEvent = mouse.down(property2);
			case "released":
				isEvent = mouse.released(property2);
			}
		}
		// Hovered
		else {
			isEvent = true;
		}

		if (isEvent)
		{
			var canvasElem = canvas.getElement(element);
			var left = canvasElem.x*canvas.getUiScale();
			var top = canvasElem.y*canvas.getUiScale();
			var right = left + canvasElem.width*canvas.getUiScale();
			var bottom = top + canvasElem.height*canvas.getUiScale();

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
