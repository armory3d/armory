const fs = require('fs');
const path = require('path');

let flags = {
	name: 'Armory',
	package: 'org.armory3d',
	release: process.argv.indexOf("--debug") == -1,
	with_audio: true,
	with_worker: true,
	with_compute: true
};

const system = platform === Platform.Windows ? "win32" :
			   platform === Platform.Linux   ? "linux" :
			   platform === Platform.OSX     ? "macos" :
			   platform === Platform.Wasm    ? "wasm" :
			   platform === Platform.Android ? "android" :
			   platform === Platform.iOS     ? "ios" :
			   								   "unknown";

const build = flags.release ? 'release' : 'debug';
let root = __dirname;
const libdir = root + '/v8/libraries/' + system + '/' + build + '/';

let project = new Project(flags.name);
await project.addProject('Kinc');
project.cppStd = "c++17";
project.setDebugDir('Deployment');

if (fs.existsSync(process.cwd() + '/icon.png')) {
	project.icon = path.relative(__dirname, process.cwd()) + '/icon.png';
}

if (flags.with_audio) {
	project.addDefine('WITH_AUDIO');
}

if (flags.with_compute) {
	project.addDefine('WITH_COMPUTE');
}

project.addFile('Sources/main.cpp');

if (flags.with_worker) {
	project.addDefine('WITH_WORKER');
	project.addFile('Sources/worker.h');
	project.addFile('Sources/worker.cpp');
}

project.addIncludeDir('v8/include');

if (platform === Platform.Windows) {
	project.addLib('Dbghelp'); // Stack walk
	project.addLib('Dwmapi'); // DWMWA_USE_IMMERSIVE_DARK_MODE
	project.addLib('winmm'); // timeGetTime for V8
	project.addLib(libdir + 'v8_monolith');
	if (!flags.release) {
		project.addDefine('_HAS_ITERATOR_DEBUGGING=0');
		project.addDefine('_ITERATOR_DEBUG_LEVEL=0');
	}
}
else if (platform === Platform.Linux) {
	project.addLib('v8_monolith -L' + libdir);
	project.addDefine("KINC_NO_WAYLAND");
}
else if (platform === Platform.OSX) {
	project.addLib('v8/libraries/macos/release/libv8_monolith.a');
}

project.flatten();
resolve(project);
