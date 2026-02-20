// npm install -g tailwindcss
// npm install -g flowbite
const path = require('child_process').execSync('npm -g root').toString().trim() + '/'
const defaultTheme = require(path + 'tailwindcss/defaultTheme')

module.exports = {
  darkMode: 'class',
  safelist: [
    {
      pattern: /^(?:dark:)?(?:hover:|focus:)?(?:bg|text|border|ring)-slate-(?:50|100|200|300|400|500|600|700|800|900)(?:\/(?:25|30|50))?$/,
    },
  ],
  content: [
    'templates/**/*.{html,js}',
    'views/**/*.{html,js}',
    path + 'flowbite/**/*.js'
  ],
  plugins: [
    // require(path + 'flowbite/plugin'),
    // require(path + 'daisyui'),
    require(path + '@tailwindcss/typography'),
    require(path + '@tailwindcss/forms'),
    require(path + '@tailwindcss/aspect-ratio'),
    require(path + '@tailwindcss/container-queries'),
  ],
  theme: {
    extend: {
      // fontFamily: {
      //   sans: ['Roboto', ...defaultTheme.fontFamily.sans],
      // },
      // colors: {
      // },
    },
  },
}
