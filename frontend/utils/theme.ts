export const theme = {
  colors: {
    white: '#FFF',
    grayLight: '#AAA',
    grayMedium: '#666',
    grayDark: '#333',
    primary: '#64a7fa',
    secondary: '#ff7878',
  },
  fonts: {
    logo: '"Asimovian", sans-serif',
    body: '"Poiret One", sans-serif',
    detail: '"Roboto", sans-serif',
  },
} as const;

export type Theme = typeof theme;

