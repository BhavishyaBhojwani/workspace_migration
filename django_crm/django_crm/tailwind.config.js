/** @type {import('tailwindcss').Config} */
export default {
    content: [
        './templates/**/*.html',
        './static/js/**/*.js',
    ],
    darkMode: 'media',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Nunito', 'sans-serif'],
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
    ],
};
