try {
  require('playwright-core');
  console.log('Playwright is available.');
} catch (error) {
  console.log('Playwright is not available:', error.message);
}