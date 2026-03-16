# myCaire Ecosystem Diagrams

Mermaid-källor och exportinstruktioner för deck-ready visuals.

## Filer

| Diagram           | Källa                           | SVG (site)                      | PNG (produktblad) |
| ----------------- | ------------------------------- | ------------------------------- | ----------------- |
| Data Layer        | `mycaire-data-layer.mmd`        | `apps/website/public/diagrams/` | `docs/assets/`    |
| Product Ecosystem | `mycaire-product-ecosystem.mmd` | `apps/website/public/diagrams/` | `docs/assets/`    |
| myCaire Flywheel  | `mycaire-flywheel.mmd`          | `apps/website/public/diagrams/` | `docs/assets/`    |

## Export (reproducible)

Kräver `npx` och `@mermaid-js/mermaid-cli`:

```bash
# Från repo-root
cd /path/to/beta-appcaire

# SVG (transparent bakgrund för ljus/mörk)
npx --yes @mermaid-js/mermaid-cli -i docs/docs_2.0/05-prd/diagrams/mycaire-data-layer.mmd -o apps/website/public/diagrams/mycaire-data-layer.svg -b transparent
npx --yes @mermaid-js/mermaid-cli -i docs/docs_2.0/05-prd/diagrams/mycaire-product-ecosystem.mmd -o apps/website/public/diagrams/mycaire-product-ecosystem.svg -b transparent
npx --yes @mermaid-js/mermaid-cli -i docs/docs_2.0/05-prd/diagrams/mycaire-flywheel.mmd -o apps/website/public/diagrams/mycaire-flywheel.svg -b transparent

# PNG (2x retina, transparent)
npx --yes @mermaid-js/mermaid-cli -i docs/docs_2.0/05-prd/diagrams/mycaire-data-layer.mmd -o docs/assets/mycaire-data-layer.png -s 2 -b transparent
npx --yes @mermaid-js/mermaid-cli -i docs/docs_2.0/05-prd/diagrams/mycaire-product-ecosystem.mmd -o docs/assets/mycaire-product-ecosystem.png -s 2 -b transparent
npx --yes @mermaid-js/mermaid-cli -i docs/docs_2.0/05-prd/diagrams/mycaire-flywheel.mmd -o docs/assets/mycaire-flywheel.png -s 2 -b transparent
```

## Verifiering

- Inga hårdkodade färger i `.mmd`-filerna (läsbar i ljus/mörk bakgrund)
- SVG: optimerad för webb
- PNG: 2x scale för retina
