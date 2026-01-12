import path from 'path';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import proxyOptions from './proxyOptions';

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [vue(), tailwindcss()],
	server: {
		port: 8080,
		strictPort: true,
		proxy: proxyOptions
	},
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src')
		}
	},
	build: {
		outDir: '../supplier_portal/public/supplier-portal',
		emptyOutDir: true,
		sourcemap: true,
		target: 'es2015',
	},
});
