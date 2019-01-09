* 2019-1-8: For any Armory blends created in Armory 0.5 or earlier you will have to take the following steps to migrate the blend for Armory 0.6:
  * You must visit the trait panel of each object that has a logic node trait. This will reload the node trait selections.
  * If there were any objects selected in the Armory Bake panel, they must be re-selected manually.
* 2018-12-21: If you are using Armory Updater, get Armory 0.6alpha from https://armory.itch.io/armory3d first (or clone the sdk from https://github.com/armory3d/armsdk). 0.6 builds are heavily wip - use at own risk!

* 2018-08-28: `LampObject` and `LampData` is now `LightObject` and `LightData`
* 2018-06-01: 'Not Equal' has been removed from the Gate logic node. Use 'Equal' and 'False' output socket instead.
* 2017-11-20: Use `armory.trait.physics.*` instead of `armory.trait.internal.*` to access physics traits.
