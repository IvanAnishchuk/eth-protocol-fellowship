# Vendored brand fonts (social card)

These three static faces are used only by the social-card generator
(`tools/social_card.py`) to rasterize `docs/assets/social-card-bg.svg`. The site
itself loads Archivo and Hanken Grotesk from Google Fonts at runtime; these files
exist so the build can render the card without a network fetch (keeping CI
egress-free) and without depending on system-installed fonts.

## Files

| File | Family name (used in the SVG) | Weight |
| --- | --- | --- |
| `Archivo-ExtraBold.ttf` | `Archivo ExtraBold` | 800 |
| `HankenGrotesk-Medium.ttf` | `Hanken Grotesk Medium` | 500 |
| `HankenGrotesk-SemiBold.ttf` | `Hanken Grotesk SemiBold` | 600 |

The card SVG references each face by its full family name with normal weight.
cairosvg renders through cairo's toy font API, which only distinguishes
normal/bold, so a unique family name per weight is the reliable way to select the
right face.

## Provenance

Source: `github.com/google/fonts`, commit
`5457e22d106dd3b693c4f9eca2551a615341ea86`.

- Archivo: `ofl/archivo/Archivo[wdth,wght].ttf` (variable), instanced to
  `wght=800, wdth=100`.
- Hanken Grotesk: `ofl/hankengrotesk/HankenGrotesk[wght].ttf` (variable),
  instanced to `wght=500` and `wght=600`.

Each instance was then subset to printable ASCII (`U+0020`–`U+007E`) with
fontTools, which is why the files are a few tens of KB. To regenerate, re-run the
instancing/subsetting against the same source commit.

## License

Both families are licensed under the SIL Open Font License 1.1, included here as
`OFL-Archivo.txt` and `OFL-HankenGrotesk.txt`. The OFL permits bundling and
redistribution of the font files, including modified (instanced/subset) copies.
