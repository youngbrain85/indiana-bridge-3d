const path=require('node:path');
const esbuild=require('esbuild');
esbuild.buildSync({entryPoints:[path.join(__dirname,'viewer.js')],outfile:path.join(__dirname,'web/viewer.bundle.js'),bundle:true,minify:true,format:'iife',legalComments:'eof'});
esbuild.buildSync({entryPoints:[path.join(__dirname,'inspect/app.js')],outfile:path.join(__dirname,'web/inspect.bundle.js'),bundle:true,minify:true,format:'iife',target:['es2022'],legalComments:'eof'});
