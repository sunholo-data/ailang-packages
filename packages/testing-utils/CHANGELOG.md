# Changelog

## 0.1.2

Builds again on current AILANG. 0.1.1 joined strings with `++`, which AILANG only allows on lists
(`` `++` is for lists only ``), so the package failed to compile on every release since that check
landed. The assertions now build their messages with string interpolation. In `assertEqual` and
`assertContains`, string values now appear without the quotes `show` added.
