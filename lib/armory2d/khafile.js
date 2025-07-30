let project = new Project('Armory2D');

project.addSources('Sources');
project.addAssets('Assets/**/*.png');
project.addAssets('Assets/**/*.ttf');
project.addLibrary('zui');
project.addLibrary('armory');

resolve(project);
