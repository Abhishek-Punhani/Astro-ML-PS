import { defineConfig } from "eslint-define-config";

export default defineConfig({
  files: ["**/*.{js,jsx,ts,tsx}"], // Explicitly target all JavaScript and TypeScript files
  languageOptions: {
    ecmaVersion: 2020,
    sourceType: "module",
  },
  env: {
    browser: true,
    node: true,
    es6: true,
  },
  plugins: {
    "@typescript-eslint": {},
    "react-refresh": "plugin:react-refresh/recommended",
    react: {}, // Add the React plugin
  },
  rules: {
    "no-console": "warn",
    "no-unused-vars": "warn",
    "no-undef": "error", // Catch undefined variables
    "@typescript-eslint/no-explicit-any": "warn",
  },
  settings: {
    react: {
      version: "detect", // Automatically detect the React version
    },
  },
  ignores: ["dist", ".eslintrc.cjs"],
});
