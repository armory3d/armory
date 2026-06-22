package iron.system;

import kha.audio1.AudioChannel;

/**
	Audio playback. This class wraps around `kha.audio1.Audio`.
**/
class Audio {

#if arm_audio

	public function new() {}

	/**
		Plays the given sound.

		If `stream` is `true` and the sound has compressed data, it is streamed
		from disk instead of being fully loaded into memory. This is useful for
		longer sounds such as background music.

		This function returns `null` if:

		- there is no unoccupied audio channel available for playback.
		- the sound has compressed data only but `stream` is `false`. In this
		  case, call `kha.Sound.uncompress()` first.
	**/
	public static function play(sound: kha.Sound, loop = false, stream = false): Null<AudioChannel> {
		if (stream && sound.compressedData != null) {
			return kha.audio1.Audio.stream(sound, loop);
		}
		else if (sound.uncompressedData != null) {
			return kha.audio1.Audio.play(sound, loop);
		}
		else return null;
	}

#end
}
