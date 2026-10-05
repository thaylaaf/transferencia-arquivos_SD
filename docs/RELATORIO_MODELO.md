# Relatório — Avaliação de desempenho na transferência de arquivo

## 1. Objetivo

Avaliar o desempenho da transferência de arquivos utilizando as arquiteturas cliente-servidor e P2P, variando o tamanho do arquivo e a quantidade de nós clientes.

## 2. Arquiteturas

### 2.1 Cliente-servidor — 1 cliente por vez
Descrever a implementação e o fluxo da transferência.

### 2.2 Cliente-servidor — todos os clientes
Descrever a utilização de threads e o atendimento simultâneo.

### 2.3 Cliente-servidor — máximo N clientes
Informar o valor de N utilizado e explicar o pool de threads.

### 2.4 P2P
Descrever o funcionamento do tracker e dos peers, destacando que os peers podem fornecer blocos que já receberam.

## 3. Metodologia

- Tamanhos de arquivo: 5 MB, 50 MB e 500 MB.
- Quantidades de clientes: [preencher com as quantidades efetivamente utilizadas].
- Número de repetições por configuração: [preencher].
- Valor N: [preencher].
- Ambiente de execução: [preencher].
- Método de medição: tempo desde o início da transferência até o recebimento do arquivo completo pelo cliente/peer.

## 4. Resultados

Inserir tabelas com mínimo, média e máximo para cada arquitetura, tamanho e quantidade de clientes.

## 5. Análise

Descrever objetivamente os comportamentos observados nos dados, sem inventar causas que não possam ser justificadas pelo experimento.

## 6. Conclusão

Retomar o que foi implementado, as variáveis experimentais e os principais resultados observados.
