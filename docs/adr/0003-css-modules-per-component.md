# CSS Modules, one file per component

A single `index.css` accumulating every page's styles under global class
names doesn't scale past a couple of pages — names collide, and nothing ties
a style block to the component that uses it, so removing a component means
hunting for its leftover rules.

So each component owns a `Component.module.css` next to `Component.tsx`.
Vite's CSS Modules support (already in with the Vite scaffold, no extra
dependency) scopes every class name to that file, and the import makes the
dependency explicit: `import styles from './LoginPage.module.css'`. `index.css`
stays for the handful of true globals — `body`, font, resets.
