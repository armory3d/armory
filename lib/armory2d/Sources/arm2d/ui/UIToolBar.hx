package arm2d.ui;

// Zui
import zui.Id;
import zui.Zui;
import armory.ui.Canvas.TCanvas;
import armory.ui.Canvas.ElementType;

// Editor
import arm2d.tools.CanvasTools;

class UIToolBar {

	public static function renderToolbar(ui:Zui, cui:Zui, canvas: TCanvas, width:Int) {

		if (ui.window(Id.handle(), 0, 0, width, kha.System.windowHeight())) {
			ui.text("Add Elements:");

			if (ui.panel(Id.handle({selected: true}), "Basic")) {
				ui.indent();

				drawToolbarItem(ui, cui, canvas, "Empty", Empty, "Create an empty element");
				drawToolbarItem(ui, cui, canvas, "Text", Text, "Create a text element");
				drawToolbarItem(ui, cui, canvas, "Image", Image, "Create an image element");

				ui.unindent();
			}

			// ui.button("VLayout");
			// ui.button("HLayout");
			if (ui.panel(Id.handle({selected: true}), "Buttons")){
				ui.indent();

				drawToolbarItem(ui, cui, canvas, "Button", Button, "Create a button element");
				drawToolbarItem(ui, cui, canvas, "Check", Check, "Create a checkbox element");
				drawToolbarItem(ui, cui, canvas, "Radio", Radio, "Create a inline-radio element");

				ui.unindent();
			}

			if (ui.panel(Id.handle({selected: true}), "Inputs")){
				ui.indent();

				drawToolbarItem(ui, cui, canvas, "Text Input", TextInput, "Create a text input element");
				drawToolbarItem(ui, cui, canvas, "Text Area", TextArea, "Create a text area element");
				drawToolbarItem(ui, cui, canvas, "Key Input", KeyInput, "Create a key input element");
				drawToolbarItem(ui, cui, canvas, "Combo Box", Combo, "Create a combo box element");
				drawToolbarItem(ui, cui, canvas, "Slider", Slider, "Create a slider element");

				ui.unindent();
			}

			if (ui.panel(Id.handle({selected: true}), "Shapes")){
				ui.indent();

				drawToolbarItem(ui, cui, canvas, "Rect", Rectangle, "Create a rectangle shape element");
				drawToolbarItem(ui, cui, canvas, "Fill Rect", FRectangle, "Create a filled rectangle shape element");
				drawToolbarItem(ui, cui, canvas, "Circle", Circle, "Create a circle shape element");
				drawToolbarItem(ui, cui, canvas, "Fill Circle", FCircle, "Create a filled circle shape element");
				drawToolbarItem(ui, cui, canvas, "Triangle", Triangle, "Create a triangle shape element");
				drawToolbarItem(ui, cui, canvas, "Fill Triangle", FTriangle, "Create a filled triangle shape element");

				ui.unindent();
			}

			if (ui.panel(Id.handle({selected: true}), "Progress Bars")){
				ui.indent();

				drawToolbarItem(ui, cui, canvas, "RectPB", ProgressBar, "Create a rectangular progress bar");
				drawToolbarItem(ui, cui, canvas, "CircularPB", CProgressBar, "Create a circular progress bar");

				ui.unindent();
			}
		}
	}

	static function drawToolbarItem(ui: Zui, cui: Zui, canvas: TCanvas, label: String, elemType: ElementType, tooltip: String) {
		if (ui.button(label)) {
			Editor.selectedElem = CanvasTools.makeElem(cui, canvas, elemType);
		}

		if (ui.isHovered) ui.tooltip(tooltip);
	}
}
