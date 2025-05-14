package iron.system;

import kha.StorageFile;

class Storage {

	static var file: StorageFile = null;
	public static var data(get, set): Dynamic;
	static var _data: Dynamic = null;

	static function init() {
		file = kha.Storage.defaultFile();
		if (file != null) {
			_data = file.readObject();
			if (_data == null) _data = {};
			save();
		}
	}

	public static function save() {
		if (file != null) {
			file.writeObject(_data);
		}
	}

	public static function clear() {
		_data = {};
	}

	public static function set_data(d: Dynamic): Dynamic {
		return _data = d;
	}

	public static function get_data(): Dynamic {
		if (file == null) init();
		return _data;
	}
}
