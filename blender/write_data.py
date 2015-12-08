import bpy
import os

# Write khafile.js
def write_khafilejs():
	with open('khafile.js', 'w') as f:
			f.write(
"""// Auto-generated
var project = new Project('""" + bpy.data.worlds[0]['CGProjectName'] + """');

project.addSources('Sources');
project.addShaders('Sources/Shaders/**');
project.addAssets('Assets/**');
project.addLibrary('lue');
project.addLibrary('cyclesgame');
project.addLibrary('haxebullet');

return project;
""")

# Write Main.hx
def write_main():
	#if not os.path.isfile('Sources/Main.hx'):
	with open('Sources/Main.hx', 'w') as f:
		f.write(
"""// Auto-generated
package ;
class Main {
	static inline var projectName = '""" + bpy.data.worlds[0]['CGProjectName'] + """';
	static inline var projectWidth = """ + str(bpy.data.worlds[0]['CGProjectWidth']) + """;
	static inline var projectHeight = """ + str(bpy.data.worlds[0]['CGProjectHeight']) + """;
	public static function main() {
		lue.sys.CompileTime.importPackage('lue.trait');
		lue.sys.CompileTime.importPackage('cycles.trait');
		lue.sys.CompileTime.importPackage('""" + bpy.data.worlds[0]['CGProjectPackage'] + """');
		#if js
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
