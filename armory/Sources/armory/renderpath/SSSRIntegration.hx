// ============================================================================
// SSSR (Stochastic Screen Space Reflections) RenderPath 集成
// 随机化屏幕空间反射 - 蓝噪声采样 + 时间累积
// ============================================================================

package armory.renderpath;

import iron.RenderPath;
import iron.Scene;

class SSSRIntegration {

    #if (rp_sssr)
    
    static var path: RenderPath;
    
    public static function init(_path: RenderPath) {
        path = _path;
        
        // 加载 SSSR 着色器
        path.loadShader("shader_datas/ssr_pass/ssr_pass");
        
        // 创建蓝噪声纹理
        createBlueNoiseTexture();
        
        // 创建历史缓冲区
        createHistoryBuffers();
    }
    
    static function createBlueNoiseTexture() {
        // 64x64 蓝噪声纹理
        var blueNoise = new RenderTargetRaw();
        blueNoise.name = "sssrBlueNoiseTex";
        blueNoise.width = 64;
        blueNoise.height = 64;
        blueNoise.format = "R8";
        blueNoise.is_target = false;
        path.createRenderTarget(blueNoise);
    }
    
    static function createHistoryBuffers() {
        // 历史颜色缓冲区
        var historyColor = new RenderTargetRaw();
        historyColor.name = "sssrHistoryColor";
        historyColor.width = 0;  // 全屏
        historyColor.height = 0;
        historyColor.format = "RGBA32";
        historyColor.is_target = true;
        path.createRenderTarget(historyColor);
        
        // 历史深度缓冲区
        var historyDepth = new RenderTargetRaw();
        historyDepth.name = "sssrHistoryDepth";
        historyDepth.width = 0;
        historyDepth.height = 0;
        historyDepth.format = "D32";
        historyDepth.is_target = true;
        path.createRenderTarget(historyDepth);
    }
    
    public static function renderSSSR() {
        // 执行 SSSR 反射 Pass
        path.setTarget("sssr_out");
        path.drawShader("ssr_pass");
    }
    
    public static function updateFrameIndex(frameIndex: Int) {
        // 更新帧索引用于蓝噪声采样
        // 在 shader 中通过 sssrFrameIndex 常量传递
    }
    
    #end
}
