# Conversor de Arquivos (`convert.py`)

O script de interface de linha de comando (`cli`) converte tabelas e arquivos delimitados de texto entre os formatos suportados nativamente pelo sistema, como `CSV` e planilhas `XLSX`.

## Papel no Sistema

Este utilitário não participa diretamente na criação das análises lexicais, mas serve como ferramenta transacional essencial de suporte. Com ele, o usuário ou analista consegue facilmente transformar arquivos tabulares estritos no terminal sem necessitar abrir o código do ambiente Jupyter ou instalar aplicações de produtividade local, viabilizando rotinas de mineração ou compatibilização com ferramentas legadas de forma Headless.

## Comportamento

O script recebe duas diretivas estritas de arquivos de apontamento (`input_path` e `output_path`). Ele processa e bloqueia sobrescritas em ambientes onde os arquivos de saída já existam (segurança anti-perda de dados) e orquestra a chamada de fábricas subjacentes para delegar a computação com o pandas e liberar o log de finalização através do observador da infraestrutura base.

## Exemplo de Uso

Execução direta via módulo Python na raiz do repositório:

```bash
python -m script.convert -i dados.csv -if csv -o formato_novo.xlsx -of xlsx
```

## Parâmetros e Flags Suportados

| Flag Curta | Flag Estendida    |  Tipo Suportado   | Obrigatório | Propósito / Descrição                                                         |
| :--------: | :---------------- | :---------------: | :---------: | :---------------------------------------------------------------------------- |
|    `-i`    | `--input-path`    |     File Path     |   **Sim**   | Caminho absoluto/relativo do arquivo lido para processamento.                 |
|    `-o`    | `--output-path`   |     FIle Path     |   **Sim**   | Destino em que o dado será injetado e finalizado pelo builder.                |
|   `-if`    | `--input-format`  | Enum `FileFormat` |   **Sim**   | Tipagem rigorosa (`csv`, `xlsx`) guiando a inferência leitora da factory.     |
|   `-of`    | `--output-format` | Enum `FileFormat` |   **Sim**   | Qualidade do dado base de esgotamento (`csv`, `xlsx`) no formato persistente. |
