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
    logo: 'var(--font-montserrat), sans-serif',
    body: 'var(--font-inter), sans-serif',
    detail: 'var(--font-roboto), sans-serif',
  },
} as const;

export type Theme = typeof theme;

