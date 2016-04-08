import bpy
import os

# Write khafile.js
def write_khafilejs(shader_references, asset_references):
	
	# Merge duplicates and sort
	shader_references = sorted(list(set(shader_references)))
	asset_references = sorted(list(set(asset_references)))

	with open('khafile.js', 'w') as f:
			f.write(
"""// Auto-generated
var project = new Project('""" + bpy.data.worlds[0]['CGProjectName'] + """');

project.addSources('Sources');
project.addShaders('Sources/Shaders/**');
project.addAssets('Assets/**');

project.addLibrary('cyclesgame');
""")

			for ref in shader_references: # Shaders
				f.write("project.addShaders('" + ref + ".frag.glsl');\n")
				f.write("project.addShaders('" + ref + ".vert.glsl');\n")
			
			for ref in asset_references: # Assets
				f.write("project.addAssets('" + ref + "');\n")

			if bpy.data.worlds[0]['CGPhysics'] != 0:
				f.write("\nproject.addDefine('WITH_PHYSICS')\n")
				f.write("project.addLibrary('haxebullet')\n")

			f.write("\nreturn project;\n")

# Write Main.hx
def write_main():
	#if not os.path.isfile('Sources/Main.hx'):
	with open('Sources/Main.hx', 'w') as f:
		f.write(
"""// Auto-generated
package ;
class Main {
	public static inline var projectName = '""" + bpy.data.worlds[0]['CGProjectName'] + """';
	public static inline var projectPackage = '""" + bpy.data.worlds[0]['CGProjectPackage'] + """';
	static inline var projectWidth = """ + str(bpy.data.worlds[0]['CGProjectWidth']) + """;
	static inline var projectHeight = """ + str(bpy.data.worlds[0]['CGProjectHeight']) + """;
	static inline var projectSamplesPerPixel = """ + str(bpy.data.worlds[0]['CGProjectSamplesPerPixel']) + """;
	public static inline var projectScene = '""" + str(bpy.data.worlds[0]['CGProjectScene']) + """';
	public static inline var texEnvironment = '""" + bpy.data.cameras[0].world_envtex_name.rsplit('.', 1)[0] + """';
	public static inline var texEnvironmentMipmaps = """ + str(bpy.data.cameras[0].world_envtex_num_mips) + """;
	public static function main() {
		lue.sys.CompileTime.importPackage('lue.trait');
		lue.sys.CompileTime.importPackage('cycles.trait');
		lue.sys.CompileTime.importPackage('""" + bpy.data.worlds[0]['CGProjectPackage'] + """');
		#if (js && WITH_PHYSICS)
		untyped __js__("
			function loadScript(url, callback) {
				var head = document.getElementsByTagName('head')[0];
				var script = document.createElement('script');
				script.type = 'text/javascript';
				script.src = url;
				script.onreadystatechange = callback;
				script.onload = callback;
				head.appendChild(script);
			}
		");
		untyped loadScript('ammo.js', start);
		#else
		start();
		#end
	}
	static function start() {
		kha.System.init({title: projectName, width: projectWidth, height: projectHeight, samplesPerPixel: projectSamplesPerPixel}, function() {
			new lue.App(cycles.Root);
		});
	}
}
""")
