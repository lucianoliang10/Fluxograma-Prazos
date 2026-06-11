# ANRESF · Fluxograma e Macro de Casos

Site estático em HTML para acompanhar o fluxograma e a visão macro dos casos ANRESF.

## Publicação no Vercel

1. Suba este repositório no GitHub.
2. No Vercel, escolha **Add New Project** e importe o repositório.
3. Mantenha as configurações padrão de projeto estático. O arquivo principal é `index.html`.
4. Publique.

## Atualização da base

Quando houver alteração na planilha base, envie os dados colados em formato tabular/TSV com o cabeçalho `Caso`, `ID`, `Etapa`, `Origem`, `Clube`, `Série`, `Ordem Etapa`, `Objeto`, `Data de envio`, `Prazo final`, `Data de entrega`, `Observação`, `Status Etapa`, `Status Caso`, `Sanção` e `Doc`. A atualização principal fica no array `DATA` dentro de `index.html`.
