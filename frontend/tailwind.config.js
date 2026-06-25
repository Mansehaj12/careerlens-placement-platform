/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "var(--color-bg)",
        darkCard: "var(--color-card)",
        glassBorder: "var(--color-border)",
        glassHoverBorder: "var(--color-border-hover)",
        textMain: "var(--color-text-main)",
        textMuted: "var(--color-text-muted)",
        brandBlue: "var(--color-primary)",
        brandCyan: "var(--color-accent)",
        brandPurple: "var(--color-purple)",
        brandSuccess: "var(--color-success)",
        brandWarning: "var(--color-warning)",
        brandDanger: "var(--color-danger)"
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glowBlue: "var(--shadow-glow)",
        glowCyan: "var(--shadow-glow)",
        glowPurple: "var(--shadow-glow)",
      }
    },
  },
  plugins: [],
}
