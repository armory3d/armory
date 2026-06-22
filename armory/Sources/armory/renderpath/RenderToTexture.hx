package armory.renderpath;

class RenderToTexture{
    /**
		The current kha g2 object to be rendered to.
	**/
    public static var g: Null<kha.graphics2.Graphics> = null;

	public static inline function ensureEmptyRenderTarget(location: String){
		assert(Error, g == null, 
			'render texture already exists at $location. Please clear the texture before setting.
			If used in logic node, please consult its documentation.'
		);
	}

    public static inline function ensure2DContext(location: String) {
		assert(Error, g != null,
			'$location must be executed inside of a render2D callback. If used in logic node, please consult its documentation.'
		);
	}
}