// ============================================================================
// DDGI RenderPath 集成
// 将 DDGI 探针更新和渲染集成到延迟渲染管线
// ============================================================================

package armory.renderpath;

import iron.RenderPath;
import iron.Scene;

class DDGIIntegration {

    #if (rp_ddgi)
    
    static var path: RenderPath;
    
    public static function init(_path: RenderPath) {
        path = _path;
        
        // 加载 DDGI 着色器
        path.loadShader("shader_datas/ddgi_update_pass/ddgi_update_pass");
        path.loadShader("shader_datas/ddgi_pass/ddgi_pass");
        
        // 创建 3D 探针纹理
        createProbeGrid();
    }
    
    static function createProbeGrid() {
        var probeGrid = new RenderTargetRaw();
        probeGrid.name = "ddgiProbeGrid";
        probeGrid.width = 16;  // 探针网格 X 分辨率
        probeGrid.height = 16; // 探针网格 Y 分辨率
        probeGrid.depth = 16;  // 探针网格 Z 分辨率 (3D 纹理)
        probeGrid.format = "RGBA32";
        probeGrid.is_target = true;
        path.createRenderTarget(probeGrid);
    }
    
    public static function updateProbes() {
        // 执行 DDGI 探针更新 (Compute Shader)
        path.setTarget("ddgiProbeGrid");
        path.drawShader("ddgi_update_pass");
    }
    
    public static function renderDDGI() {
        // 渲染 DDGI 间接光照
        path.setTarget("ddgi_out");
        path.drawShader("ddgi_pass");
    }
    
    #end
}
