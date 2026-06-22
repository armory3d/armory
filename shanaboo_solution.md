 ```diff
--- a/armory/Sources/armory/renderpath/RenderPathCreator.hx
+++ b/armory/Sources/armory/renderpath/RenderPathCreator.hx
@@ -1,5 +1,6 @@
 package armory.renderpath;
 
+import armory.renderpath.Inc;
 import iron.RenderPath;
 
 class RenderPathCreator {
@@ -7,6 +8,7 @@ class RenderPathCreator {
 	public static var path:RenderPath;
 
 	public static function get():RenderPath {
+		Inc.init();
 		path = new RenderPath();
 		RenderPathCreator.path = path;
 		#if (rp_gi == "Voxel GI")
@@ -15,6 +17,7 @@ class RenderPathCreator {
 		#end
 		#if (rp_renderer == "Forward")
 		{
+			Inc.initForward();
 			armory.renderpath.Forward.init(path);
 			armory.renderpath.Forward.commands();
 		}
@@ -24,6 +27,7 @@ class RenderPathCreator {
 		}
 		#else
 		{
+			Inc.initDeferred();
 			armory.renderpath.Deferred.init(path);
 			armory.renderpath.Deferred.commands();
 		}
--- /dev/null
+++ b/armory/Sources/armory/renderpath/BoxProject.hx
@@ -0,0 +1,56 @@
+package armory.renderpath;
+
+import iron.math.Vec4;
+
+class BoxProject {
+	
+	public static var boxProjCenter:Vec4 = new Vec4(0.0, 0.0, 0.0);
+	public static var boxProjSize:Vec4 = new Vec4(1.0, 1.0, 1.0);
+	public static var boxProjBlend:Float = 1.0;
+	public static var boxProjEnabled:Bool = false;
+
+	public static function setBoxProjection(center:Vec4, size:Vec4, blend:Float = 1.0) {
+		boxProjCenter.setFrom(center);
+		boxProjSize.setFrom(size);
+		boxProjBlend = blend;
+		boxProjEnabled = true;
+	}
+
+	public static function disableBoxProjection() {
+		boxProjEnabled = false;
+	}
+
+	public static inline function getBoxProjectedCoords():Vec4 {
+		return new Vec4(
+			boxProjCenter.x,
+			boxProjCenter.y,
+			boxProjCenter.z,
+			boxProjBlend
+		);
+	}
+
+	public static inline function getBoxProjectedSize():Vec4 {
+		return new Vec4(
+			boxProjSize.x,
+			boxProjSize.y,
+			boxProjSize.z,
+			0.0
+		);
+	}
+
+	public static function applyUniforms(object:Dynamic) {
+		if (object == null) return;
+		var g = object;
+		if (g == null) return;
+		
+		if (Std.is(g, kha.graphics4.Graphics)) {
+			var gg: kha.graphics4.Graphics = cast g;
+			if (boxProjEnabled) {
+				gg.setFloat4(Inc.getBoxProjectedCenterLocation(), boxProjCenter.x, boxProjCenter.y, boxProjCenter.z, boxProjBlend);
+				gg.setFloat4(Inc.getBoxProjectedSizeLocation(), boxProjSize.x, boxProjSize.y, boxProjSize.z, 0.0);
+			}
+		}
+	}
+
+	public static function isEnabled():Bool {
+		return boxProjEnabled;
+	}
+}
--- /dev/null
+++ b/armory/Sources/armory/renderpath/BoxProjectShader.hx
@@ -0,0 +1,10 @@
+package armory.renderpath;
+
+class BoxProjectShader {
+	
+	public static var boxProjectedCenter:iron.math.Vec4 = null;
+	public static var boxProjectedSize:iron.math.Vec4 = null;
+	public static var boxProjectedBlend:Float = 1.0;
+	public static var boxProjectedEnabled:Bool = false;
+
+	public function new() {}
+}
--- a/armory/Sources/armory/renderpath/Inc.hx
+++ b/armory/Sources/armory/renderpath/Inc.hx
@@ -1,5 +1,6 @@
 package armory.renderpath;
 
+import kha.graphics4.Graphics;
 import iron.RenderPath;
 import iron.data.MaterialData;
 import iron.data.ShaderData;
@@ -9,6 +10,7 @@ import iron.object.MeshObject;
 import iron.math.Vec4;
 import iron.math.Mat4;
 import iron.Scene;
+import armory.renderpath.BoxProject;
 
 class Inc {
 
@@ -16,6 +18,12 @@ class Inc {
 	static var pointIndex = 0;
 	static var spotIndex = 0;
 
+	// Box projection uniforms
+	static var boxProjectedCenterLocation:ConstantLocation = null;
+	static var boxProjectedSizeLocation:ConstantLocation = null;
+	static var boxProjectedEnabledLocation:ConstantLocation = null;
+	static var boxProjectedInit:Bool = false;
+
 	public static function init() {
 		#if (rp_gi == "Voxel GI")
 		{
@@ -23,6 +31,7 @@ class Inc {
 			armory.renderpath.Voxelizer.init();
 		}
 		#end
+		boxProjectedInit = false;
 	}
 
 	public static function initDeferred() {
@@ -30,6 +39,9 @@ class Inc {
 
 	public static function initForward() {
 	}
+
+	public static function initBoxProjected(g:kha.graphics4.Graphics, shader:kha.graphics4.Shader) {
+	}
 
 	public static function bindShadowsCubeMap() {
 		#if (rp_shadowmap)
@@ -41,6 +53,46 @@ class Inc {
 		#end
 	}
 
+	public static function getBoxProjectedCenterLocation():ConstantLocation {
+		return boxProjectedCenterLocation;
+	}
+
+	public static function getBoxProjectedSizeLocation():ConstantLocation {
+		return boxProjectedSizeLocation;
+	}
+
+	public static function getBoxProjectedEnabledLocation():ConstantLocation {
+		return boxProjectedEnabledLocation;
+	}
+
+	public static function initBoxProjection(g:kha.graphics4.Graphics, shader:kha.graphics4.Shader) {
+		if (boxProjectedInit) return;
+		boxProjectedCenterLocation = shader.getConstantLocation("_boxProjectedCenter");
+		boxProjectedSizeLocation = shader.getConstantLocation("_boxProjectedSize");
+		boxProjectedEnabledLocation = shader.getConstantLocation("_boxProjectedEnabled");
+		boxProjectedInit = true;
+	}
+
+	public static function setBoxProjectionConstants(g:kha.graphics4.Graphics) {
+	