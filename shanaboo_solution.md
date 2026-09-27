 ```diff
--- a/armory/Sources/armory/renderpath/RenderPathDeferred.hx
+++ b/armory/Sources/armory/renderpath/RenderPathDeferred.hx
@@ -1,5 +1,6 @@
 package armory.renderpath;
 
+import iron.math.Vec4;
 import iron.data.SceneFormat;
 import iron.data.RenderPath;
 import iron.data.RenderPath.RenderPass;
@@ -10,6 +11,7 @@
 	public static var screenAlignedQuadVB: kha.graphics4.VertexBuffer;
 	public static var screenAlignedQuadIB: kha.graphics4.IndexBuffer;
 	public static var pointLightData: kha.FastFloatBuffer;
+	public static var boxProjectedCubemapData: kha.FastFloatBuffer;
 
 	public static function init(_path: RenderPath) {
 		path = _path;
@@ -21,6 +23,9 @@
 		if (pointLightData == null) {
 			pointLightData = new kha.FastFloatBuffer(20 * 1024);
 		}
+		if (boxProjectedCubemapData == null) {
+			boxProjectedCubemapData = new kha.FastFloatBuffer(8);
+		}
 
 		// Mesh
 		var vertexLayout = new kha.graphics4.VertexLayout([
@@ -44,6 +49,10 @@
 		screenAlignedQuadIB.unlock();
 	}
 
+	public static function setBoxProjectedCubemapData(boxMin: Vec4, boxMax: Vec4) {
+		boxProjectedCubemapData = new kha.FastFloatBuffer(8);
+		boxProjectedCubemapData.set(0, boxMin.x);
+		boxProjectedCubemapData.set(1, boxMin.y);
+		boxProjectedCubemapData.set(2, boxMin.z);
+		boxProjectedCubemapData.set(3, 0.0);
+		boxProjectedCubemapData.set(4, boxMax.x);
+		boxProjectedCubemapData.set(5, boxMax.y);
+		boxProjectedCubemapData.set(6, boxMax.z);
+		boxProjectedCubemapData.set(7, 0.0);
+	}
+
 	public static function commands() {
 
 		if (path == null) return;
@@ -51,6 +60,7 @@
 		var camera = iron.Scene.active.camera;
 		var g = iron.App.graphics4;
 		var rt = path.renderTargets;
+		var boxProjectedCubemap = iron.Scene.active.raw.box_projected_cubemap;
 
 		#if rp_shadows
 		{
@@ -168,6 +178,11 @@
 				path.bindTarget("_main", "gbufferD");
 				#if rp_gbuffer2
 				path.bindTarget("gbuffer2", "gbuffer2");
+				#end
+				#if rp_box_projected_cubemap
+				if (boxProjectedCubemap != null) {
+					path.bindTarget("boxProjectedCubemapData",Internal, "boxProjectedCubemapData");
+				}
 				#end
 				path.drawMeshes("translucent");
 				path.end();
@@ -232,6 +247,11 @@
 				path.bindTarget("_main", "gbufferD");
 				#if rp_gbuffer2
 				path.bindTarget("gbuffer2", "gbuffer2");
+				#end
+				#if rp_box_projected_cubemap
+				if (boxProjectedCubemap != null) {
+					path.bindTarget("boxProjectedCubemapData",Internal, "boxProjectedCubemapData");
+				}
 				#end
 				path.drawMeshes("translucent");
 				path.end();
@@ -296,6 +316,11 @@
 				path.bindTarget("_main", "gbufferD");
 				#if rp_gbuffer2
 				path.bindTarget("gbuffer2", "gbuffer2");
+				#end
+				#if rp_box_projected_cubemap
+				if (boxProjectedCubemap != null) {
+					path.bindTarget("boxProjectedCubemapData",Internal, "boxProjectedCubemapData");
anticubemapData");
+				}
 				#end
 				path.drawMeshes("translucent");
 				path.end();
@@ -360,6 +385,11 @@
 				path.bindTarget("_main", "gbufferD");
 				#if rp_gbuffer2
 				path.bindTarget("gbuffer2", "gbuffer2");
+				#end
+				#if rp_box_projected_cubemap
+				if (boxProjectedCubemap != null) {
+					path.bindTarget("boxProjectedCubemapData",Internal, "boxProjectedCubemapData");
+				}
 				#end
 				path.drawMeshes("translucent");
 				path.end();
@@ -424,6 +454,11 @@
 				path.bindTarget("_main", "gbufferD");
 				#if rp_gbuffer2
 				path.bindTarget("gbuffer2", "gbuffer2");
+				#end
+				#if rp_box_projected_cubemap
+				if (boxProjectedCubemap != null) {
+					path.bindTarget("boxProjectedCubemapData",Internal, "boxProjectedCubemapData");
+				}
 				#end
 				path.drawMeshes("translucent");
 				path.end();
@@ -488,6 +523,11 @@
 				path.bindTarget("_main", "gbufferD");
 				#if rp_gbuffer2
 				path.bindTarget("gbuffer2", "gbuffer2");
+				#end
+				#if rp_box_projected_cubemap
+				if (boxProjectedCubemap != null) {
+					path.bindTarget("boxProjectedCubemapData",Internal, "boxProjectedCubemapData");
+				}
 				#end
 				path.drawMeshes("translucent");
 				path.end();
@@ -552,6 +592,11 @@
 				path.bindTarget("_main", "gbufferD");
 				#if rp_gbuffer2
 				path.bindTarget("gbuffer2", "gbuffer2");
+				#end
+				#if rp_box_projected_cubemap
+				if (boxProjectedCubemap != null) {
+					path.bindTarget("boxProjectedCubemapData",Internal, "boxProjectedCubemapData");
+				}
 				#end
 				path.drawMeshes("translucent");
 				path.end();
@@ -616,6 +661,11 @@
 				path.bindTarget("_main", "gbufferD");
 				#if rp_gbuffer2
 				path.bindTarget("gbuffer2", "gbuffer2");
+				#end
+				#if rp_box_projected_cubemap
+				if (boxProjectedCubemap != null) {
+					path.bindTarget("boxProject