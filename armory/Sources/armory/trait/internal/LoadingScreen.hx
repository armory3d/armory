package armory.trait.internal;

// To create a custom loading screen copy this file to blend_root/Sources/arm/LoadingScreen.hx

class LoadingScreen {

	public static function render(g: kha.graphics2.Graphics, assetsLoaded: Int, assetsTotal: Int) {
		g.color = 0xffcf2b43;
		g.fillRect(0, iron.App.h() - 6, iron.App.w() / assetsTotal * assetsLoaded, 6);
	}
}
