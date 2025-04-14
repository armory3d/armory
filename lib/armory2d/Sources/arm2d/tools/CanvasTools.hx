package arm2d.tools;

// Zui
import zui.Zui;
import armory.ui.Canvas;

class CanvasTools {

	public static function makeElem(cui:Zui, canvas:TCanvas, type:ElementType) {
		var name = "";
		var height = cui.t.ELEMENT_H;
		var alignment = Align.Left;

		switch (type) {
		case ElementType.Text:
			name = unique("Text", canvas.elements, "name");
		case ElementType.Button:
			name = unique("Button", canvas.elements, "name");
			alignment = Align.Center;
		case ElementType.Image:
			name = unique("Image", canvas.elements, "name");
			height = 100;
		case ElementType.FRectangle:
			name = unique("Filled_Rectangle", canvas.elements, "name");
			height = 100;
		case ElementType.FCircle:
			name = unique("Filled_Circle", canvas.elements, "name");
		case ElementType.Rectangle:
			name = unique("Rectangle", canvas.elements, "name");
			height = 100;
		case ElementType.FTriangle:
			name = unique("Filled_Triangle", canvas.elements, "name");
		case ElementType.Triangle:
			name = unique("Triangle", canvas.elements, "name");
		case ElementType.Circle:
			name = unique("Circle", canvas.elements, "name");
		case ElementType.Check:
			name = unique("Check", canvas.elements, "name");
		case ElementType.Radio:
			name = unique("Radio", canvas.elements, "name");
		case ElementType.Combo:
			name = unique("Combo", canvas.elements, "name");
		case ElementType.Slider:
			name = unique("Slider", canvas.elements, "name");
			alignment = Align.Right;
		case ElementType.TextInput:
			name = unique("TextInput", canvas.elements, "name");
		case ElementType.KeyInput:
			name = unique("KeyInput", canvas.elements, "name");
		case ElementType.TextArea:
			name = unique("TextArea", canvas.elements, "name");
		case ElementType.ProgressBar:
			name = unique("Progress_bar", canvas.elements, "name");
		case ElementType.CProgressBar:
			name = unique("CProgress_bar", canvas.elements, "name");
		case ElementType.Empty:
			name = unique("Empty", canvas.elements, "name");
			height = 100;
		}
		var elem:TElement = {
			id: Canvas.getElementId(canvas),
			type: type,
			name: name,
			event: "",
			x: 0,
			y: 0,
			width: 150,
			height: height,
			rotation: 0,
			text: "My " + name,
			asset: "",
			progress_at: 0,
			progress_total: 100,
			strength: 1,
			alignment: cast(alignment, Int),
			anchor: 0,
			parent: null,
			children: [],
			visible: true
		};
		canvas.elements.push(elem);
		return elem;
	}

	/**
	 * Generates a unique string for a given array based on the string s.
	 *
	 * @param s The string that is returned in a unique form
	 * @param data The array where the string should be unique
	 * @param elemAttr The name of the attribute of the data elements to be compared with the string.
	 * @param counter=-1 Internal use only, do not overwrite!
	 * @return String A unique string in the given array
	 */
	 //TODO: Here
	public static function unique(s:String, data:Array<Dynamic>, elemAttr:String, counter=-1): String {
		var originalName = s;

		// Reconstruct the original name
		var split = s.lastIndexOf(".");
		if (split != -1) {
			// .001, .002...
			var suffix = s.substring(split);
			if (suffix.length == 4) {
				originalName = s.substring(0, split);
			}
		}

		for (elem in data) {
			if (Reflect.getProperty(elem, elemAttr) == s) {
				if (counter > -1) {
					counter++;
					var counterLen = Std.string(counter).length;
					if (counterLen > 3) counterLen = 3;
					var padding = ".";
					for (i in 0...3 - counterLen) {
						padding += "0";
					}

					return unique(originalName + padding + Std.string(counter), data, elemAttr, counter);

				} else {
					return unique(originalName, data, elemAttr, 0);
				}
			}
		}
		return s;
	}

	public static function moveElem(canvas:TCanvas, elem:TElement, d:Int) {
		var ar = canvas.elements;
		var i = ar.indexOf(elem);
		var p = elem.parent;

		while (true) {
			i += d;
			if (i < 0 || i >= ar.length) break;

			if (ar[i].parent == p) {
				ar.remove(elem);
				ar.insert(i, elem);
				break;
			}
		}
	}

	public static function removeElem(canvas:TCanvas, elem:TElement) {
		if (elem.children != null) for (id in elem.children) removeElem(canvas, CanvasTools.elemById(canvas, id));
		canvas.elements.remove(elem);
		if (elem.parent != null) {
			CanvasTools.elemById(canvas, elem.parent).children.remove(elem.id);
			elem.parent = null;
		}
	}

	public static function elemById(canvas: TCanvas, id: Int): TElement {
		for (e in canvas.elements) if (e.id == id) return e;
		return null;
	}

	public static function unparent(canvas:TCanvas, elem:TElement) {
		var parent = CanvasTools.elemById(canvas, elem.parent);
		if (parent != null) {
			elem.x += Math.absx(canvas, parent);
			elem.y += Math.absy(canvas, parent);
			elem.parent = null;
			parent.children.remove(elem.id);
		}
	}

	public static function setParent(canvas:TCanvas, elem:TElement, parent:TElement) {
		var oldParent = CanvasTools.elemById(canvas, elem.parent);
		if (oldParent == parent) return;
		unparent(canvas, elem); //Unparent first if we already have a parent

		if (parent != null) { //Parent
			if (parent.children == null) elem.children = [];
			parent.children.push(elem.id);
			elem.parent = parent.id;
			elem.x -= Math.absx(canvas, parent);
			elem.y -= Math.absy(canvas, parent);
		}
	}

	public static function duplicateElem(canvas:TCanvas, elem:TElement, parentId:Null<Int> = null):TElement {
		if (elem != null) {
			if (parentId == null) parentId = elem.parent;
			var dupe:TElement = {
				id: Canvas.getElementId(canvas),
				type: elem.type,
				name: elem.name,
				event: elem.event,
				x: elem.x + 10,
				y: elem.y + 10,
				width: elem.width,
				height: elem.height,
				rotation: elem.rotation,
				text: elem.text,
				asset: elem.asset,
				color: elem.color,
				color_text: elem.color_text,
				color_hover: elem.color_hover,
				color_press: elem.color_press,
				color_progress: elem.color_progress,
				progress_at: elem.progress_at,
				progress_total: elem.progress_total,
				strength: elem.strength,
				anchor: elem.anchor,
				parent: parentId,
				children: [],
				visible: elem.visible
			};
			canvas.elements.push(dupe);
			if (parentId != null) {
				var parentElem = CanvasTools.elemById(canvas, parentId);
				parentElem.children.push(dupe.id);
				if (elem.parent != parentId) {
					dupe.x = elem.x;
					dupe.y = elem.y;
				}
			}
			for(child in elem.children) {
				duplicateElem(canvas, CanvasTools.elemById(canvas, child), dupe.id);
			}

			return dupe;
		}
		return null;
	}
}
