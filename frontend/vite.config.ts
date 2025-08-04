import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
	plugins: [sveltekit()],
	resolve: {
		alias: {
			$components: resolve('./src/lib/components'),
			$stores: resolve('./src/lib/stores'),
			$services: resolve('./src/lib/services'),
			$types: resolve('./src/lib/types'),
			$lib: resolve('./src/lib')
		}
	},
	server: {
		port: 5173,
		host: true
	},
	preview: {
		port: 4173,
		host: true
	}
});