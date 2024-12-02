package zui;

using zui.GraphicsExtension;

@:access(zui.Zui)
class Nodes {

	public var nodesDrag = false;
	public var nodesSelected: Array<TNode> = [];
	public var panX = 0.0;
	public var panY = 0.0;
	public var zoom = 1.0;
	public var uiw = 0;
	public var uih = 0;
	public var _inputStarted = false;
	public var colorPickerCallback: kha.Color->Void = null;
	var scaleFactor = 1.0;
	var ELEMENT_H = 25;
	var dragged = false;
	var moveOnTop: TNode = null;
	var linkDrag: TNodeLink = null;
	var isNewLink = false;
	var snapFromId = -1;
	var snapToId = -1;
	var snapSocket = 0;
	var snapX = 0.0;
	var snapY = 0.0;
	var handle = new Zui.Handle();
	static var elementsBaked = false;
	static var socketImage: kha.Image = null;
	static var socketReleased = false;
	static var clipboard = "";
	static var boxSelect = false;
	static var boxSelectX = 0;
	static var boxSelectY = 0;
	static inline var maxButtons = 9;

	public static var excludeRemove: Array<String> = []; // No removal for listed node types
	public static var onLinkDrag: TNodeLink->Bool->Void = null;
	public static var onHeaderReleased: TNode->Void = null;
	public static var onSocketReleased: TNodeSocket->Void = null;
	public static var onCanvasReleased: Void->Void = null;
	public static var onNodeRemove: TNode->Void = null;
	public static var onCanvasControl: Void->CanvasControl = null; // Pan, zoom

	#if zui_translate
	public static dynamic function tr(id: String, vars: Map<String, String> = null) {
		return id;
	}
	#else
	public static inline function tr(id: String, vars: Map<String, String> = null) {
		return id;
	}
	#end

	public function new() {}

	public inline function SCALE(): Float {
		return scaleFactor * zoom;
	}
	public inline function PAN_X(): Float {
		var zoomPan = (1.0 - zoom) * uiw / 2.5;
		return panX * SCALE() + zoomPan;
	}
	public inline function PAN_Y(): Float {
		var zoomPan = (1.0 - zoom) * uih / 2.5;
		return panY * SCALE() + zoomPan;
	}
	public inline function LINE_H(): Int {
		return Std.int(ELEMENT_H * SCALE());
	}
	function BUTTONS_H(node: TNode): Int {
		var h = 0.0;
		for (but in node.buttons) {
			if (but.type == "RGBA") h += 102 * SCALE() + LINE_H() * 5; // Color wheel + controls
			else if (but.type == "VECTOR") h += LINE_H() * 4;
			else if (but.type == "CUSTOM") h += LINE_H() * but.height;
			else h += LINE_H();
		}
		return Std.int(h);
	}
	function OUTPUTS_H(sockets: Array<TNodeSocket>, length: Null<Int> = null): Int {
		var h = 0.0;
		for (i in 0...(length == null ? sockets.length : length)) {
			h += LINE_H();
		}
		return Std.int(h);
	}
	function INPUTS_H(canvas: TNodeCanvas, sockets: Array<TNodeSocket>, length: Null<Int> = null): Int {
		var h = 0.0;
		for (i in 0...(length == null ? sockets.length : length)) {
			if (sockets[i].type == "VECTOR" && sockets[i].display == 1 && !inputLinked(canvas, sockets[i].node_id, i)) h += LINE_H() * 4;
			else h += LINE_H();
		}
		return Std.int(h);
	}
	inline function NODE_H(canvas: TNodeCanvas, node: TNode): Int {
		return Std.int(LINE_H() * 1.2 + INPUTS_H(canvas, node.inputs) + OUTPUTS_H(node.outputs) + BUTTONS_H(node));
	}
	inline function NODE_W(node: TNode): Int {
		return Std.int((node.width != null ? node.width : 140) * SCALE());
	}
	inline function NODE_X(node: TNode): Float {
		return node.x * SCALE() + PAN_X();
	}
	inline function NODE_Y(node: TNode): Float {
		return node.y * SCALE() + PAN_Y();
	}
	inline function INPUT_Y(canvas: TNodeCanvas, sockets: Array<TNodeSocket>, pos: Int): Int {
		return Std.int(LINE_H() * 1.62) + INPUTS_H(canvas, sockets, pos);
	}
	inline function OUTPUT_Y(sockets: Array<TNodeSocket>, pos: Int): Int {
		return Std.int(LINE_H() * 1.62) + OUTPUTS_H(sockets, pos);
	}
	public inline function p(f: Float): Float {
		return f * SCALE();
	}

	public function getNode(nodes: Array<TNode>, id: Int): TNode {
		for (node in nodes) if (node.id == id) return node;
		return null;
	}

	var nodeId = -1;
	public function getNodeId(nodes: Array<TNode>): Int {
		if (nodeId == -1) for (n in nodes) if (nodeId < n.id) nodeId = n.id;
		return ++nodeId;
	}

	public function getLinkId(links: Array<TNodeLink>): Int {
		var id = 0;
		for (l in links) if (l.id >= id) id = l.id + 1;
		return id;
	}

	public function getSocketId(nodes: Array<TNode>): Int {
		var id = 0;
		for (n in nodes) {
			for (s in n.inputs) if (s.id >= id) id = s.id + 1;
			for (s in n.outputs) if (s.id >= id) id = s.id + 1;
		}
		return id;
	}

	function inputLinked(canvas: TNodeCanvas, node_id: Int, i: Int): Bool {
		for (l in canvas.links) if (l.to_id == node_id && l.to_socket == i) return true;
		return false;
	}

	function bakeElements(ui: Zui) {
		ui.g.end();
		elementsBaked = true;
		socketImage = kha.Image.createRenderTarget(24, 24);
		var g = socketImage.g2;
		g.begin(true, 0x00000000);
		g.color = 0xff000000;
		zui.GraphicsExtension.fillCircle(g, 12, 12, 12);
		g.color = 0xffffffff;
		zui.GraphicsExtension.fillCircle(g, 12, 12, 9);
		g.end();
		ui.g.begin(false);
	}

	public function nodeCanvas(ui: Zui, canvas: TNodeCanvas) {
		if (!elementsBaked) bakeElements(ui);

		var wx = ui._windowX;
		var wy = ui._windowY;
		var _inputEnabled = ui.inputEnabled;
		ui.inputEnabled = _inputEnabled && popupCommands == null;
		var controls = onCanvasControl != null ? onCanvasControl() : {
			panX: ui.inputDownR ? ui.inputDX : 0.0,
			panY: ui.inputDownR ? ui.inputDY : 0.0,
			zoom: -ui.inputWheelDelta / 10.0
		};
		socketReleased = false;

		// Pan canvas
		if (ui.inputEnabled && (controls.panX != 0.0 || controls.panY != 0.0)) {
			panX += controls.panX / SCALE();
			panY += controls.panY / SCALE();
		}

		// Zoom canvas
		if (ui.inputEnabled && controls.zoom != 0.0) {
			zoom += controls.zoom;
			if (zoom < 0.1) zoom = 0.1;
			else if (zoom > 1.0) zoom = 1.0;
			zoom = Math.round(zoom * 10) / 10;
			uiw = ui._w;
			uih = ui._h;
		}
		scaleFactor = ui.SCALE();
		ELEMENT_H = ui.t.ELEMENT_H + 2;
		ui.setScale(SCALE()); // Apply zoomed scale
		ui.elementsBaked = true;
		ui.g.font = ui.ops.font;
		ui.g.fontSize = ui.fontSize;

		for (link in canvas.links) {
			var from = getNode(canvas.nodes, link.from_id);
			var to = getNode(canvas.nodes, link.to_id);
			var fromX = from == null ? ui.inputX : wx + NODE_X(from) + NODE_W(from);
			var fromY = from == null ? ui.inputY : wy + NODE_Y(from) + OUTPUT_Y(from.outputs, link.from_socket);
			var toX = to == null ? ui.inputX : wx + NODE_X(to);
			var toY = to == null ? ui.inputY : wy + NODE_Y(to) + INPUT_Y(canvas, to.inputs, link.to_socket) + OUTPUTS_H(to.outputs) + BUTTONS_H(to);

			// Cull
			var left = toX > fromX ? fromX : toX;
			var right = toX > fromX ? toX : fromX;
			var top = toY > fromY ? fromY : toY;
			var bottom = toY > fromY ? toY : fromY;
			if (right < 0 || left > wx + ui._windowW ||
				bottom < 0 || top > wy + ui._windowH) {
				continue;
			}

			// Snap to nearest socket
			if (linkDrag == link) {
				if (snapFromId != -1) {
					fromX = snapX;
					fromY = snapY;
				}
				if (snapToId != -1) {
					toX = snapX;
					toY = snapY;
				}
				snapFromId = snapToId = -1;

				for (node in canvas.nodes) {
					var inps = node.inputs;
					var outs = node.outputs;
					var nodeh = NODE_H(canvas, node);
					var rx = wx + NODE_X(node) - LINE_H() / 2;
					var ry = wy + NODE_Y(node) - LINE_H() / 2;
					var rw = NODE_W(node) + LINE_H();
					var rh = nodeh + LINE_H();
					if (ui.getInputInRect(rx, ry, rw, rh)) {
						if (from == null && node.id != to.id) { // Snap to output
							for (i in 0...outs.length) {
								var sx = wx + NODE_X(node) + NODE_W(node);
								var sy = wy + NODE_Y(node) + OUTPUT_Y(outs, i);
								var rx = sx - LINE_H() / 2;
								var ry = sy - LINE_H() / 2;
								if (ui.getInputInRect(rx, ry, LINE_H(), LINE_H())) {
									snapX = sx;
									snapY = sy;
									snapFromId = node.id;
									snapSocket = i;
									break;
								}
							}
						}
						else if (to == null && node.id != from.id) { // Snap to input
							for (i in 0...inps.length) {
								var sx = wx + NODE_X(node);
								var sy = wy + NODE_Y(node) + INPUT_Y(canvas, inps, i) + OUTPUTS_H(outs) + BUTTONS_H(node);
								var rx = sx - LINE_H() / 2;
								var ry = sy - LINE_H() / 2;
								if (ui.getInputInRect(rx, ry, LINE_H(), LINE_H())) {
									snapX = sx;
									snapY = sy;
									snapToId = node.id;
									snapSocket = i;
									break;
								}
							}
						}
					}
				}
			}

			var selected = false;
			for (n in nodesSelected) {
				if (link.from_id == n.id || link.to_id == n.id) {
					selected = true;
					break;
				}
			}

			drawLink(ui, fromX - wx, fromY - wy, toX - wx, toY - wy, selected);
		}

		for (node in canvas.nodes) {
			// Cull
			if (NODE_X(node) > ui._windowW || NODE_X(node) + NODE_W(node) < 0 ||
				NODE_Y(node) > ui._windowH || NODE_Y(node) + NODE_H(canvas, node) < 0) {
				if (!isSelected(node)) continue;
			}

			var inps = node.inputs;
			var outs = node.outputs;

			// Drag node
			var nodeh = NODE_H(canvas, node);
			if (ui.inputEnabled && ui.getInputInRect(wx + NODE_X(node) - LINE_H() / 2, wy + NODE_Y(node), NODE_W(node) + LINE_H(), LINE_H())) {
				if (ui.inputStarted) {
					if (ui.isShiftDown || ui.isCtrlDown) {
						// Add to selection or deselect
						isSelected(node) ?
							nodesSelected.remove(node) :
							nodesSelected.push(node);
					}
					else if (nodesSelected.length <= 1) {
						// Selecting single node, otherwise wait for input release
						nodesSelected = [node];
					}
					moveOnTop = node; // Place selected node on top
					nodesDrag = true;
					dragged = false;
				}
				else if (ui.inputReleased && !ui.isShiftDown && !ui.isCtrlDown && !dragged) {
					// No drag performed, select single node
					nodesSelected = [node];
					if (onHeaderReleased != null) {
						onHeaderReleased(node);
					}
				}
			}
			if (ui.inputStarted && ui.getInputInRect(wx + NODE_X(node) - LINE_H() / 2, wy + NODE_Y(node) - LINE_H() / 2, NODE_W(node) + LINE_H(), nodeh + LINE_H())) {
				// Check sockets
				if (linkDrag == null) {
					for (i in 0...outs.length) {
						var sx = wx + NODE_X(node) + NODE_W(node);
						var sy = wy + NODE_Y(node) + OUTPUT_Y(outs, i);
						if (ui.getInputInRect(sx - LINE_H() / 2, sy - LINE_H() / 2, LINE_H(), LINE_H())) {
							// New link from output
							var l: TNodeLink = { id: getLinkId(canvas.links), from_id: node.id, from_socket: i, to_id: -1, to_socket: -1 };
							canvas.links.push(l);
							linkDrag = l;
							isNewLink = true;
							break;
						}
					}
				}
				if (linkDrag == null) {
					for (i in 0...inps.length) {
						var sx = wx + NODE_X(node);
						var sy = wy + NODE_Y(node) + INPUT_Y(canvas, inps, i) + OUTPUTS_H(outs) + BUTTONS_H(node);
						if (ui.getInputInRect(sx - LINE_H() / 2, sy - LINE_H() / 2, LINE_H(), LINE_H())) {
							// Already has a link - disconnect
							for (l in canvas.links) {
								if (l.to_id == node.id && l.to_socket == i) {
									l.to_id = l.to_socket = -1;
									linkDrag = l;
									isNewLink = false;
									break;
								}
							}
							if (linkDrag != null) break;
							// New link from input
							var l: TNodeLink = {
								id: getLinkId(canvas.links),
								from_id: -1,
								from_socket: -1,
								to_id: node.id,
								to_socket: i
							};
							canvas.links.push(l);
							linkDrag = l;
							isNewLink = true;
							break;
						}
					}
				}
			}
			else if (ui.inputReleased) {
				if (snapToId != -1) { // Connect to input
					// Force single link per input
					for (l in canvas.links) {
						if (l.to_id == snapToId && l.to_socket == snapSocket) {
							canvas.links.remove(l);
							break;
						}
					}
					linkDrag.to_id = snapToId;
					linkDrag.to_socket = snapSocket;
					ui.changed = true;
				}
				else if (snapFromId != -1) { // Connect to output
					linkDrag.from_id = snapFromId;
					linkDrag.from_socket = snapSocket;
					ui.changed = true;
				}
				else if (linkDrag != null) { // Remove dragged link
					canvas.links.remove(linkDrag);
					ui.changed = true;
					if (onLinkDrag != null) {
						onLinkDrag(linkDrag, isNewLink);
					}
				}
				snapToId = snapFromId = -1;
				linkDrag = null;
				nodesDrag = false;
			}
			if (nodesDrag && isSelected(node) && !ui.inputDownR) {
				if (ui.inputDX != 0 || ui.inputDY != 0) {
					dragged = true;
					node.x += Std.int(ui.inputDX / SCALE());
					node.y += Std.int(ui.inputDY / SCALE());
				}
			}

			drawNode(ui, node, canvas);
		}

		if (onCanvasReleased != null && ui.inputEnabled && (ui.inputReleased || ui.inputReleasedR) && !socketReleased) {
			onCanvasReleased();
		}

		if (boxSelect) {
			ui.g.color = 0x223333dd;
			ui.g.fillRect(boxSelectX, boxSelectY, ui.inputX - boxSelectX - ui._windowX, ui.inputY - boxSelectY - ui._windowY);
			ui.g.color = 0x773333dd;
			ui.g.drawRect(boxSelectX, boxSelectY, ui.inputX - boxSelectX - ui._windowX, ui.inputY - boxSelectY - ui._windowY);
			ui.g.color = 0xffffffff;
		}
		if (ui.inputEnabled && ui.inputStarted && !ui.isAltDown && linkDrag == null && !nodesDrag && !ui.changed) {
			boxSelect = true;
			boxSelectX = Std.int(ui.inputX - ui._windowX);
			boxSelectY = Std.int(ui.inputY - ui._windowY);
		}
		else if (boxSelect && !ui.inputDown) {
			boxSelect = false;
			var nodes: Array<TNode> = [];
			var left = boxSelectX;
			var top = boxSelectY;
			var right = Std.int(ui.inputX - ui._windowX);
			var bottom = Std.int(ui.inputY - ui._windowY);
			if (left > right) {
				var t = left;
				left = right;
				right = t;
			}
			if (top > bottom) {
				var t = top;
				top = bottom;
				bottom = t;
			}
			for (n in canvas.nodes) {
				if (NODE_X(n) + NODE_W(n) > left && NODE_X(n) < right &&
					NODE_Y(n) + NODE_H(canvas, n) > top && NODE_Y(n) < bottom) {
					nodes.push(n);
				}
			}
			(ui.isShiftDown || ui.isCtrlDown) ? for (n in nodes) nodesSelected.push(n) : nodesSelected = nodes;
		}

		// Place selected node on top
		if (moveOnTop != null) {
			canvas.nodes.remove(moveOnTop);
			canvas.nodes.push(moveOnTop);
			moveOnTop = null;
		}

		// Node copy & paste
		var cutSelected = false;
		if (Zui.isCopy) {
			var copyNodes: Array<TNode> = [];
			for (n in nodesSelected) {
				if (excludeRemove.indexOf(n.type) >= 0) continue;
				copyNodes.push(n);
			}
			var copyLinks: Array<TNodeLink> = [];
			for (l in canvas.links) {
				var from = getNode(nodesSelected, l.from_id);
				var to = getNode(nodesSelected, l.to_id);
				if (from != null && excludeRemove.indexOf(from.type) == -1 &&
					to != null && excludeRemove.indexOf(to.type) == -1) {
					copyLinks.push(l);
				}
			}
			if (copyNodes.length > 0) {
				var copyCanvas: TNodeCanvas = {
					name: canvas.name,
					nodes: copyNodes,
					links: copyLinks
				};
				clipboard = haxe.Json.stringify(copyCanvas);
			}
			cutSelected = Zui.isCut;
		}
		if (Zui.isPaste && !ui.isTyping) {
			var pasteCanvas: TNodeCanvas = null;
			// Clipboard can contain non-json data
			try {
				pasteCanvas = haxe.Json.parse(clipboard);
			}
			catch(_) {}
			if (pasteCanvas != null) {
				for (l in pasteCanvas.links) {
					// Assign unique link id
					l.id = getLinkId(canvas.links);
					canvas.links.push(l);
				}
				var offsetX = Std.int((Std.int(ui.inputX / ui.SCALE()) * SCALE() - wx - PAN_X()) / SCALE()) - pasteCanvas.nodes[pasteCanvas.nodes.length - 1].x;
				var offsetY = Std.int((Std.int(ui.inputY / ui.SCALE()) * SCALE() - wy - PAN_Y()) / SCALE()) - pasteCanvas.nodes[pasteCanvas.nodes.length - 1].y;
				for (n in pasteCanvas.nodes) {
					// Assign unique node id
					var old_id = n.id;
					n.id = getNodeId(canvas.nodes);
					for (soc in n.inputs) {
						soc.id = getSocketId(canvas.nodes);
						soc.node_id = n.id;
					}
					for (soc in n.outputs) {
						soc.id = getSocketId(canvas.nodes);
						soc.node_id = n.id;
					}
					for (l in pasteCanvas.links) {
						if (l.from_id == old_id) l.from_id = n.id;
						else if (l.to_id == old_id) l.to_id = n.id;
					}
					n.x += offsetX;
					n.y += offsetY;
					canvas.nodes.push(n);
				}
				nodesDrag = true;
				nodesSelected = pasteCanvas.nodes;
				ui.changed = true;
			}
		}

		// Select all nodes
		if (ui.isCtrlDown && ui.key == kha.input.KeyCode.A && !ui.isTyping) {
			nodesSelected = [];
			for (n in canvas.nodes) nodesSelected.push(n);
		}

		// Node removal
		if (ui.inputEnabled && (ui.isBackspaceDown || ui.isDeleteDown || cutSelected) && !ui.isTyping) {
			var i = nodesSelected.length - 1;
			while (i >= 0) {
				var n = nodesSelected[i--];
				if (excludeRemove.indexOf(n.type) >= 0) continue;
				removeNode(n, canvas);
				ui.changed = true;
			}
		}

		ui.setScale(scaleFactor); // Restore non-zoomed scale
		ui.elementsBaked = true;
		ui.inputEnabled = _inputEnabled;

		if (popupCommands != null) {
			ui._x = popupX;
			ui._y = popupY;
			ui._w = popupW;

			ui.fill(-6, -6, ui._w / ui.SCALE() + 12, popupH + 12, ui.t.ACCENT_SELECT_COL);
			ui.fill(-5, -5, ui._w / ui.SCALE() + 10, popupH + 10, ui.t.SEPARATOR_COL);
			popupCommands(ui);

			var hide = (ui.inputStarted || ui.inputStartedR) && (ui.inputX - wx < popupX - 6 || ui.inputX - wx > popupX + popupW + 6 || ui.inputY - wy < popupY - 6 || ui.inputY - wy > popupY + popupH * ui.SCALE() + 6);
			if (hide || ui.isEscapeDown) {
				popupCommands = null;
			}
		}
	}

	// Retrieve combo items for buttons of type ENUM
	public static var enumTexts: String->Array<String> = null;

	inline function isSelected(node: TNode): Bool {
		return nodesSelected.indexOf(node) >= 0;
	}

	public function drawNode(ui: Zui, node: TNode, canvas: TNodeCanvas) {
		var wx = ui._windowX;
		var wy = ui._windowY;
		var uiX = ui._x;
		var uiY = ui._y;
		var uiW = ui._w;
		var w = NODE_W(node);
		var g = ui.g;
		var h = NODE_H(canvas, node);
		var nx = NODE_X(node);
		var ny = NODE_Y(node);
		var text = tr(node.name);
		var lineh = LINE_H();

		// Disallow input if node is overlapped by another node
		_inputStarted = ui.inputStarted;
		if (ui.inputStarted) {
			for (i in (canvas.nodes.indexOf(node) + 1)...canvas.nodes.length) {
				var n = canvas.nodes[i];
				if (NODE_X(n) < ui.inputX - ui._windowX && NODE_X(n) + NODE_W(n) > ui.inputX - ui._windowX &&
					NODE_Y(n) < ui.inputY - ui._windowY && NODE_Y(n) + NODE_H(canvas, n) > ui.inputY - ui._windowY) {
					ui.inputStarted = false;
					break;
				}
			}
		}

		// Outline
		g.color = isSelected(node) ? ui.t.LABEL_COL : ui.t.CONTEXT_COL;
		g.fillRect(nx - 1, ny - 1, w + 2, h + 2);

		// Body
		g.color = ui.t.WINDOW_BG_COL;
		g.fillRect(nx, ny, w, h);

		// Header line
		g.color = node.color;
		g.fillRect(nx, ny + lineh - p(3), w, p(3));

		// Title
		g.color = ui.t.LABEL_COL;
		var textw = g.font.width(ui.fontSize, text);
		g.drawString(text, nx + p(10), ny + p(6));
		ui._x = nx; // Use the whole line for hovering and not just the drawn string.
		ui._y = ny;
		ui._w = w;
		if (ui.getHover(lineh) && node.tooltip != null) ui.tooltip(tr(node.tooltip));

		ny += lineh * 0.5;

		// Outputs
		for (out in node.outputs) {
			ny += lineh;
			g.color = out.color;
			g.drawScaledImage(socketImage, nx + w - p(6), ny - p(3), p(12), p(12));
		}
		ny -= lineh * node.outputs.length;
		g.color = ui.t.LABEL_COL;
		for (out in node.outputs) {
			ny += lineh;
			var strw = ui.ops.font.width(ui.fontSize, tr(out.name));
			g.drawString(tr(out.name), nx + w - strw - p(12), ny - p(3));
			ui._x = nx;
			ui._y = ny;
			ui._w = w;
			if (ui.getHover(lineh) && out.tooltip != null) ui.tooltip(tr(out.tooltip));

			if (onSocketReleased != null && ui.inputEnabled && (ui.inputReleased || ui.inputReleasedR)) {
				if (ui.inputX > wx + nx && ui.inputX < wx + nx + w && ui.inputY > wy + ny && ui.inputY < wy + ny + lineh) {
					onSocketReleased(out);
					socketReleased = true;
				}
			}
		}

		// Buttons
		var nhandle = handle.nest(node.id);
		ny -= lineh / 3; // Fix align
		for (buti in 0...node.buttons.length) {
			var but = node.buttons[buti];

			if (but.type == "RGBA") {
				ny += lineh; // 18 + 2 separator
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				var val: kha.arrays.Float32Array = node.outputs[but.output].default_value;
				nhandle.color = kha.Color.fromFloats(val[0], val[1], val[2]);
				Ext.colorWheel(ui, nhandle, false, null, null, true,  function () {
					colorPickerCallback = function (color: kha.Color) {
						node.outputs[but.output].default_value[0] = color.R;
						node.outputs[but.output].default_value[1] = color.G;
						node.outputs[but.output].default_value[2] = color.B;
						ui.changed = true;
					};
				});
				val[0] = nhandle.color.R;
				val[1] = nhandle.color.G;
				val[2] = nhandle.color.B;
			}
			else if (but.type == "VECTOR") {
				ny += lineh;
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				var min = but.min != null ? but.min : 0.0;
				var max = but.max != null ? but.max : 1.0;
				var textOff = ui.t.TEXT_OFFSET;
				ui.t.TEXT_OFFSET = 6;
				ui.text(tr(but.name));
				if (ui.isHovered && but.tooltip != null) ui.tooltip(tr(but.tooltip));
				var val: kha.arrays.Float32Array = but.default_value;
				val[0] = ui.slider(nhandle.nest(buti).nest(0, {value: val[0]}), "X", min, max, true, 100, true, Left);
				if (ui.isHovered && but.tooltip != null) ui.tooltip(tr(but.tooltip));
				val[1] = ui.slider(nhandle.nest(buti).nest(1, {value: val[1]}), "Y", min, max, true, 100, true, Left);
				if (ui.isHovered && but.tooltip != null) ui.tooltip(tr(but.tooltip));
				val[2] = ui.slider(nhandle.nest(buti).nest(2, {value: val[2]}), "Z", min, max, true, 100, true, Left);
				if (ui.isHovered && but.tooltip != null) ui.tooltip(tr(but.tooltip));
				ui.t.TEXT_OFFSET = textOff;
				if (but.output != null) node.outputs[but.output].default_value = but.default_value;
				ny += lineh * 3;
			}
			else if (but.type == "VALUE") {
				ny += lineh;
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				var soc = node.outputs[but.output];
				var min = but.min != null ? but.min : 0.0;
				var max = but.max != null ? but.max : 1.0;
				var prec = but.precision != null ? but.precision : 100.0;
				var textOff = ui.t.TEXT_OFFSET;
				ui.t.TEXT_OFFSET = 6;
				soc.default_value = ui.slider(nhandle.nest(buti, {value: soc.default_value}), "Value", min, max, true, prec, true, Left);
				if (ui.isHovered && but.tooltip != null) ui.tooltip(tr(but.tooltip));
				ui.t.TEXT_OFFSET = textOff;
			}
			else if (but.type == "STRING") {
				ny += lineh;
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				var soc = but.output != null ? node.outputs[but.output] : null;
				but.default_value = ui.textInput(nhandle.nest(buti, {text: soc != null ? soc.default_value : but.default_value != null ? but.default_value : ""}), tr(but.name));
				if (soc != null) soc.default_value = but.default_value;
				if (ui.isHovered && but.tooltip != null) ui.tooltip(tr(but.tooltip));
			}
			else if (but.type == "ENUM") {
				ny += lineh;
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				var texts = Std.isOfType(but.data, Array) ? [for (s in cast(but.data, Array<Dynamic>)) tr(s)] : enumTexts(node.type);
				var buthandle = nhandle.nest(buti);
				buthandle.position = but.default_value;
				but.default_value = ui.combo(buthandle, texts, tr(but.name));
				if (ui.isHovered && but.tooltip != null) ui.tooltip(tr(but.tooltip));
			}
			else if (but.type == "BOOL") {
				ny += lineh;
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				but.default_value = ui.check(nhandle.nest(buti, {selected: but.default_value}), tr(but.name));
				if (ui.isHovered && but.tooltip != null) ui.tooltip(tr(but.tooltip));
			}
			else if (but.type == "CUSTOM") { // Calls external function for custom button drawing
				ny += lineh;
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				var dot = but.name.lastIndexOf("."); // TNodeButton.name specifies external function path
				var fn = Reflect.field(Type.resolveClass(but.name.substr(0, dot)), but.name.substr(dot + 1));
				fn(ui, this, node);
				ny += lineh * (but.height - 1); // TNodeButton.height specifies vertical button size
			}
		}
		ny += lineh / 3; // Fix align

		// Inputs
		for (i in 0...node.inputs.length) {
			var inp = node.inputs[i];
			ny += lineh;
			g.color = inp.color;
			g.drawScaledImage(socketImage, nx - p(6), ny - p(3), p(12), p(12));
			var isLinked = inputLinked(canvas, node.id, i);
			if (!isLinked && inp.type == "VALUE") {
				ui._x = nx + p(6);
				ui._y = ny - p(9);
				ui._w = Std.int(w - p(6));
				var soc = inp;
				var min = soc.min != null ? soc.min : 0.0;
				var max = soc.max != null ? soc.max : 1.0;
				var prec = soc.precision != null ? soc.precision : 100.0;
				var textOff = ui.t.TEXT_OFFSET;
				ui.t.TEXT_OFFSET = 6;
				soc.default_value = ui.slider(nhandle.nest(maxButtons).nest(i, {value: soc.default_value}), tr(inp.name), min, max, true, prec, true, Left);
				if (ui.isHovered && inp.tooltip != null) ui.tooltip(tr(inp.tooltip));
				ui.t.TEXT_OFFSET = textOff;
			}
			else if (!isLinked && inp.type == "STRING") {
				ui._x = nx + p(6);
				ui._y = ny - p(9);
				ui._w = Std.int(w - p(6));
				var soc = inp;
				var textOff = ui.t.TEXT_OFFSET;
				ui.t.TEXT_OFFSET = 6;
				soc.default_value = ui.textInput(nhandle.nest(maxButtons).nest(i, {text: soc.default_value}), tr(inp.name), Left);
				if (ui.isHovered && inp.tooltip != null) ui.tooltip(tr(inp.tooltip));
				ui.t.TEXT_OFFSET = textOff;
			}
			else if (!isLinked && inp.type == "RGBA") {
				g.color = ui.t.LABEL_COL;
				g.drawString(tr(inp.name), nx + p(12), ny - p(3));
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				if (ui.getHover(lineh) && inp.tooltip != null) ui.tooltip(tr(inp.tooltip));
				var soc = inp;
				g.color = 0xff000000;
				g.fillRect(nx + w - p(38), ny - p(6), p(36), p(18));
				var val: kha.arrays.Float32Array = soc.default_value;
				g.color = kha.Color.fromFloats(val[0], val[1], val[2]);
				var rx = nx + w - p(37);
				var ry = ny - p(5);
				var rw = p(34);
				var rh = p(16);
				g.fillRect(rx, ry, rw, rh);
				var ix = ui.inputX - wx;
				var iy = ui.inputY - wy;
				if (ui.inputStarted && ix > rx && iy > ry && ix < rx + rw && iy < ry + rh) {
					_inputStarted = ui.inputStarted = false;
					rgbaPopup(ui, nhandle, soc.default_value, Std.int(rx), Std.int(ry + ui.ELEMENT_H()));
				}
			}
			else if (!isLinked && inp.type == "VECTOR" && inp.display == 1) {
				g.color = ui.t.LABEL_COL;
				g.drawString(tr(inp.name), nx + p(12), ny - p(3));
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				if (ui.getHover(lineh) && inp.tooltip != null) ui.tooltip(tr(inp.tooltip));

				ny += lineh / 2;
				ui._y = ny;
				var min = inp.min != null ? inp.min : 0.0;
				var max = inp.max != null ? inp.max : 1.0;
				var textOff = ui.t.TEXT_OFFSET;
				ui.t.TEXT_OFFSET = 6;
				var val: kha.arrays.Float32Array = inp.default_value;
				val[0] = ui.slider(nhandle.nest(maxButtons).nest(i).nest(0, {value: val[0]}), "X", min, max, true, 100, true, Left);
				if (ui.isHovered && inp.tooltip != null) ui.tooltip(tr(inp.tooltip));
				val[1] = ui.slider(nhandle.nest(maxButtons).nest(i).nest(1, {value: val[1]}), "Y", min, max, true, 100, true, Left);
				if (ui.isHovered && inp.tooltip != null) ui.tooltip(tr(inp.tooltip));
				val[2] = ui.slider(nhandle.nest(maxButtons).nest(i).nest(2, {value: val[2]}), "Z", min, max, true, 100, true, Left);
				if (ui.isHovered && inp.tooltip != null) ui.tooltip(tr(inp.tooltip));
				ui.t.TEXT_OFFSET = textOff;
				ny += lineh * 2.5;
			}
			else {
				g.color = ui.t.LABEL_COL;
				g.drawString(tr(inp.name), nx + p(12), ny - p(3));
				ui._x = nx;
				ui._y = ny;
				ui._w = w;
				if (ui.getHover(lineh) && inp.tooltip != null) ui.tooltip(tr(inp.tooltip));
			}
			if (onSocketReleased != null && ui.inputEnabled && (ui.inputReleased || ui.inputReleasedR)) {
				if (ui.inputX > wx + nx && ui.inputX < wx + nx + w && ui.inputY > wy + ny && ui.inputY < wy + ny + lineh) {
					onSocketReleased(inp);
					socketReleased = true;
				}
			}
		}

		ui._x = uiX;
		ui._y = uiY;
		ui._w = uiW;
		ui.inputStarted = _inputStarted;
	}

	public function rgbaPopup(ui: Zui, nhandle: zui.Zui.Handle, val: kha.arrays.Float32Array, x: Int, y: Int) {
		popup(x, y, Std.int(140 * scaleFactor), Std.int(ui.t.ELEMENT_H * 10), function(ui: Zui) {
			nhandle.color = kha.Color.fromFloats(val[0], val[1], val[2]);
			Ext.colorWheel(ui, nhandle, false, null, true, function () {
				colorPickerCallback = function (color: kha.Color) {
					val[0] = color.R;
					val[1] = color.G;
					val[2] = color.B;
					ui.changed = true;
				};
			});
			val[0] = nhandle.color.R; val[1] = nhandle.color.G; val[2] = nhandle.color.B;
		});
	}

	public function drawLink(ui: Zui, x1: Float, y1: Float, x2: Float, y2: Float, highlight: Bool = false) {
		var g = ui.g;
		var c1: kha.Color = ui.t.LABEL_COL;
		var c2: kha.Color = ui.t.ACCENT_SELECT_COL;
		g.color = highlight ? kha.Color.fromBytes(c1.Rb, c1.Gb, c1.Bb, 210) : kha.Color.fromBytes(c2.Rb, c2.Gb, c2.Bb, 210);
		if (ui.t.LINK_STYLE == Line) {
			g.drawLine(x1, y1, x2, y2, 1.0);
			g.color = highlight ? kha.Color.fromBytes(c1.Rb, c1.Gb, c1.Bb, 150) : kha.Color.fromBytes(c2.Rb, c2.Gb, c2.Bb, 150); // AA
			g.drawLine(x1 + 0.5, y1, x2 + 0.5, y2, 1.0);
			g.drawLine(x1 - 0.5, y1, x2 - 0.5, y2, 1.0);
			g.drawLine(x1, y1 + 0.5, x2, y2 + 0.5, 1.0);
			g.drawLine(x1, y1 - 0.5, x2, y2 - 0.5, 1.0);
		}
		else if (ui.t.LINK_STYLE == CubicBezier) {
			g.drawCubicBezier([x1, x1 + Math.abs(x1 - x2) / 2, x2 - Math.abs(x1 - x2) / 2, x2], [y1, y1, y2, y2], 30, highlight ? 2.0 : 1.0);
		}
	}

	public function removeNode(n: TNode, canvas: TNodeCanvas) {
		if (n == null) return;
		var i = 0;
		while (i < canvas.links.length) {
			var l = canvas.links[i];
			if (l.from_id == n.id || l.to_id == n.id) {
				canvas.links.splice(i, 1);
			}
			else i++;
		}
		canvas.nodes.remove(n);
		if (onNodeRemove != null) {
			onNodeRemove(n);
		}
	}

	var popupX = 0;
	var popupY = 0;
	var popupW = 0;
	var popupH = 0;
	var popupCommands: Zui->Void = null;
	function popup(x: Int, y: Int, w: Int, h: Int, commands: Zui->Void) {
		popupX = x;
		popupY = y;
		popupW = w;
		popupH = h;
		popupCommands = commands;
	}
}

typedef CanvasControl = {
	var panX: Float;
	var panY: Float;
	var zoom: Float;
}

typedef TNodeCanvas = {
	var name: String;
	var nodes: Array<TNode>;
	var links: Array<TNodeLink>;
}

typedef TNode = {
	var id: Int;
	var name: String;
	var type: String;
	var x: Float;
	var y: Float;
	var inputs: Array<TNodeSocket>;
	var outputs: Array<TNodeSocket>;
	var buttons: Array<TNodeButton>;
	var color: Int;
	@:optional var width: Null<Float>;
	@:optional var tooltip: String;
}

typedef TNodeSocket = {
	var id: Int;
	var node_id: Int;
	var name: String;
	var type: String;
	var color: Int;
	var default_value: Dynamic;
	@:optional var min: Null<Float>;
	@:optional var max: Null<Float>;
	@:optional var precision: Null<Float>;
	@:optional var display: Null<Int>;
	@:optional var tooltip: String;
}

typedef TNodeLink = {
	var id: Int;
	var from_id: Int;
	var from_socket: Int;
	var to_id: Int;
	var to_socket: Int;
}

typedef TNodeButton = {
	var name: String;
	var type: String;
	@:optional var output: Null<Int>;
	@:optional var default_value: Dynamic;
	@:optional var data: Dynamic;
	@:optional var min: Null<Float>;
	@:optional var max: Null<Float>;
	@:optional var precision: Null<Float>;
	@:optional var height: Null<Float>;
	@:optional var tooltip: String;
}
