import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    plugins: [
        tailwindcss(),
    ],

    build: {
        manifest: true,
        outDir: 'static/build',
        rollupOptions: {
            input: {
                app: './static/src/js/app.js',
                style: './static/src/css/input.css',
                input: './static/src/css/input.css',
            },
        },
    },
})