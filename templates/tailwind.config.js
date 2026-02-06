const path = require('path');

module.exports = {
  content: [
    'templates/**/*.{html,js}',
    'views/**/*.{html,js}',
    path.dirname(require.resolve('flowbite/package.json')) + '**/*.js'
  ],
  plugins: [
    // require(path + 'flowbite/plugin'),
    // require(path + 'daisyui'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/container-queries'),
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
