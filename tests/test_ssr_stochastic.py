import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestSSRStochasticShader(unittest.TestCase):
    def read(self, rel_path: str) -> str:
        return (ROOT / rel_path).read_text(encoding="utf-8")

    def test_shared_helper_is_available(self) -> None:
        shader = self.read("armory/Shaders/std/ssrs.glsl")
        self.assertIn('#include "std/math.glsl"', shader)
        self.assertIn("ssrGetStochasticDir", shader)

    def test_ssr_pass_uses_stochastic_helper(self) -> None:
        shader = self.read("armory/Shaders/ssr_pass/ssr_pass.frag.glsl")
        self.assertIn('#include "std/ssrs.glsl"', shader)
        self.assertIn("ssrGetStochasticDir(reflected, texCoord, roughness, ssrJitter)", shader)
        self.assertIn("vec4 rayCast(vec3 dir, float rayJitter)", shader)

    def test_water_pass_uses_stochastic_helper(self) -> None:
        shader = self.read("armory/Shaders/water_pass/water_pass.frag.glsl")
        self.assertIn('#include "std/ssrs.glsl"', shader)
        self.assertIn("ssrGetStochasticDir(reflected, texCoord, roughness, ssrJitter)", shader)
        self.assertIn("vec4 rayCast(vec3 dir, float rayJitter)", shader)

    def test_renderpath_still_wires_ssr(self) -> None:
        write_data = self.read("armory/blender/arm/write_data.py")
        make_renderpath = self.read("armory/blender/arm/make_renderpath.py")
        self.assertIn("assets.add_shader_pass('ssr_pass')", make_renderpath)
        self.assertIn("const float ssrJitter", write_data)


if __name__ == "__main__":
    unittest.main()
