import { defineConfig } from "eslint-define-config";

export default defineConfig({
  files: ["/**/*.{js,jsx,ts,tsx}"], // Explicitly target the 'src' directory
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
  },
  rules: {
    "no-console": "warn",
    "no-unused-vars": "warn",
    "no-undef": "error", // Catch undefined variables
    "@typescript-eslint/no-explicit-any": "warn",
  },
  ignores: ["dist", ".eslintrc.cjs"],
});
