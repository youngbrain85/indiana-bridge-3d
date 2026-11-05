// Compress a display model in place with EXT_meshopt_compression, used by blender_render_model.py.
//   node scripts/compress_render_model.mjs data/bridges/<id>/model_render.glb
// Positions are stored as 16-bit integers per mesh (step = mesh size / 65535, about 1 mm on a 70 m deck)
// and the box-projected texture coordinates stay float. Node names, materials and the scene's
// render_source stamp are kept; check_render_models.mjs then verifies the geometry against model.glb.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { meshopt } from '@gltf-transform/functions';
import { MeshoptDecoder, MeshoptEncoder } from 'meshoptimizer';

const [input, output = input] = process.argv.slice(2);
if (!input) {
  console.error('usage: node scripts/compress_render_model.mjs <model_render.glb> [output.glb]');
  process.exit(2);
}
await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });
const doc = await io.read(input);
await doc.transform(meshopt({ encoder: MeshoptEncoder, level: 'medium', quantizePosition: 16, quantizeTexcoord: 14 }));
await io.write(output, doc);
