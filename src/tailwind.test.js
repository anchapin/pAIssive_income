import assert from 'assert';
import fs from 'fs';
import path from 'path';

describe('Tailwind CSS Integration', function () {
  it('should have a tailwind.config.js file', function () {
    const configExists = fs.existsSync(path.join(process.cwd(), 'tailwind.config.js'));
    assert.strictEqual(configExists, true, 'tailwind.config.js file should exist');
  });

  it('should have a tailwind.css source file', function () {
    const sourceExists = fs.existsSync(path.join(process.cwd(), 'ui', 'static', 'css', 'tailwind.css'));
    assert.strictEqual(sourceExists, true, 'ui/static/css/tailwind.css file should exist');
  });

  it('should generate tailwind.output.css file when built', function () {
    // This test will pass if the build script runs before tests
    const outputPath = path.join(process.cwd(), 'ui', 'static', 'css', 'tailwind.output.css');
    const outputExists = fs.existsSync(outputPath);
    
    if (!outputExists) {
      console.warn('Warning: tailwind.output.css does not exist. Make sure to run the build script before tests.');
    }
    
    assert.strictEqual(outputExists, true, 'ui/static/css/tailwind.output.css should be generated');
  });

  it('should have tailwind directives in the source file', function () {
    const sourcePath = path.join(process.cwd(), 'ui', 'static', 'css', 'tailwind.css');
    const sourceContent = fs.readFileSync(sourcePath, 'utf8');
    
    assert.ok(
      sourceContent.includes('@tailwind base') && 
      sourceContent.includes('@tailwind components') && 
      sourceContent.includes('@tailwind utilities'),
      'tailwind.css should include the required Tailwind directives'
    );
  });
});
