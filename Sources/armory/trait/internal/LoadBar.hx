package armory.trait.internal;

class LoadBar {

	public static function render(g:kha.graphics2.Graphics) {
		if (iron.Scene.active != null && iron.Scene.active.ready) {
			iron.App.removeRender2D(LoadBar.render);
			return;
		}

		g.color = 0xffcf2b43;
		g.fillRect(0, App.h() - 4, App.w() / Main.projectAssets * iron.data.Data.assetsLoaded, 4);
	}
}
