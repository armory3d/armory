 ```diff
--- a/armory/Sources/armory/renderpath/Inc.hx
+++ b/armory/Sources/armory/renderpath/Inc.hx
@@ -1,6 +1,7 @@
 package armory.renderpath;
 
 import iron.RenderPath;
+import iron.math.Vec4;
 
 class Inc {
 
@@ -8,6 +9,9 @@
 	static var path:RenderPath;
 	static var loadedDeferredShader = false;
 	static var loadedVoxelShader = false;
+	
+	// Box-projected cubemap environment mapping
+	public static var boxProjectedCubemapEnabled = false;
 
 	public static function init(_path:RenderPath) {
 		path = _path;
@@ -15,6 +19,41 @@
 
 	public static function bindCubeMap() {
 		path.bindCubeMap("cubeMap");
+		// Bind box projection parameters if enabled
+		if (boxProjectedCubemapEnabled) {
+			var boxMin = new Vec4(-1.0, -1.0, -1.0, 0.0);
+			var boxMax = new Vec4(1.0, 1.0, 1.0, 0.0);
+			var boxCenter = new Vec4(0.0, 0.0, 0.0, 0.0);
+			// These will be overridden by material uniforms if set
+			path.setFloat3("boxMin", boxMin.x, boxMin.y, boxMin.z);
+			path.setFloat3("boxMax", boxMax.x, boxMax.y, boxMax.z);
+			path.setFloat3("boxCenter", boxCenter.x, boxCenter.y, boxCenter.z);
+		}
+	}
+
+	public static function setBoxProjectionParams(boxMin:Vec4, boxMax:Vec4, boxCenter:Vec4) {
+		path.setFloat3("boxMin", boxMin.x, boxMin.y, boxMin.z);
+		path.setFloat3("boxMax", boxMax.x, boxMax.y, boxMax.z);
+		path.setFloat3("boxCenter", boxCenter.x, boxCenter.y, boxCenter.z);
+	}
+
+	public static inline function getBoxProjectedCubemapFragment():String {
+		return
+"#ifdef _BoxProjectedCubemap\n" +
+"uniform vec3 boxMin;\n" +
+"uniform vec3 boxMax;\n" +
+"uniform vec3 boxCenter;\n" +
+"\n" +
+"vec3 getBoxProjectedCoord(vec3 worldPos, vec3 worldNormalReflected, vec3 envMapPos) {\n" +
+"	vec3 nrdir = normalize(worldNormalReflected);\n" +
+"	vec3 rbmax = (boxMax - worldPos) / nrdir;\n" +
+"	vec3 rbmin = (boxMin - worldPos) / nrdir;\n" +
+"	vec3 rbminmax;\n" +
+"	rbminmax.x = (nrdir.x > 0.0) ? rbmax.x : rbmin.x;\n" +
+"	rbminmax.y = (nrdir.y > 0.0) ? rbmax.y : rbmin.y;\n" +
+"	rbminmax.z = (nrdir.z > 0.0) ? rbmax.z : rbmin.z;\n" +
+"	float fa = min(min(rbminmax.x, rbminmax.y), rbminmax.z);\n" +
+"	vec3 posonbox = worldPos + nrdir * fa;\n" +
+"	return posonbox - boxCenter;\n" +
+"}\n" +
+"#endif\n";
 	}
 
 	public static function bindShadowMap() {
--- a/armory/Sources/armory/object/Uniforms.hx
+++ b/armory/Sources/armory/object/Uniforms.hx
@@ -1,6 +1,7 @@
 package armory.object;
 
 import iron.object.Object;
+import iron.math.Vec4;
 
 class Uniforms {
 
@@ -8,4 +9,20 @@
 		// Override per object
 		return false;
 	}
+
+	public static function setBoxProjection(object:Object, boxMin:Vec4, boxMax:Vec4, boxCenter:Vec4):Bool {
+		// Set box projection parameters for an object
+		// Returns true if the object has box projection enabled
+		if (object == null) return false;
+		
+		// Check if object has box projection property
+		var props = object.properties;
+		if (props != null && Reflect.hasField(props, "_boxProjectedCubemap")) {
+			var bpc = Reflect.field(props, "_boxProjectedCubemap");
+			boxMin.setFrom(bpc.boxMin);
+			boxMax.setFrom(bpc.boxMax);
+			boxCenter.setFrom(bpc.boxCenter);
+			return true;
+		}
+		return false;
+	}
 }
--- a/armory/Sources/armory/renderpath/RenderPathDeferred.hx
+++ b/armory/Sources/armory/renderpath/RenderPathDeferred.hx
@@ -1,6 +1,7 @@
 package armory.renderpath;
 
 import iron.RenderPath;
+import iron.math.Vec4;
 
 class RenderPathDeferred {
 
@@ -8,6 +9,10 @@
 	static var path:RenderPath;
 	static var v:Int;
 	static var t:Int;
+	
+	// Box projection parameters
+	static var boxMin = new Vec4(-1.0, -1.0, -1.0, 0.0);
+	static var boxMax = new Vec4(1.0, 1.0, 1.0, 0.0);
+	static var boxCenter = new Vec4(0.0, 0.0, 0.0, 0.0);
 
 	public static function init(_path:RenderPath) {
 		path = _path;
@@ -15,6 +20,11 @@
 
 	public static function bindCubeMap() {
 		path.bindCubeMap("cubeMap");
+		// Bind box projection parameters
+		if (Inc.boxProjectedCubemapEnabled) {
+			Inc.setBoxProjectionParams(boxMin, boxMax, boxCenter);
+		}
 	}
 
 	public static function render() {
--- a/armory/Sources/armory/renderpath/RenderPathForward.hx
+++ b/armory/Sources/armory/renderpath/RenderPathForward.hx
@@ -1,6 +1,7 @@
 package armory.renderpath;
 
 import iron.RenderPath;
+import iron.math.Vec4;
 
 class RenderPathForward {
 
@@ -8,6 +9,10 @@
 	static var path:RenderPath;
 	static var v:Int;
 	static var t:Int;
+	
+	// Box projection parameters
+	static var boxMin = new Vec