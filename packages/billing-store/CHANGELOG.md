# Changelog

## 0.9.4

Builds again on current AILANG. 0.9.3 was published against `sunholo/firestore` 0.7.2, whose
`client.ail` fails AILANG's strict check (`STRICT_FALLBACK_001`), so all six repositories failed to
compile. This release depends on firestore 0.7.3. The billing code is unchanged.
