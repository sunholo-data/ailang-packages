# Changelog

## 0.1.1

Fix: `interaction.ail` imported `get` from `std/json` while exporting its own
`get(project, id)`. Inside the module the import silently won. AILANG v0.51.2
makes an explicitly imported name that is also defined at module level a
compile error (MOD015, ailang#1467), which broke every consumer of this
package. The JSON import is now `get as jsonGet`. No API change: `get`,
`start`, `list`, `cancel` and `delete` keep their names and signatures.

