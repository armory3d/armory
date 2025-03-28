package arm2d;

// Zui
import armory.ui.Canvas;

// Editor
import arm2d.Path;
import arm2d.ui.UIProperties;

class Assets {

	public static function getImage(asset:TAsset):kha.Image {
		return Canvas.assetMap.get(asset.id);
	}

	public static function getFont(asset:TAsset):kha.Font {
		return Canvas.assetMap.get(asset.id);
	}

	public static function importAsset(canvas:TCanvas, path:String) {
		var abspath = Path.toAbsolute(path, Main.cwd);
		abspath = kha.System.systemId == "Windows" ? StringTools.replace(abspath, "/", "\\") : abspath;

		if (isPathImage(path)) {
			kha.Assets.loadImageFromPath(abspath, false, function(image:kha.Image) {
				var ar = path.split("/");
				var name = ar[ar.length - 1];
				var asset:TAsset = { name: name, file: path, id: Canvas.getAssetId(canvas) };
				canvas.assets.push(asset);
				Canvas.assetMap.set(asset.id, image);

				Editor.assetNames.push(name);
				UIProperties.hwin.redraws = 2;
			});
		}
		else if (isPathFont(path)) {
			kha.Assets.loadFontFromPath(abspath, function(font:kha.Font) {
				var ar = path.split("/");
				var name = ar[ar.length - 1];
				var asset:TAsset = { name: name, file: path, id: Canvas.getAssetId(canvas) };
				canvas.assets.push(asset);
				Canvas.assetMap.set(asset.id, font);

				Editor.assetNames.push(name);
				UIProperties.hwin.redraws = 2;
			});
		}
	}

	/**
	 * Imports all themes from '_themes.json'. If the file doesn't exist, the
	 * default light theme is used instead.
	 */
	public static function importThemes() {
		var themesDir = haxe.io.Path.directory(Main.prefs.path);
		var themesPath = haxe.io.Path.join([themesDir, "_themes.json"]);
		themesPath = kha.System.systemId == "Windows" ? StringTools.replace(themesPath, "/", "\\") : themesPath;

		try {
			kha.Assets.loadBlobFromPath(themesPath, function(b:kha.Blob) {
				Canvas.themes = haxe.Json.parse(b.toString());

				if (Canvas.themes.length == 0) {
					Canvas.themes.push(Reflect.copy(armory.ui.Themes.light));
				}
				if (Main.inst != null) Editor.selectedTheme = Canvas.themes[0];

			// Error handling for HTML5 target
			}, function(a:kha.AssetError) {
				Canvas.themes.push(Reflect.copy(armory.ui.Themes.light));
				if (Main.inst != null) Editor.selectedTheme = Canvas.themes[0];
			});
		}
		// Error handling for Krom, as the failed callback for loadBlobFromPath()
		// is currently not implemented in Krom
		catch (e: Dynamic) {
			Canvas.themes.push(Reflect.copy(armory.ui.Themes.light));
			if(Main.inst != null) Editor.selectedTheme = Canvas.themes[0];
		}
	}

	public static function save(canvas: TCanvas) {
		// Unpan
		canvas.x = 0;
		canvas.y = 0;

		saveCanvas(canvas);
		saveAssets(canvas);
		saveThemes();

		canvas.x = Editor.coffX;
		canvas.y = Editor.coffY;
	}

	public static function load(done: TCanvas->Void) {
		kha.Assets.loadBlobFromPath(Main.prefs.path, function(b: kha.Blob) {
			done(Canvas.parseCanvasFromBlob(b));
		});
	}

	static function saveCanvas(canvas: TCanvas) {
		#if kha_krom
		Krom.fileSaveBytes(Main.prefs.path, haxe.io.Bytes.ofString(haxe.Json.stringify(canvas)).getData());

		#elseif kha_debug_html5
		html5WriteFile(Main.prefs.path, haxe.Json.stringify(canvas));
		#end
	}

	static function saveAssets(canvas: TCanvas) {
		var filesPath = Main.prefs.path.substr(0, Main.prefs.path.length - 5); // .json
		filesPath += '.files';

		var filesList = '';
		for (a in canvas.assets) filesList += a.file + '\n';

		#if kha_krom
		Krom.fileSaveBytes(filesPath, haxe.io.Bytes.ofString(filesList).getData());

		#elseif kha_debug_html5
		html5WriteFile(filesPath, filesList);
		#end
	}

	static function saveThemes() {
		var themesPath = haxe.io.Path.join([haxe.io.Path.directory(Main.prefs.path), "_themes.json"]);

		#if kha_krom
		Krom.fileSaveBytes(themesPath, haxe.io.Bytes.ofString(haxe.Json.stringify(Canvas.themes)).getData());

		#elseif kha_debug_html5
		html5WriteFile(themesPath, haxe.Json.stringify(Canvas.themes));
		#end
	}

	#if kha_debug_html5
	static function html5WriteFile(filePath: String, data: String) {
		var fs = js.Syntax.code('require("fs");');
		var path = js.Syntax.code('require("path")');

		var filePath = path.resolve(js.Syntax.code('__dirname'), filePath);

		try { fs.writeFileSync(filePath, data); }
		catch (x: Dynamic) { trace('saving "${filePath}" failed'); }
	}
	#end

	public static function getEnumTexts():Array<String> {
		if(Main.inst==null) return [""];
		return Editor.assetNames.length > 0 ? Editor.assetNames : [""];
	}

	public static function getAssetIndex(canvas:TCanvas, asset:String):Int {
		for (i in 0...canvas.assets.length) if (asset == canvas.assets[i].name) return i + 1; // assetNames[0] = ""
		return 0;
	}

	/**
	 * Returns if the given path is a path to an image file.
	 * @param path The path of the asset
	 * @return Bool
	 */
	public static function isPathImage(path: String): Bool {
		var extension = haxe.io.Path.extension(path).toLowerCase();
		return extension == "jpg" || extension == "png" || extension == "k" || extension == "hdr";
	}
	/**
	 * Returns if the given path is a path to a font file.
	 * @param path The path of the asset
	 * @return Bool
	 */
	public static inline function isPathFont(path: String): Bool {
		return haxe.io.Path.extension(path).toLowerCase() == "ttf";
	}
}
