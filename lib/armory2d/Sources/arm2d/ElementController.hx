package arm2d;

// Kha
import kha.math.Vector2;
import kha.input.KeyCode;
import kha.graphics2.Graphics;
using kha.graphics2.GraphicsExtension;

// Zui
import zui.Zui;
import armory.ui.Canvas;

// Editor
import arm2d.tools.Math;
import arm2d.ui.UIProperties;
import arm2d.tools.CanvasTools;

class ElementController {

	static var ui:Zui;
	static var cui:Zui;

	public static var isManipulating = false;
	static var transformInitInput:Vector2;
	static var transformInitPos:Vector2;
	static var transformInitRot:Float;
	static var transformInitSize:Vector2;
	// Was the transformation editing started by dragging the mouse
	static var transformStartedMouse = false;
	static var drag = false;
	static var dragLeft = false;
	static var dragTop = false;
	static var dragRight = false;
	static var dragBottom = false;
	static var grab = false;
	static var grabX = false;
	static var grabY = false;
	static var rotate = false;
	static var newElementSelected = false;

	public static var handleSize(get, null):Int;
	static inline function get_handleSize():Int { return Std.int(8 * ui.SCALE()); }

	public static function initialize(ui: Zui, cui: Zui) {
		ElementController.ui = ui;
		ElementController.cui = cui;
	}

	public static function selectElement(canvas:TCanvas) {
		if (ui == null) return;

		var selectButton = Main.prefs.keyMap.selectMouseButton;
		if (selectButton == "Left" && ui.inputStarted && ui.inputDown ||
				selectButton == "Right" && ui.inputStartedR && ui.inputDownR) {

			// Deselect
			var lastSelected = Editor.selectedElem;
			Editor.selectedElem = null;

			newElementSelected = false;

			// Elements are sorted by z position (descending), so the topmost element will get
			// selected if multiple elements overlap each other at the mouse position
			var sorted_elements = canvas.elements.copy();
			sorted_elements.reverse();
			for (elem in sorted_elements) {
				var anchorOffset = Canvas.getAnchorOffset(canvas, elem);
				var ex = scaled(Math.absx(canvas, elem)) + anchorOffset[0];
				var ey = scaled(Math.absy(canvas, elem)) + anchorOffset[1];
				var ew = scaled(elem.width);
				var eh = scaled(elem.height);
				// Element center
				var cx = canvas.x + ex + ew / 2;
				var cy = canvas.y + ey + eh / 2;

				var rotHandleX = cx - handleSize / 2;
				var rotHandleY = canvas.y + ey - handleSize * 2 - handleSize / 2;
				var rotHandleH = handleSize * 2 + handleSize / 2;

				if (Math.hitbox(cui, canvas.x + ex - handleSize / 2, canvas.y + ey - handleSize / 2, ew + handleSize, eh + handleSize, elem.rotation)
						|| (Math.hitbox(cui, rotHandleX, rotHandleY, handleSize, rotHandleH, elem.rotation, [cx, cy]) // Rotation handle hitbox
							&& lastSelected == elem)) { // Don't select elements other than the currently selected by their rotation handle
					Editor.selectedElem = elem;

					if (lastSelected != elem)
						newElementSelected = true;
					break;
				}
			}
			// force properties redraw to show selection
			UIProperties.hwin.redraws = 2;
		}
	}

	public static function render(g:Graphics, canvas:TCanvas) {

		// Outline selected elem
		if (Editor.selectedElem != null) {
			var anchorOffset = Canvas.getAnchorOffset(canvas, Editor.selectedElem);

			// Resize rects
			var ex = scaled(Math.absx(canvas, Editor.selectedElem)) + anchorOffset[0];
			var ey = scaled(Math.absy(canvas, Editor.selectedElem)) + anchorOffset[1];
			var ew = scaled(Editor.selectedElem.width);
			var eh = scaled(Editor.selectedElem.height);
			// Element center
			var cx = canvas.x + ex + ew / 2;
			var cy = canvas.y + ey + eh / 2;
			g.pushRotation(Editor.selectedElem.rotation, cx, cy);

			// Draw element outline
			g.color = 0xffffffff;
			g.drawRect(canvas.x + ex, canvas.y + ey, ew, eh);
			g.color = 0xff000000;
			g.drawRect(canvas.x + ex + 1, canvas.y + ey + 1, ew, eh);
			g.color = 0xffffffff;

			// Rotate mouse coords in opposite direction as the element
			var rotatedInput:Vector2 = Math.rotatePoint(ui.inputX, ui.inputY, cx, cy, -Editor.selectedElem.rotation);

			// Draw corner drag handles
			for (handlePosX in 0...3) {
				// 0 = Left, 0.5 = Center, 1 = Right
				var handlePosX:Float = handlePosX / 2;

				for (handlePosY in 0...3) {
					// 0 = Top, 0.5 = Center, 1 = Bottom
					var handlePosY:Float = handlePosY / 2;

					if (handlePosX == 0.5 && handlePosY == 0.5) {
						continue;
					}

					var hX = canvas.x + ex + ew * handlePosX - handleSize / 2;
					var hY = canvas.y + ey + eh * handlePosY - handleSize / 2;

					// Check if the handle is currently dragged (not necessarily hovered!)
					var dragged = false;

					if (handlePosX == 0 && dragLeft) {
						if (handlePosY == 0 && dragTop) dragged = true;
						else if (handlePosY == 0.5 && !(dragTop || dragBottom)) dragged = true;
						else if (handlePosY == 1 && dragBottom) dragged = true;
					} else if (handlePosX == 0.5 && !(dragLeft || dragRight)) {
						if (handlePosY == 0 && dragTop) dragged = true;
						else if (handlePosY == 1 && dragBottom) dragged = true;
					} else if (handlePosX == 1 && dragRight) {
						if (handlePosY == 0 && dragTop) dragged = true;
						else if (handlePosY == 0.5 && !(dragTop || dragBottom)) dragged = true;
						else if (handlePosY == 1 && dragBottom) dragged = true;
					}
					dragged = dragged && drag;


					// Hover
					if (rotatedInput.x > hX && rotatedInput.x < hX + handleSize || dragged) {
						if (rotatedInput.y > hY && rotatedInput.y < hY + handleSize || dragged) {
							g.color = 0xff205d9c;
							g.fillRect(hX, hY, handleSize, handleSize);
							g.color = 0xffffffff;
						}
					}

					g.drawRect(hX, hY, handleSize, handleSize);
				}
			}

			// Draw rotation handle
			g.drawLine(cx, canvas.y + ey, cx, canvas.y + ey - handleSize * 2);

			var rotHandleCenter = new Vector2(cx, canvas.y + ey - handleSize * 2);
			if (rotatedInput.sub(rotHandleCenter).length <= handleSize / 2 || rotate) {
				g.color = 0xff205d9c;
				g.fillCircle(rotHandleCenter.x, rotHandleCenter.y, handleSize / 2);
				g.color = 0xffffffff;
			}
			g.drawCircle(rotHandleCenter.x, rotHandleCenter.y, handleSize / 2);

			g.popTransformation();
		}

	}

	public static function update(ui:Zui, cui:Zui, canvas:TCanvas) {
		arm2d.ElementController.ui = ui;
		arm2d.ElementController.cui = cui;

		if (newElementSelected)
			return;

		if (Editor.selectedElem != null) {
			var elem = Editor.selectedElem;
			var anchorOffset = Canvas.getAnchorOffset(canvas, elem);

			var ex = scaled(Math.absx(canvas, elem)) + anchorOffset[0];
			var ey = scaled(Math.absy(canvas, elem)) + anchorOffset[1];
			var ew = scaled(elem.width);
			var eh = scaled(elem.height);
			var rotatedInput:Vector2 = Math.rotatePoint(ui.inputX, ui.inputY, canvas.x + ex + ew / 2, canvas.y + ey + eh / 2, -elem.rotation);

			if (ui.inputStarted && ui.inputDown) {
				// Drag selected element
				if (Math.hitbox(ui, canvas.x + ex - handleSize / 2, canvas.y + ey - handleSize / 2, ew + handleSize, eh + handleSize, Editor.selectedElem.rotation)) {
					drag = true;
					// Resize
					dragLeft = dragRight = dragTop = dragBottom = false;
					if (rotatedInput.x > canvas.x + ex + ew - handleSize) dragRight = true;
					else if (rotatedInput.x < canvas.x + ex + handleSize) dragLeft = true;
					if (rotatedInput.y > canvas.y + ey + eh - handleSize) dragBottom = true;
					else if (rotatedInput.y < canvas.y + ey + handleSize) dragTop = true;

					startElementManipulation(true);

				} else {
					var rotHandleCenter = new Vector2(canvas.x + ex + ew / 2, canvas.y + ey - handleSize * 2);
					var inputPos = rotatedInput.sub(rotHandleCenter);

					// Rotate selected element
					if (inputPos.length <= handleSize) {
						rotate = true;
						startElementManipulation(true);
					}
				}
			}

			if (isManipulating) {
				UIProperties.hwin.redraws = 2;

				// Confirm
				if ((transformStartedMouse && ui.inputReleased) || (!transformStartedMouse && ui.inputStarted)) {
					endElementManipulation();

				// Reset
				} else if ((ui.isKeyPressed && ui.isEscapeDown) || ui.inputStartedR) {
					endElementManipulation(true);

				} else if (drag) {
					var transformDelta = new Vector2(ui.inputX, ui.inputY).sub(transformInitInput);

					if (!transformStartedMouse) {
						if (ui.isKeyPressed && ui.key == KeyCode.X) {
							elem.width = Std.int(transformInitSize.x);
							elem.height = Std.int(transformInitSize.y);
							dragRight = true;
							dragBottom = !dragBottom;
						}
						if (ui.isKeyPressed && ui.key == KeyCode.Y) {
							elem.width = Std.int(transformInitSize.x);
							elem.height = Std.int(transformInitSize.y);
							dragBottom = true;
							dragRight = !dragRight;
						}
					}

					if (dragRight) {
						transformDelta.x = Math.calculateTransformDelta(ui, Editor.gridSnapPos, Editor.gridUseRelative, Editor.gridSize, transformDelta.x, transformInitPos.x + transformInitSize.x);
						elem.width = Std.int(transformInitSize.x + transformDelta.x);
					} else if (dragLeft) {
						transformDelta.x = Math.calculateTransformDelta(ui, Editor.gridSnapPos, Editor.gridUseRelative, Editor.gridSize, transformDelta.x, transformInitPos.x);
						elem.x = transformInitPos.x + transformDelta.x;
						elem.width = Std.int(transformInitSize.x - transformDelta.x);
					}
					if (dragBottom) {
						transformDelta.y = Math.calculateTransformDelta(ui, Editor.gridSnapPos, Editor.gridUseRelative, Editor.gridSize, transformDelta.y, transformInitPos.y + transformInitSize.y);
						elem.height = Std.int(transformInitSize.y + transformDelta.y);
					}
					else if (dragTop) {
						transformDelta.y = Math.calculateTransformDelta(ui, Editor.gridSnapPos, Editor.gridUseRelative, Editor.gridSize, transformDelta.y, transformInitPos.y);
						elem.y = transformInitPos.y + transformDelta.y;
						elem.height = Std.int(transformInitSize.y - transformDelta.y);
					}

					if (elem.type != ElementType.Image) {
						if (elem.width < 1) elem.width = 1;
						if (elem.height < 1) elem.height = 1;
					}

					if (!dragLeft && !dragRight && !dragBottom && !dragTop) {
						grab = true;
						grabX = true;
						grabY = true;
						drag = false;
					} else {
						// Ensure there the delta is 0 on unused axes
						if (!dragBottom && !dragTop) transformDelta.y = 0;
						else if (!dragLeft && !dragRight) transformDelta.y = 0;

						Editor.currentOperation = ' x: ${elem.x}  y: ${elem.y}  w: ${elem.width}  h: ${elem.height}  (dx: ${transformDelta.x}  dy: ${transformDelta.y})';
					}

				} else if (grab) {
					var transformDelta = new Vector2(ui.inputX, ui.inputY).sub(transformInitInput);

					if (ui.isKeyPressed && ui.key == KeyCode.X) {
						elem.x = transformInitPos.x;
						elem.y = transformInitPos.y;
						grabX = true;
						grabY = !grabY;
					}
					if (ui.isKeyPressed && ui.key == KeyCode.Y) {
						elem.x = transformInitPos.x;
						elem.y = transformInitPos.y;
						grabY = true;
						grabX = !grabX;
					}

					if (grabX) {
						transformDelta.x = Math.calculateTransformDelta(ui, Editor.gridSnapPos, Editor.gridUseRelative, Editor.gridSize, transformDelta.x, transformInitPos.x);
						elem.x = Std.int(transformInitPos.x + transformDelta.x);
					}
					if (grabY) {
						transformDelta.y = Math.calculateTransformDelta(ui, Editor.gridSnapPos, Editor.gridUseRelative, Editor.gridSize, transformDelta.y, transformInitPos.y);
						elem.y = Std.int(transformInitPos.y + transformDelta.y);
					}

					// Ensure there the delta is 0 on unused axes
					if (!grabX) transformDelta.x = 0;
					else if (!grabY) transformDelta.y = 0;

					Editor.currentOperation = ' x: ${elem.x}  y: ${elem.y}  (dx: ${transformDelta.x}  dy: ${transformDelta.y})';

				} else if (rotate) {
					var elemCenter = new Vector2(canvas.x + ex + ew / 2, canvas.y + ey + eh / 2);
					var inputPos = new Vector2(ui.inputX, ui.inputY).sub(elemCenter);

					// inputPos.x and inputPos.y are both positive when the mouse is in the lower right
					// corner of the elements center, so the positive x axis used for the angle calculation
					// in atan2() is equal to the global negative y axis. That's why we have to invert the
					// angle and add Pi to get the correct rotation. atan2() also returns an angle in the
					// intervall (-PI, PI], so we don't have to calculate the angle % PI*2 anymore.
					var inputAngle = -std.Math.atan2(inputPos.x, inputPos.y) + std.Math.PI;

					// Ctrl toggles rotation step mode
					if ((ui.isKeyDown && ui.key == Main.prefs.keyMap.gridInvert) != Editor.useRotationSteps) {
						inputAngle = std.Math.round(inputAngle / Editor.rotationSteps) * Editor.rotationSteps;
					}

					elem.rotation = inputAngle;
					Editor.currentOperation = " Rot: " + Math.roundPrecision(Math.toDegrees(inputAngle), 2) + "deg";
				}
			}

			if (ui.isKeyPressed && !ui.isTyping) {
				if (!grab && ui.key == Main.prefs.keyMap.grabKey){startElementManipulation(); grab = true; grabX = true; grabY = true;}
				if (!drag && ui.key == Main.prefs.keyMap.sizeKey) {startElementManipulation(); drag = true; dragLeft = false; dragTop = false; dragRight = true; dragBottom = true;}
				if (!rotate && ui.key == Main.prefs.keyMap.rotateKey) {startElementManipulation(); rotate = true;}

				if (!isManipulating) {
					// Move with arrows
					if (ui.key == KeyCode.Left) Editor.gridSnapPos ? elem.x -= Editor.gridSize : elem.x--;
					if (ui.key == KeyCode.Right) Editor.gridSnapPos ? elem.x += Editor.gridSize : elem.x++;
					if (ui.key == KeyCode.Up) Editor.gridSnapPos ? elem.y -= Editor.gridSize : elem.y--;
					if (ui.key == KeyCode.Down) Editor.gridSnapPos ? elem.y += Editor.gridSize : elem.y++;

					if (ui.isBackspaceDown || ui.isDeleteDown){
						CanvasTools.removeElem(canvas, Editor.selectedElem);
						Editor.selectedElem = null;
					}
					else if (ui.key == KeyCode.D) Editor.selectedElem = CanvasTools.duplicateElem(canvas, elem);
				}
			}
		} else {
			endElementManipulation();
		}
	}

	static function startElementManipulation(?mousePressed=false) {
		if (isManipulating) endElementManipulation(true);

		transformInitInput = new Vector2(ui.inputX, ui.inputY);
		transformInitPos = new Vector2(Editor.selectedElem.x, Editor.selectedElem.y);
		transformInitSize = new Vector2(Editor.selectedElem.width, Editor.selectedElem.height);
		transformInitRot = Editor.selectedElem.rotation;
		transformStartedMouse = mousePressed;

		isManipulating = true;
	}

	static function endElementManipulation(reset=false) {
		if (reset) {
			Editor.selectedElem.x = transformInitPos.x;
			Editor.selectedElem.y = transformInitPos.y;
			Editor.selectedElem.width = Std.int(transformInitSize.x);
			Editor.selectedElem.height = Std.int(transformInitSize.y);
			Editor.selectedElem.rotation = transformInitRot;
		}

		isManipulating = false;

		grab = false;
		drag = false;
		rotate = false;

		transformStartedMouse = false;
		Editor.currentOperation = "";
	}

	static inline function scaled(f: Float): Int { return Std.int(f * cui.SCALE()); }
}
