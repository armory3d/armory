
Building API docs:
- Install [Haxe](https://haxe.org/) and [dox](https://github.com/HaxeFoundation/dox)
- Open terminal at `armsdk/api`
- Run `haxe api.hxml -xml build/api.xml -D doc-gen` to build xml description
- Run `haxe dox.hxml` to generate html into the `pages/` directory
