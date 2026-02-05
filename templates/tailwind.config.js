// npm install -g tailwindcss
// npm install -g flowbite
const path = require('child_process').execSync('npm -g root').toString().trim() + '/'
const defaultTheme = require(path + 'tailwindcss/defaultTheme')

module.exports = {
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
