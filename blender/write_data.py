import bpy
import os

# Write khafile.js
def write_khafilejs(shader_references):
	
	# Merge duplicates and sort
	shader_references = sorted(list(set(shader_references)))

	with open('khafile.js', 'w') as f:
			f.write(
"""// Auto-generated
var project = new Project('""" + bpy.data.worlds[0]['CGProjectName'] + """');

project.addSources('Sources');
project.addShaders('Sources/Shaders/**');
project.addAssets('Assets/**');

project.addLibrary('cyclesgame');
project.addAssets('Libraries/cyclesgame/Assets/**');
""")

			for ref in shader_references:
				# ArmoryExporter.pipeline_pass instead of split
				base_name = ref.split('_', 1)[0] + "/"
				f.write("project.addAssets('Libraries/cyclesgame/compiled/ShaderResources/" + base_name + "" + ref + ".json');\n")
				f.write("project.addShaders('Libraries/cyclesgame/compiled/Shaders/" + base_name + "" + ref + ".frag.glsl');\n")
				f.write("project.addShaders('Libraries/cyclesgame/compiled/Shaders/" + base_name + "" + ref + ".vert.glsl');\n")

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
	public static inline var projectScene = '""" + str(bpy.data.worlds[0]['CGProjectScene']) + """';
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
		kha.System.init(projectName, projectWidth, projectHeight, function() {
			new lue.App(cycles.Root);
		});
	}
}
""")
