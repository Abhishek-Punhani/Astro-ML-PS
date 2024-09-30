import { defineConfig } from "eslint-define-config";

export default defineConfig([
  {
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: "module",
    },
    plugins: {
      "react-refresh": "plugin:react-refresh/recommended",
    },
    rules: {
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
      // Add any additional rules you want to customize here
      "no-console": "warn",
      "no-unused-vars": "warn",
      "@typescript-eslint/no-explicit-any": "warn",
    },
    ignores: ["dist", ".eslintrc.cjs"],
  },
]);
